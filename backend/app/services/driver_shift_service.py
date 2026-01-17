from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timezone

from app.models.fleet import DriverProfile
from app.models.operations import DriverShift
from app.models.identity import AppUser


class DriverShiftService:

    @staticmethod
    def start_shift(db: Session, user: AppUser):
        if user.role != "DRIVER":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only drivers can start a shift"
            )

        profile = (
            db.query(DriverProfile)
            .filter(DriverProfile.driver_id == user.user_id)
            .first()
        )

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver profile not found"
            )

        if profile.approval_status != "APPROVED":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Driver is not approved yet"
            )

        active_shift = (
            db.query(DriverShift)
            .filter(
                DriverShift.driver_id == user.user_id,
                DriverShift.ended_at.is_(None)
            )
            .first()
        )

        if active_shift:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Driver already has an active shift"
            )

        shift = DriverShift(
            driver_id=user.user_id,
            tenant_id=profile.tenant_id,
            status="ACTIVE",
            started_at=datetime.now(timezone.utc),
            created_by=user.user_id
        )

        db.add(shift)
        db.commit()
        db.refresh(shift)

        return shift
    
    @staticmethod
    def end_shift(db: Session, user: AppUser):
        if user.role != "DRIVER":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only drivers can end a shift"
            )

        shift = (
            db.query(DriverShift)
            .filter(
                DriverShift.driver_id == user.user_id,
                DriverShift.ended_at.is_(None)
            )
            .first()
        )

        if not shift:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active shift found"
            )

        shift.ended_at = datetime.now(timezone.utc)
        shift.status = "ENDED"

        db.commit()

