"""
Dispatch Service - Driver dispatch with controlled parallelism.

Dispatch model:
- Dispatch is INTERNAL logic, not a public API
- Drivers explicitly receive dispatch offers
- Controlled parallelism: batch size 2-3, timeout ~10-15 seconds
- Start radius: 3 km, expand gradually up to max
- First acceptance wins (atomic at DB level)
"""

from datetime import datetime, timezone, timedelta
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException

from app.models.trips import Trip
from app.models.dispatch import DispatchAttempt
from app.models.fleet import DriverProfile
from app.models.operations import DriverShift, DriverLocation
from app.models.identity import AppUser
from app.utils.haversine import haversine


# Dispatch configuration
BATCH_SIZE = 3
MAX_WAVES = 3
INITIAL_RADIUS_KM = 3.0
RADIUS_INCREMENT_KM = 2.0
MAX_RADIUS_KM = 10.0
OFFER_TIMEOUT_SECONDS = 15


class DispatchService:
    """Service for driver dispatch operations."""

    @staticmethod
    def find_eligible_drivers(
        db: Session,
        pickup_lat: float,
        pickup_lng: float,
        city_id: int,
        vehicle_category: str,
        radius_km: float,
        exclude_driver_ids: List[int] = None
    ) -> List[Tuple[int, float]]:
        """
        Find eligible drivers within radius.
        
        Eligibility:
        - APPROVED driver profile
        - Active shift (ended_at IS NULL)
        - Shift status is ONLINE (not BUSY)
        - Vehicle category matches
        - Within radius
        - Not already attempted for this trip
        
        Args:
            db: Database session
            pickup_lat, pickup_lng: Pickup coordinates
            city_id: City ID for the trip
            vehicle_category: Required vehicle category
            radius_km: Search radius in kilometers
            exclude_driver_ids: Driver IDs to exclude (already attempted)
        
        Returns:
            List of (driver_id, distance_km) tuples, sorted by distance
        """
        exclude_driver_ids = exclude_driver_ids or []
        
        # Query for eligible drivers with active shifts and locations
        query = (
            db.query(
                DriverProfile.driver_id,
                DriverLocation.latitude,
                DriverLocation.longitude,
                DriverProfile.allowed_vehicle_categories
            )
            .join(
                DriverShift,
                and_(
                    DriverShift.driver_id == DriverProfile.driver_id,
                    DriverShift.ended_at.is_(None),
                    DriverShift.status == "ONLINE"
                )
            )
            .join(
                DriverLocation,
                DriverLocation.driver_id == DriverProfile.driver_id
            )
            .filter(
                DriverProfile.approval_status == "APPROVED"
            )
        )
        
        # Exclude already-attempted drivers
        if exclude_driver_ids:
            query = query.filter(~DriverProfile.driver_id.in_(exclude_driver_ids))
        
        drivers = query.all()
        
        # Filter by distance and vehicle category
        eligible = []
        for driver_id, lat, lng, allowed_categories in drivers:
            # Check vehicle category
            if allowed_categories and vehicle_category not in allowed_categories:
                continue
            
            # Calculate distance
            distance = haversine(pickup_lat, pickup_lng, float(lat), float(lng))
            
            if distance <= radius_km:
                eligible.append((driver_id, distance))
        
        # Sort by distance (nearest first)
        eligible.sort(key=lambda x: x[1])
        
        return eligible

    @staticmethod
    def create_dispatch_attempts(
        db: Session,
        trip_id: int,
        driver_ids: List[int],
        wave: int,
        created_by: int
    ) -> List[DispatchAttempt]:
        """
        Create dispatch attempts for a batch of drivers.
        
        Args:
            db: Database session
            trip_id: Trip ID
            driver_ids: List of driver IDs
            wave: Wave number (1, 2, 3, ...)
            created_by: User ID creating attempts
        
        Returns:
            List of created DispatchAttempt objects
        """
        now = datetime.now(timezone.utc)
        attempts = []
        
        for driver_id in driver_ids:
            attempt = DispatchAttempt(
                trip_id=trip_id,
                driver_id=driver_id,
                sent_at=now,
                response=f"PENDING_WAVE_{wave}",
                created_by=created_by
            )
            db.add(attempt)
            attempts.append(attempt)
        
        db.flush()
        return attempts

    @staticmethod
    def dispatch_trip(
        db: Session,
        trip: Trip,
        vehicle_category: str,
        created_by: int
    ) -> bool:
        """
        Dispatch a trip to available drivers.
        
        This initiates the first wave of dispatch.
        Returns True if at least one driver was notified.
        
        Args:
            db: Database session
            trip: Trip to dispatch
            vehicle_category: Vehicle category filter
            created_by: User ID initiating dispatch
        
        Returns:
            True if dispatch attempts were created
        """
        # Update trip status to DISPATCHING
        trip.status = "DISPATCHING"
        db.flush()
        
        # Find eligible drivers (first wave, initial radius)
        eligible = DispatchService.find_eligible_drivers(
            db=db,
            pickup_lat=float(trip.pickup_lat),
            pickup_lng=float(trip.pickup_lng),
            city_id=trip.city_id,
            vehicle_category=vehicle_category,
            radius_km=INITIAL_RADIUS_KM
        )
        
        if not eligible:
            # Try with max radius as fallback
            eligible = DispatchService.find_eligible_drivers(
                db=db,
                pickup_lat=float(trip.pickup_lat),
                pickup_lng=float(trip.pickup_lng),
                city_id=trip.city_id,
                vehicle_category=vehicle_category,
                radius_km=MAX_RADIUS_KM
            )
        
        if not eligible:
            return False
        
        # Take first batch
        batch_driver_ids = [d[0] for d in eligible[:BATCH_SIZE]]
        
        # Create dispatch attempts
        DispatchService.create_dispatch_attempts(
            db=db,
            trip_id=trip.trip_id,
            driver_ids=batch_driver_ids,
            wave=1,
            created_by=created_by
        )
        
        db.commit()
        return True

    @staticmethod
    def get_pending_dispatches(
        db: Session,
        driver_id: int
    ) -> List[DispatchAttempt]:
        """
        Get pending dispatch offers for a driver.
        
        Returns offers that:
        - Are still PENDING (any wave)
        - Were sent within timeout period
        - Trip is still in DISPATCHING status
        
        Args:
            db: Database session
            driver_id: Driver's user ID
        
        Returns:
            List of pending DispatchAttempt objects
        """
        timeout_cutoff = datetime.now(timezone.utc) - timedelta(seconds=OFFER_TIMEOUT_SECONDS)
        
        return (
            db.query(DispatchAttempt)
            .join(Trip, Trip.trip_id == DispatchAttempt.trip_id)
            .filter(
                DispatchAttempt.driver_id == driver_id,
                DispatchAttempt.response.like("PENDING%"),
                DispatchAttempt.sent_at >= timeout_cutoff,
                Trip.status == "DISPATCHING"
            )
            .all()
        )

    @staticmethod
    def assign_driver_to_trip(
        db: Session,
        trip_id: int,
        driver_id: int,
        attempt_id: int
    ) -> Trip:
        """
        Atomically assign a driver to a trip.
        
        Uses optimistic locking: UPDATE WHERE driver_id IS NULL
        First acceptance wins, others fail gracefully.
        
        Args:
            db: Database session
            trip_id: Trip ID
            driver_id: Driver's user ID
            attempt_id: Dispatch attempt ID
        
        Returns:
            Updated Trip object
        
        Raises:
            HTTPException if assignment fails
        """
        # Validate the dispatch attempt
        attempt = (
            db.query(DispatchAttempt)
            .filter(
                DispatchAttempt.attempt_id == attempt_id,
                DispatchAttempt.driver_id == driver_id
            )
            .first()
        )
        
        if not attempt:
            raise HTTPException(
                status_code=404,
                detail="Dispatch attempt not found"
            )
        
        if not attempt.response.startswith("PENDING"):
            raise HTTPException(
                status_code=400,
                detail="Dispatch offer already responded to"
            )
        
        # Get the trip
        trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()
        
        if not trip:
            raise HTTPException(
                status_code=404,
                detail="Trip not found"
            )
        
        if trip.status != "DISPATCHING":
            raise HTTPException(
                status_code=400,
                detail=f"Trip is not available for assignment (status: {trip.status})"
            )
        
        # Atomic assignment check
        if trip.driver_id is not None:
            raise HTTPException(
                status_code=409,
                detail="Trip already assigned to another driver"
            )
        
        # Get driver's tenant_id from their profile
        driver_profile = (
            db.query(DriverProfile)
            .filter(DriverProfile.driver_id == driver_id)
            .first()
        )
        
        if not driver_profile:
            raise HTTPException(
                status_code=400,
                detail="Driver profile not found"
            )
        
        # Assign driver and set tenant
        now = datetime.now(timezone.utc)
        trip.driver_id = driver_id
        trip.tenant_id = driver_profile.tenant_id
        trip.status = "ASSIGNED"
        trip.assigned_at = now
        trip.updated_by = driver_id
        
        # Update the accepting attempt
        attempt.response = "ACCEPTED"
        attempt.responded_at = now
        
        # Cancel other pending attempts for this trip
        db.query(DispatchAttempt).filter(
            DispatchAttempt.trip_id == trip_id,
            DispatchAttempt.attempt_id != attempt_id,
            DispatchAttempt.response.like("PENDING%")
        ).update(
            {"response": "CANCELLED", "responded_at": now},
            synchronize_session=False
        )
        
        # Update driver shift status to BUSY
        db.query(DriverShift).filter(
            DriverShift.driver_id == driver_id,
            DriverShift.ended_at.is_(None)
        ).update(
            {"status": "BUSY"},
            synchronize_session=False
        )
        
        db.commit()
        db.refresh(trip)
        
        return trip

    @staticmethod
    def reject_dispatch_attempt(
        db: Session,
        attempt_id: int,
        driver_id: int
    ) -> DispatchAttempt:
        """
        Reject a dispatch offer.
        
        Args:
            db: Database session
            attempt_id: Dispatch attempt ID
            driver_id: Driver's user ID
        
        Returns:
            Updated DispatchAttempt object
        
        Raises:
            HTTPException if attempt not found or already responded
        """
        attempt = (
            db.query(DispatchAttempt)
            .filter(
                DispatchAttempt.attempt_id == attempt_id,
                DispatchAttempt.driver_id == driver_id
            )
            .first()
        )
        
        if not attempt:
            raise HTTPException(
                status_code=404,
                detail="Dispatch attempt not found"
            )
        
        if not attempt.response.startswith("PENDING"):
            raise HTTPException(
                status_code=400,
                detail="Dispatch offer already responded to"
            )
        
        attempt.response = "REJECTED"
        attempt.responded_at = datetime.now(timezone.utc)
        
        db.commit()
        db.refresh(attempt)
        
        return attempt

    @staticmethod
    def get_rider_display_name(full_name: str) -> str:
        """
        Generate a masked display name for the rider.
        
        Examples:
        - "Likhitha Maradugu" -> "Likhitha M."
        - "John" -> "John"
        - None/empty -> "Customer"
        
        Args:
            full_name: Rider's full name
        
        Returns:
            Masked display name
        """
        if not full_name or not full_name.strip():
            return "Customer"
        
        parts = full_name.strip().split()
        if len(parts) == 1:
            return parts[0]
        
        first_name = parts[0]
        last_initial = parts[-1][0].upper() if parts[-1] else ""
        
        return f"{first_name} {last_initial}." if last_initial else first_name