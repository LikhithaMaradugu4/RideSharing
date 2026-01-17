from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.fleet import DriverProfile
from app.models.identity import AppUser
from app.schemas.driver import DriverApplyRequest

class DriverService:

    @staticmethod
    def apply_to_tenant(
        db: Session,
        user: AppUser,
        data: DriverApplyRequest
    ):
        # Role check
        if user.role != "DRIVER":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only drivers can apply"
            )

        # Prevent duplicate application
        existing = (
            db.query(DriverProfile)
            .filter(DriverProfile.driver_id == user.user_id)
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Driver already applied to a tenant"
            )

        driver_profile = DriverProfile(
            driver_id=user.user_id,
            tenant_id=data.tenant_id,
            driver_type=data.driver_type,
            approval_status="PENDING",
            rating=5.00,
            created_by=user.user_id
        )

        db.add(driver_profile)
        db.commit()
        db.refresh(driver_profile)

        return driver_profile
    
    @staticmethod
    def get_my_profile(db: Session, user: AppUser):
        if user.role != "DRIVER":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only drivers can access this"
            )

        profile = (
            db.query(DriverProfile)
            .filter(DriverProfile.driver_id == user.user_id)
            .first()
        )

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver profile not found. Apply first."
            )

        return profile


    
