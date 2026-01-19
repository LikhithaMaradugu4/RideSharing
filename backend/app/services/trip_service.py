from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timezone

from app.models.trips import Trip
from app.models.fleet import DriverProfile
from app.models.operations import DriverShift
from app.models.operations import DriverLocation
from app.models.dispatch import DispatchAttempt
from app.models.identity import AppUser
from app.schemas.trip import RiderRequestTrip
from app.utils.dispatch_attempt import haversine


class TripService:

    @staticmethod
    def request_trip(
        db: Session,
        user: AppUser,
        data: RiderRequestTrip
    ):
        # 1️⃣ Validate user has active session
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is not active"
            )
        
        # Check if user already has an active trip
        existing_trip = (
            db.query(Trip)
            .filter(
                Trip.rider_id == user.user_id,
                Trip.status.in_(["REQUESTED", "ACCEPTED", "ARRIVED", "IN_PROGRESS"])
            )
            .first()
        )
        
        if existing_trip:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"You already have an active trip (Trip ID: {existing_trip.trip_id})"
            )
        
        # 2️⃣ Create trip (REQUESTED)
        trip = Trip(
            rider_id=user.user_id,
            city_id=data.city_id,
            pickup_lat=data.pickup_lat,
            pickup_lng=data.pickup_lng,
            drop_lat=data.drop_lat,
            drop_lng=data.drop_lng,
            status="REQUESTED",
            requested_at=datetime.now(timezone.utc),
            created_by=user.user_id
        )

        db.add(trip)
        db.flush()  # get trip_id

        # 3️⃣ Find available drivers with location
        drivers = (
            db.query(DriverProfile, DriverLocation)
            .join(DriverShift, DriverShift.driver_id == DriverProfile.driver_id)
            .join(DriverLocation, DriverLocation.driver_id == DriverProfile.driver_id)
            .filter(
                DriverProfile.approval_status == "APPROVED",
                DriverShift.ended_at.is_(None)
            )
            .all()
        )

        if not drivers:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No drivers available"
            )

        # 4️⃣ Calculate distance from pickup
        driver_distances = []
        for profile, location in drivers:
            distance = haversine(
                data.pickup_lat,
                data.pickup_lng,
                location.latitude,
                location.longitude
            )
            driver_distances.append((profile, distance))

        # 5️⃣ Sort by nearest
        driver_distances.sort(key=lambda x: x[1])

        # 6️⃣ Pick first 3 drivers
        selected_drivers = driver_distances[:3]

        # 7️⃣ Insert dispatch_attempt rows
        now = datetime.now(timezone.utc)

        for profile, _ in selected_drivers:
            attempt = DispatchAttempt(
                trip_id=trip.trip_id,
                driver_id=profile.driver_id,
                sent_at=now,
                response="SENT",
                created_by=user.user_id
            )
            db.add(attempt)

        db.commit()
        db.refresh(trip)

        return trip
