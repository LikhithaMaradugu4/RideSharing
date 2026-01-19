from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.fleet import DriverProfile
from app.models.tenant import TenantAdmin
from app.models.identity import AppUser

class TenantAdminService:

    @staticmethod
    def _get_admin_tenant(db: Session, user: AppUser):
        admin = (
            db.query(TenantAdmin)
            .filter(TenantAdmin.user_id == user.user_id)
            .first()
        )

        if not admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not a tenant admin"
            )

        return admin.tenant_id

    @staticmethod
    def approve_driver(db: Session, user: AppUser, driver_id: int):
        if user.role != "TENANT_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only tenant admins can approve drivers"
            )

        tenant_id = TenantAdminService._get_admin_tenant(db, user)

        driver = (
            db.query(DriverProfile)
            .filter(
                DriverProfile.driver_id == driver_id,
                DriverProfile.tenant_id == tenant_id
            )
            .first()
        )

        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found for this tenant"
            )

        if driver.approval_status != "PENDING":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Driver is not in pending state"
            )

        driver.approval_status = "APPROVED"
        db.commit()

    @staticmethod
    def reject_driver(db: Session, user: AppUser, driver_id: int):
        if user.role != "TENANT_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only tenant admins can reject drivers"
            )

        tenant_id = TenantAdminService._get_admin_tenant(db, user)

        driver = (
            db.query(DriverProfile)
            .filter(
                DriverProfile.driver_id == driver_id,
                DriverProfile.tenant_id == tenant_id
            )
            .first()
        )

        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found for this tenant"
            )

        driver.approval_status = "REJECTED"
        db.commit()
