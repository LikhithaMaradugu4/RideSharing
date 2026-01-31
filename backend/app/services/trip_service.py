"""
Trip Service - Trip creation and lifecycle management.

Trip lifecycle:
REQUESTED → DISPATCHING → ASSIGNED → PICKED_UP → COMPLETED
REQUESTED / DISPATCHING → CANCELLED
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timezone
from typing import Optional

from app.models.trips import Trip
from app.models.identity import AppUser
from app.services.geo_service import GeoService
from app.services.pricing_service import PricingService


class TripService:
    """Service for trip operations."""

    # Valid trip statuses
    ACTIVE_STATUSES = ["REQUESTED", "DISPATCHING", "ASSIGNED", "PICKED_UP"]
    CANCELLABLE_STATUSES = ["REQUESTED", "DISPATCHING", "ASSIGNED", "DRIVER_EN_ROUTE"]
    
    @staticmethod
    def create_trip(
        db: Session,
        user: AppUser,
        pickup_lat: float,
        pickup_lng: float,
        drop_lat: float,
        drop_lng: float,
        vehicle_category: str
    ) -> Trip:
        """
        Create a new trip.
        
        Steps:
        1. Validate user is active
        2. Check no existing active trip
        3. Validate locations (city check)
        4. Calculate fare (locked at request time)
        5. Create trip with status=REQUESTED
        
        Args:
            db: Database session
            user: Current user (rider)
            pickup_lat, pickup_lng: Pickup coordinates
            drop_lat, drop_lng: Drop coordinates
            vehicle_category: Vehicle category code
        
        Returns:
            Created Trip object
        
        Raises:
            HTTPException on validation failure
        """
        # 1. Validate user is active
        if user.status != "ACTIVE":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is not active"
            )
        
        # 2. Check for existing active trip
        existing_trip = (
            db.query(Trip)
            .filter(
                Trip.rider_id == user.user_id,
                Trip.status.in_(TripService.ACTIVE_STATUSES)
            )
            .first()
        )
        
        if existing_trip:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"You already have an active trip (Trip ID: {existing_trip.trip_id})"
            )
        
        # 3. Validate locations
        city, error = GeoService.validate_location(
            db, pickup_lat, pickup_lng, drop_lat, drop_lng
        )
        
        if error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error
            )
        
        # 4. Calculate fare (locked at request time)
        fare_breakdown = PricingService.calculate_fare(
            db=db,
            city_id=city.city_id,
            vehicle_category=vehicle_category,
            pickup_lat=pickup_lat,
            pickup_lng=pickup_lng,
            drop_lat=drop_lat,
            drop_lng=drop_lng
        )
        
        # 5. Create trip
        trip = Trip(
            rider_id=user.user_id,
            city_id=city.city_id,
            surge_zone_id=fare_breakdown.surge_zone_id,
            pickup_lat=pickup_lat,
            pickup_lng=pickup_lng,
            drop_lat=drop_lat,
            drop_lng=drop_lng,
            status="REQUESTED",
            fare_amount=fare_breakdown.fare_applied,
            requested_at=datetime.now(timezone.utc),
            created_by=user.user_id
        )
        
        db.add(trip)
        db.commit()
        db.refresh(trip)
        
        return trip
    
    @staticmethod
    def get_trip(db: Session, trip_id: int) -> Optional[Trip]:
        """
        Get trip by ID.
        
        Args:
            db: Database session
            trip_id: Trip ID
        
        Returns:
            Trip object or None
        """
        return db.query(Trip).filter(Trip.trip_id == trip_id).first()
    
    @staticmethod
    def get_trip_for_rider(db: Session, trip_id: int, rider_id: int) -> Trip:
        """
        Get trip by ID for a specific rider.
        
        Args:
            db: Database session
            trip_id: Trip ID
            rider_id: Rider's user ID
        
        Returns:
            Trip object
        
        Raises:
            HTTPException if not found or not authorized
        """
        trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()
        
        if not trip:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trip not found"
            )
        
        if trip.rider_id != rider_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this trip"
            )
        
        return trip
    
    @staticmethod
    def cancel_trip(db: Session, trip_id: int, user_id: int) -> Trip:
        """
        Cancel a trip.
        
        Only trips in REQUESTED or DISPATCHING status can be cancelled.
        
        Args:
            db: Database session
            trip_id: Trip ID
            user_id: User requesting cancellation
        
        Returns:
            Updated Trip object
        
        Raises:
            HTTPException if trip cannot be cancelled
        """
        trip = TripService.get_trip_for_rider(db, trip_id, user_id)
        
        if trip.status not in TripService.CANCELLABLE_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel trip in '{trip.status}' status"
            )
        
        trip.status = "CANCELLED"
        trip.cancelled_at = datetime.now(timezone.utc)
        trip.updated_by = user_id
        
        db.commit()
        db.refresh(trip)
        
        return trip
    
    @staticmethod
    def update_trip_status(
        db: Session,
        trip_id: int,
        new_status: str,
        updated_by: int
    ) -> Trip:
        """
        Update trip status (internal use).
        
        Args:
            db: Database session
            trip_id: Trip ID
            new_status: New status
            updated_by: User ID making the update
        
        Returns:
            Updated Trip object
        """
        trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()
        
        if not trip:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trip not found"
            )
        
        trip.status = new_status
        trip.updated_by = updated_by
        
        # Set timestamp based on status
        now = datetime.now(timezone.utc)
        if new_status == "ASSIGNED":
            trip.assigned_at = now
        elif new_status == "PICKED_UP":
            trip.picked_up_at = now
        elif new_status == "COMPLETED":
            trip.completed_at = now
        elif new_status == "CANCELLED":
            trip.cancelled_at = now
        
        db.commit()
        db.refresh(trip)
        
        return trip
