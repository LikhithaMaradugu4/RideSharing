"""
Dispatch Service - Driver dispatch with controlled parallelism.

Dispatch model:
- Dispatch is INTERNAL logic, not a public API
- Drivers explicitly receive dispatch offers
- Controlled parallelism: batch size 2-3, timeout ~10-15 seconds
- Start radius: 3 km, expand gradually up to max
- First acceptance wins (atomic at DB level)

Wave logic:
- Wave 1: dispatch_trip() - initial radius
- Wave 2+: advance_dispatch_wave() - expanding radius
- Trip CANCELLED only when all waves exhausted with no driver
"""

from datetime import datetime, timezone, timedelta
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from fastapi import HTTPException

from app.models.trips import Trip
from app.models.dispatch import DispatchAttempt
from app.models.fleet import DriverProfile
from app.models.operations import DriverShift, DriverLocation
from app.models.identity import AppUser
from app.utils.haversine import haversine
from app.services.driver_location_service import DriverLocationService


# Dispatch configuration
BATCH_SIZE = 3
MAX_WAVES = 3
INITIAL_RADIUS_KM = 3.0
RADIUS_INCREMENT_KM = 2.0
MAX_RADIUS_KM = 10.0
OFFER_TIMEOUT_SECONDS = 15


def calculate_radius_for_wave(wave: int) -> float:
    """
    Calculate search radius for a given wave.
    
    Formula: radius_km = INITIAL_RADIUS_KM + (wave - 1) * RADIUS_INCREMENT_KM
    
    Args:
        wave: Wave number (1-indexed)
    
    Returns:
        Radius in kilometers
    """
    return INITIAL_RADIUS_KM + (wave - 1) * RADIUS_INCREMENT_KM


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
        
        Strategy:
        1. Use Redis GEORADIUS to find nearby driver IDs + distance
        2. Filter those driver IDs using DB checks:
           - APPROVED driver profile
           - Active shift (ended_at IS NULL)
           - Shift status is ONLINE (not BUSY)
           - Vehicle category matches (allowed_vehicle_categories)
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
        
        # Step 1: Get nearby drivers from Redis GEO
        nearby_drivers = DriverLocationService.find_nearby_drivers(
            longitude=pickup_lng,
            latitude=pickup_lat,
            radius_km=radius_km
        )
        
        if not nearby_drivers:
            # Fallback: Use DB-only approach if Redis has no data
            return DispatchService._find_eligible_drivers_db_fallback(
                db=db,
                pickup_lat=pickup_lat,
                pickup_lng=pickup_lng,
                vehicle_category=vehicle_category,
                radius_km=radius_km,
                exclude_driver_ids=exclude_driver_ids
            )
        
        # Extract driver IDs and distances from Redis results
        nearby_driver_ids = [d[0] for d in nearby_drivers]
        distance_map = {d[0]: d[1] for d in nearby_drivers}
        
        # Remove excluded drivers
        if exclude_driver_ids:
            nearby_driver_ids = [d for d in nearby_driver_ids if d not in exclude_driver_ids]
        
        if not nearby_driver_ids:
            return []
        
        # Step 2: Filter by DB criteria (shift ONLINE, profile APPROVED, vehicle category)
        eligible_drivers = (
            db.query(
                DriverProfile.driver_id,
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
            .filter(
                DriverProfile.driver_id.in_(nearby_driver_ids),
                DriverProfile.approval_status == "APPROVED"
            )
            .all()
        )
        
        # Step 3: Filter by vehicle category and build result
        eligible = []
        for driver_id, allowed_categories in eligible_drivers:
            # Check vehicle category
            if allowed_categories and vehicle_category not in allowed_categories:
                continue
            
            # Get distance from Redis results
            distance = distance_map.get(driver_id, float('inf'))
            eligible.append((driver_id, distance))
        
        # Sort by distance (nearest first)
        eligible.sort(key=lambda x: x[1])
        
        return eligible

    @staticmethod
    def _find_eligible_drivers_db_fallback(
        db: Session,
        pickup_lat: float,
        pickup_lng: float,
        vehicle_category: str,
        radius_km: float,
        exclude_driver_ids: List[int] = None
    ) -> List[Tuple[int, float]]:
        """
        Fallback method using DB-only approach (when Redis has no data).
        
        Uses Postgres driver_location table and haversine calculation.
        """
        exclude_driver_ids = exclude_driver_ids or []
        
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
        
        if exclude_driver_ids:
            query = query.filter(~DriverProfile.driver_id.in_(exclude_driver_ids))
        
        drivers = query.all()
        
        eligible = []
        for driver_id, lat, lng, allowed_categories in drivers:
            if allowed_categories and vehicle_category not in allowed_categories:
                continue
            
            distance = haversine(pickup_lat, pickup_lng, float(lat), float(lng))
            
            if distance <= radius_km:
                eligible.append((driver_id, distance))
        
        eligible.sort(key=lambda x: x[1])
        
        return eligible

    @staticmethod
    def get_attempted_driver_ids(db: Session, trip_id: int) -> List[int]:
        """
        Get list of driver IDs already attempted for a trip.
        
        Args:
            db: Database session
            trip_id: Trip ID
        
        Returns:
            List of driver IDs
        """
        attempts = (
            db.query(DispatchAttempt.driver_id)
            .filter(DispatchAttempt.trip_id == trip_id)
            .all()
        )
        return [a[0] for a in attempts]

    @staticmethod
    def get_current_wave(db: Session, trip_id: int) -> int:
        """
        Get the current (highest) wave number for a trip.
        
        Args:
            db: Database session
            trip_id: Trip ID
        
        Returns:
            Current wave number (0 if no attempts exist)
        """
        result = (
            db.query(func.max(DispatchAttempt.wave_number))
            .filter(DispatchAttempt.trip_id == trip_id)
            .scalar()
        )
        
        return result or 0

    @staticmethod
    def count_pending_attempts(db: Session, trip_id: int) -> int:
        """
        Count pending dispatch attempts for a trip.
        
        Args:
            db: Database session
            trip_id: Trip ID
        
        Returns:
            Number of pending attempts
        """
        return (
            db.query(DispatchAttempt)
            .filter(
                DispatchAttempt.trip_id == trip_id,
                DispatchAttempt.response.like("PENDING%")
            )
            .count()
        )

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
                wave_number=wave,  # Explicitly set wave number
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
        Dispatch a trip to available drivers (Wave 1 only).
        
        This initiates the FIRST wave of dispatch only.
        NEVER marks trip as NO_DRIVER_AVAILABLE or CANCELLED.
        
        Args:
            db: Database session
            trip: Trip to dispatch
            vehicle_category: Vehicle category filter
            created_by: User ID initiating dispatch
        
        Returns:
            True if at least one dispatch_attempt was created
            False ONLY if zero eligible drivers exist even at MAX_RADIUS
        """
        # Only dispatch if trip is REQUESTED
        if trip.status != "REQUESTED":
            return False
        
        # Update trip status to DISPATCHING
        trip.status = "DISPATCHING"
        db.flush()
        
        # Wave 1 radius
        radius_km = calculate_radius_for_wave(1)
        
        # Find eligible drivers for wave 1
        eligible = DispatchService.find_eligible_drivers(
            db=db,
            pickup_lat=float(trip.pickup_lat),
            pickup_lng=float(trip.pickup_lng),
            city_id=trip.city_id,
            vehicle_category=vehicle_category,
            radius_km=radius_km
        )
        
        if not eligible:
            # No drivers in initial radius - this is NOT a failure
            # Trip stays in DISPATCHING, advance_dispatch_wave will handle expansion
            db.commit()
            return False
        
        # Take first batch
        batch_driver_ids = [d[0] for d in eligible[:BATCH_SIZE]]
        
        # Create dispatch attempts for wave 1
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
    def advance_dispatch_wave(
        db: Session,
        trip_id: int,
        vehicle_category: str,
        created_by: int
    ) -> dict:
        """
        Advance to the next dispatch wave.
        
        This method handles wave 2, wave 3, etc.
        
        Logic:
        1. Count existing waves for the trip
        2. If waves < MAX_WAVES:
           - Increase radius
           - Exclude already-attempted drivers
           - Create next wave dispatch_attempts
        3. If waves == MAX_WAVES AND no pending attempts AND no driver assigned:
           - Mark trip as CANCELLED
           - Set cancel_reason = "NO_DRIVER_AVAILABLE"
        
        Args:
            db: Database session
            trip_id: Trip ID
            vehicle_category: Vehicle category filter
            created_by: User ID initiating advance
        
        Returns:
            Dict with status info: {
                "action": "WAVE_CREATED" | "DISPATCH_EXHAUSTED" | "ALREADY_ASSIGNED" | "NO_ACTION",
                "wave": int (if created),
                "attempts_created": int (if created),
                "trip_status": str
            }
        """
        # Get trip
        trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()
        
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found")
        
        # If trip already has a driver, no action needed
        if trip.driver_id is not None:
            return {
                "action": "ALREADY_ASSIGNED",
                "trip_status": trip.status
            }
        
        # If trip is not in DISPATCHING status, no action
        if trip.status != "DISPATCHING":
            return {
                "action": "NO_ACTION",
                "trip_status": trip.status,
                "reason": f"Trip is in {trip.status} status"
            }
        
        # Get current wave and pending attempts
        current_wave = DispatchService.get_current_wave(db, trip_id)
        pending_count = DispatchService.count_pending_attempts(db, trip_id)
        
        # If there are still pending attempts, don't advance yet
        if pending_count > 0:
            return {
                "action": "NO_ACTION",
                "trip_status": trip.status,
                "reason": f"{pending_count} pending attempts remaining",
                "current_wave": current_wave
            }
        
        # Calculate next wave
        next_wave = current_wave + 1
        
        # Check if we've exhausted all waves
        if next_wave > MAX_WAVES:
            # Dispatch exhausted - mark trip as CANCELLED
            trip.status = "CANCELLED"
            trip.cancelled_at = datetime.now(timezone.utc)
            trip.updated_by = created_by
            # Note: If you have a cancel_reason column, set it here
            # trip.cancel_reason = "NO_DRIVER_AVAILABLE"
            db.commit()
            
            return {
                "action": "DISPATCH_EXHAUSTED",
                "trip_status": "CANCELLED",
                "reason": "All dispatch waves exhausted with no driver"
            }
        
        # Calculate radius for next wave
        radius_km = calculate_radius_for_wave(next_wave)
        
        # Check if radius exceeds max
        if radius_km > MAX_RADIUS_KM:
            # Radius exceeded - mark trip as CANCELLED
            trip.status = "CANCELLED"
            trip.cancelled_at = datetime.now(timezone.utc)
            trip.updated_by = created_by
            db.commit()
            
            return {
                "action": "DISPATCH_EXHAUSTED",
                "trip_status": "CANCELLED",
                "reason": f"Max radius {MAX_RADIUS_KM}km exceeded"
            }
        
        # Get already-attempted driver IDs
        exclude_driver_ids = DispatchService.get_attempted_driver_ids(db, trip_id)
        
        # Find eligible drivers for next wave
        eligible = DispatchService.find_eligible_drivers(
            db=db,
            pickup_lat=float(trip.pickup_lat),
            pickup_lng=float(trip.pickup_lng),
            city_id=trip.city_id,
            vehicle_category=vehicle_category,
            radius_km=radius_km,
            exclude_driver_ids=exclude_driver_ids
        )
        
        if not eligible:
            # No new drivers in this radius
            # Do NOT recurse - one API call advances at most one wave
            # Return status so caller can decide to call again
            return {
                "action": "NO_DRIVERS_IN_RADIUS",
                "wave": next_wave,
                "radius_km": radius_km,
                "attempts_created": 0,
                "trip_status": trip.status,
                "reason": f"No eligible drivers found within {radius_km}km"
            }
        
        # Take batch for this wave
        batch_driver_ids = [d[0] for d in eligible[:BATCH_SIZE]]
        
        # Create dispatch attempts for this wave
        attempts = DispatchService.create_dispatch_attempts(
            db=db,
            trip_id=trip_id,
            driver_ids=batch_driver_ids,
            wave=next_wave,
            created_by=created_by
        )
        
        db.commit()
        
        return {
            "action": "WAVE_CREATED",
            "wave": next_wave,
            "radius_km": radius_km,
            "attempts_created": len(attempts),
            "trip_status": trip.status
        }

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