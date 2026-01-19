from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timezone

from app.models.fleet import DriverProfile
from app.models.operations import DriverShift,DriverLocation,DriverLocationHistory
from app.models.identity import AppUser


class DriverLocationService:

    @staticmethod
    def update_location(
        db: Session,
        user: AppUser,
        latitude: float,
        longitude: float
    ):
        if user.role != "DRIVER":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only drivers can update location"
            )

        profile = (
            db.query(DriverProfile)
            .filter(DriverProfile.driver_id == user.user_id)
            .first()
        )

        if not profile or profile.approval_status != "APPROVED":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Driver is not approved"
            )

        active_shift = (
            db.query(DriverShift)
            .filter(
                DriverShift.driver_id == user.user_id,
                DriverShift.ended_at.is_(None)
            )
            .first()
        )

        if not active_shift:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Driver does not have an active shift"
            )

        now = datetime.now(timezone.utc)

        # Upsert latest location
        location = (
            db.query(DriverLocation)
            .filter(DriverLocation.driver_id == user.user_id)
            .first()
        )

        if location:
            location.latitude = latitude
            location.longitude = longitude
            location.last_updated = now
        else:
            location = DriverLocation(
                driver_id=user.user_id,
                latitude=latitude,
                longitude=longitude,
                last_updated=now
            )
            db.add(location)

        # Insert history
        history = DriverLocationHistory(
            driver_id=user.user_id,
            latitude=latitude,
            longitude=longitude,
            recorded_at=now
        )

        db.add(history)
        db.commit()


