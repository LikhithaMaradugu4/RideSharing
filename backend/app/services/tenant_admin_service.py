from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional

from app.models.fleet import DriverProfile, Fleet
from app.models.identity import UserKYC
from app.models.vehicle import Vehicle, VehicleDocument
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

    @staticmethod
    def get_pending_drivers(db: Session, user: AppUser):
        if user.role != "TENANT_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only tenant admins can view pending drivers"
            )

        tenant_id = TenantAdminService._get_admin_tenant(db, user)

        drivers = (
            db.query(DriverProfile, AppUser)
            .join(AppUser, DriverProfile.driver_id == AppUser.user_id)
            .filter(
                DriverProfile.tenant_id == tenant_id,
                DriverProfile.approval_status == "PENDING"
            )
            .all()
        )

        return drivers

    @staticmethod
    def approve_driver_with_fleet(
        db: Session,
        user: AppUser,
        driver_id: int,
        allowed_vehicle_categories: List[str]
    ):
        if user.role != "TENANT_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only tenant admins can approve drivers"
            )

        if not allowed_vehicle_categories:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="allowed_vehicle_categories is required"
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

        # Update driver profile
        driver.approval_status = "APPROVED"
        driver.allowed_vehicle_categories = allowed_vehicle_categories

        # Auto-create INDIVIDUAL fleet
        fleet = Fleet(
            owner_user_id=driver_id,
            tenant_id=tenant_id,
            fleet_name=f"Driver {driver_id} Fleet",
            fleet_type="INDIVIDUAL",
            approval_status="APPROVED",
            status="ACTIVE",
            created_by=user.user_id
        )

        db.add(fleet)
        db.commit()

        return driver

    @staticmethod
    def reject_driver_with_reason(
        db: Session,
        user: AppUser,
        driver_id: int,
        reason: Optional[str] = None
    ):
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
        # Note: reason could be stored in a separate field if schema supports it
        db.commit()

    @staticmethod
    def approve_fleet(db: Session, user: AppUser, fleet_id: int):
        if user.role != "TENANT_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only tenant admins can approve fleets"
            )

        tenant_id = TenantAdminService._get_admin_tenant(db, user)

        fleet = (
            db.query(Fleet)
            .filter(
                Fleet.fleet_id == fleet_id,
                Fleet.tenant_id == tenant_id
            )
            .first()
        )

        if not fleet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fleet not found for this tenant"
            )

        if fleet.fleet_type != "BUSINESS":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only BUSINESS fleets can be approved here"
            )

        if fleet.approval_status != "PENDING":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Fleet is not in pending state"
            )

        fleet.approval_status = "APPROVED"
        db.commit()

    @staticmethod
    def reject_fleet(db: Session, user: AppUser, fleet_id: int):
        if user.role != "TENANT_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only tenant admins can reject fleets"
            )

        tenant_id = TenantAdminService._get_admin_tenant(db, user)

        fleet = (
            db.query(Fleet)
            .filter(
                Fleet.fleet_id == fleet_id,
                Fleet.tenant_id == tenant_id
            )
            .first()
        )

        if not fleet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fleet not found for this tenant"
            )

        fleet.approval_status = "REJECTED"
        db.commit()

    @staticmethod
    def get_pending_fleets_with_docs(db: Session, user: AppUser):
        if user.role != "TENANT_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only tenant admins can view pending fleets"
            )

        tenant_id = TenantAdminService._get_admin_tenant(db, user)

        fleets = (
            db.query(Fleet)
            .filter(
                Fleet.tenant_id == tenant_id,
                Fleet.approval_status == "PENDING"
            )
            .all()
        )

        result = []
        for fleet in fleets:
            docs = list(fleet.documents) if hasattr(fleet, "documents") else []
            result.append((fleet, docs))

        return result

    @staticmethod
    def get_driver_documents(db: Session, user: AppUser, driver_id: int):
        if user.role != "TENANT_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only tenant admins can view driver documents"
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

        documents = (
            db.query(UserKYC)
            .filter(UserKYC.user_id == driver_id)
            .all()
        )

        return documents

    @staticmethod
    def get_vehicle_documents(db: Session, user: AppUser, vehicle_id: int):
        if user.role != "TENANT_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only tenant admins can view vehicle documents"
            )

        tenant_id = TenantAdminService._get_admin_tenant(db, user)

        vehicle = (
            db.query(Vehicle)
            .join(Fleet, Vehicle.fleet_id == Fleet.fleet_id)
            .filter(
                Vehicle.vehicle_id == vehicle_id,
                Fleet.tenant_id == tenant_id
            )
            .first()
        )

        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found for this tenant"
            )

        documents = (
            db.query(VehicleDocument)
            .filter(VehicleDocument.vehicle_id == vehicle_id)
            .all()
        )

        return documents
