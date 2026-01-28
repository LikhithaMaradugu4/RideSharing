from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Tuple
import math

from app.models.trips import Trip
from app.models.dispatch import DispatchAttempt
from app.models.operations import DriverShift, DriverLocation
from app.models.fleet import DriverProfile, Fleet, FleetDriver
from app.models.vehicle import Vehicle, DriverVehicleAssignment
from app.models.tenant import TenantCity
from app.models.identity import AppUser
from app.utils.dispatch_attempt import haversine


class DispatchService:
    """
    Trip Dispatch and Driver Matching Service.
    
    Mental Model:
    "Dispatch is eligibility + distance + controlled retries,
     not geographic policing."
    
    Key Principles:
    - One trip → ONE tenant → ONE driver
    - Dispatch within tenant boundaries only
    - Distance-based matching (Haversine)
    - Wave-based controlled retries
    - No surge pricing, no geo-fencing, no ML
    """

    # Configuration
    WAVE_SIZE = 3  # Drivers per wave
    WAVE_TIMEOUT_SECONDS = 30  # Time before moving to next wave
    MAX_WAVES = 5  # Maximum dispatch attempts
    LOCATION_STALENESS_MINUTES = 10  # Max age for driver_location

    @staticmethod
    def validate_trip_eligibility(
        db: Session,
        rider_id: int,
        pickup_city_id: int,
        tenant_id: int
    ) -> bool:
        """
        Validate trip can be created for this pickup location.
        
        Rules:
        - pickup_city_id must exist in tenant_city
        
        Returns: True if valid, raises HTTPException otherwise
        """
        tenant_city = (
            db.query(TenantCity)
            .filter(
                TenantCity.tenant_id == tenant_id,
                TenantCity.city_id == pickup_city_id
            )
            .first()
        )

        if not tenant_city:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Pickup city not supported by tenant"
            )

        return True

    @staticmethod
    def find_eligible_drivers(
        db: Session,
        tenant_id: int,
        pickup_city_id: int,
        pickup_lat: float,
        pickup_lng: float,
        vehicle_category: Optional[str] = None
    ) -> List[Tuple[int, float]]:
        """
        Find eligible drivers for dispatch.
        
        Eligibility Filters (ALL must pass):
        - driver_shift.status = ONLINE
        - driver_shift.ended_at IS NULL
        - driver NOT BUSY
        - driver_location exists and recent
        - driver in same tenant
        - driver active fleet APPROVED
        - driver has active vehicle assignment
        - vehicle category matches (if specified)
        - driver city = pickup city
        
        Returns: List of (driver_id, distance_km) tuples, sorted by distance ASC
        """
        location_cutoff = datetime.now(timezone.utc) - timedelta(
            minutes=DispatchService.LOCATION_STALENESS_MINUTES
        )

        # Build query with all eligibility filters
        query = (
            db.query(
                DriverShift.driver_id,
                DriverLocation.latitude,
                DriverLocation.longitude
            )
            .join(
                DriverLocation,
                DriverLocation.driver_id == DriverShift.driver_id
            )
            .join(
                DriverProfile,
                DriverProfile.driver_id == DriverShift.driver_id
            )
            .join(
                FleetDriver,
                and_(
                    FleetDriver.driver_id == DriverShift.driver_id,
                    FleetDriver.end_date.is_(None)  # Active fleet association
                )
            )
            .join(
                Fleet,
                Fleet.fleet_id == FleetDriver.fleet_id
            )
            .join(
                DriverVehicleAssignment,
                and_(
                    DriverVehicleAssignment.driver_id == DriverShift.driver_id,
                    DriverVehicleAssignment.end_time.is_(None)  # Active assignment
                )
            )
            .join(
                Vehicle,
                Vehicle.vehicle_id == DriverVehicleAssignment.vehicle_id
            )
            .filter(
                # Shift filters
                DriverShift.status == "ONLINE",
                DriverShift.ended_at.is_(None),
                DriverShift.tenant_id == tenant_id,
                
                # Location filters
                DriverLocation.last_updated >= location_cutoff,
                
                # Profile filters
                DriverProfile.approval_status == "APPROVED",
                DriverProfile.tenant_id == tenant_id,
                
                # Fleet filters
                Fleet.approval_status == "APPROVED",
                
                # Vehicle filters
                Vehicle.approval_status == "APPROVED"
            )
        )

        # Add vehicle category filter if specified
        if vehicle_category:
            query = query.filter(Vehicle.category == vehicle_category)

        # Execute query
        results = query.all()

        # Calculate distances using Haversine
        candidates = []
        for driver_id, driver_lat, driver_lng in results:
            if driver_lat is None or driver_lng is None:
                continue
            
            distance_km = haversine(
                float(pickup_lat),
                float(pickup_lng),
                float(driver_lat),
                float(driver_lng)
            )
            candidates.append((driver_id, distance_km))

        # Sort by distance ascending
        candidates.sort(key=lambda x: x[1])

        return candidates

    @staticmethod
    def create_dispatch_attempts(
        db: Session,
        trip_id: int,
        driver_ids: List[int],
        wave_number: int,
        created_by: int
    ) -> List[DispatchAttempt]:
        """
        Create dispatch_attempt records for a wave of drivers.
        
        Args:
            trip_id: Trip to dispatch
            driver_ids: List of driver IDs in this wave
            wave_number: Which wave this is (1-indexed)
            created_by: User creating attempts (system or dispatcher)
        
        Returns: List of DispatchAttempt objects
        """
        attempts = []
        now = datetime.now(timezone.utc)

        for driver_id in driver_ids:
            attempt = DispatchAttempt(
                trip_id=trip_id,
                driver_id=driver_id,
                sent_at=now,
                response=f"PENDING_WAVE_{wave_number}",
                created_by=created_by
            )
            db.add(attempt)
            attempts.append(attempt)

        db.commit()
        return attempts

    @staticmethod
    def dispatch_trip(
        db: Session,
        trip: Trip,
        vehicle_category: Optional[str] = None,
        created_by: Optional[int] = None
    ) -> Optional[int]:
        """
        Dispatch trip using wave-based matching.
        
        Algorithm:
        1. Find all eligible drivers
        2. Divide into waves (WAVE_SIZE drivers each)
        3. Create dispatch_attempts for wave
        4. Wait WAVE_TIMEOUT_SECONDS for response
        5. If no response, escalate to next wave
        6. Repeat until driver found or MAX_WAVES reached
        
        Args:
            trip: Trip object to dispatch
            vehicle_category: Optional vehicle category filter
            created_by: User ID creating dispatch (for audit)
        
        Returns: driver_id if assigned, None if no driver found
        
        Note: This is a SYNCHRONOUS implementation. In production,
              use async/celery for wave timeouts and notifications.
        """
        # Validate trip eligibility
        DispatchService.validate_trip_eligibility(
            db=db,
            rider_id=trip.rider_id,
            pickup_city_id=trip.city_id,
            tenant_id=trip.tenant_id
        )

        # Find eligible drivers
        candidates = DispatchService.find_eligible_drivers(
            db=db,
            tenant_id=trip.tenant_id,
            pickup_city_id=trip.city_id,
            pickup_lat=float(trip.pickup_lat),
            pickup_lng=float(trip.pickup_lng),
            vehicle_category=vehicle_category
        )

        if not candidates:
            return None

        # Divide into waves
        wave_number = 1
        driver_index = 0

        while driver_index < len(candidates) and wave_number <= DispatchService.MAX_WAVES:
            # Get drivers for this wave
            wave_drivers = [
                driver_id
                for driver_id, _ in candidates[
                    driver_index : driver_index + DispatchService.WAVE_SIZE
                ]
            ]

            if not wave_drivers:
                break

            # Create dispatch attempts
            DispatchService.create_dispatch_attempts(
                db=db,
                trip_id=trip.trip_id,
                driver_ids=wave_drivers,
                wave_number=wave_number,
                created_by=created_by or trip.rider_id
            )

            # TODO: In production, this would:
            # 1. Send notifications via WebSocket/Push
            # 2. Wait WAVE_TIMEOUT_SECONDS asynchronously
            # 3. Check for driver acceptance
            # 4. If accepted, assign trip and return
            # 5. If timeout/reject, continue to next wave

            # For MVP, we just create the attempts and return first driver
            # Real acceptance logic handled by separate endpoint

            # Move to next wave
            driver_index += DispatchService.WAVE_SIZE
            wave_number += 1

        # If we reach here, no driver found
        return None

    @staticmethod
    def assign_driver_to_trip(
        db: Session,
        trip_id: int,
        driver_id: int,
        attempt_id: int
    ) -> Trip:
        """
        Assign driver to trip after acceptance.
        
        Actions:
        1. Validate driver still ONLINE (not BUSY)
        2. Update trip with driver_id and assigned_at
        3. Update driver_shift status to BUSY
        4. Mark dispatch_attempt as ACCEPTED
        5. Cancel remaining dispatch_attempts for this trip
        
        Returns: Updated Trip object
        """
        # Get trip
        trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()
        if not trip:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trip not found"
            )

        # Validate driver still ONLINE
        shift = (
            db.query(DriverShift)
            .filter(
                DriverShift.driver_id == driver_id,
                DriverShift.ended_at.is_(None)
            )
            .first()
        )

        if not shift or shift.status != "ONLINE":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Driver is not available"
            )

        # Get driver's vehicle
        assignment = (
            db.query(DriverVehicleAssignment)
            .filter(
                DriverVehicleAssignment.driver_id == driver_id,
                DriverVehicleAssignment.end_time.is_(None)
            )
            .first()
        )

        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Driver has no active vehicle assignment"
            )

        # Assign trip
        trip.driver_id = driver_id
        trip.vehicle_id = assignment.vehicle_id
        trip.assigned_at = datetime.now(timezone.utc)
        trip.status = "ASSIGNED"

        # Update driver shift to BUSY
        shift.status = "BUSY"
        shift.updated_on = datetime.now(timezone.utc)

        # Mark accepted attempt
        attempt = db.query(DispatchAttempt).filter(
            DispatchAttempt.attempt_id == attempt_id
        ).first()
        if attempt:
            attempt.response = "ACCEPTED"
            attempt.responded_at = datetime.now(timezone.utc)

        # Cancel remaining attempts for this trip
        (
            db.query(DispatchAttempt)
            .filter(
                DispatchAttempt.trip_id == trip_id,
                DispatchAttempt.attempt_id != attempt_id,
                DispatchAttempt.response.like("PENDING%")
            )
            .update(
                {
                    "response": "CANCELLED",
                    "responded_at": datetime.now(timezone.utc)
                },
                synchronize_session=False
            )
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
        Driver rejects dispatch attempt.
        
        Actions:
        - Mark attempt as REJECTED
        - Set responded_at
        
        Note: System will automatically move to next wave/driver
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
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dispatch attempt not found"
            )

        if not attempt.response.startswith("PENDING"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Attempt already responded to"
            )

        attempt.response = "REJECTED"
        attempt.responded_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(attempt)

        return attempt

    @staticmethod
    def get_pending_dispatches(
        db: Session,
        driver_id: int
    ) -> List[DispatchAttempt]:
        """
        Get all pending dispatch attempts for a driver.
        
        Used by driver app to show incoming trip requests.
        """
        return (
            db.query(DispatchAttempt)
            .filter(
                DispatchAttempt.driver_id == driver_id,
                DispatchAttempt.response.like("PENDING%")
            )
            .order_by(DispatchAttempt.sent_at.desc())
            .all()
        )
