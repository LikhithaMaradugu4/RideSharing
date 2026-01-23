from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.fleet import Fleet, FleetDriver, DriverProfile, FleetCity
from app.models.vehicle import DriverVehicleAssignment
from app.models.identity import AppUser
from app.models.core import City


class DriverFleetService:
    """Driver-side actions for BUSINESS fleet joining and discovery."""

    # ---------------------- Helpers ----------------------
    @staticmethod
    def _get_driver_profile(db: Session, user: AppUser) -> DriverProfile:
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
                detail="Driver is not approved"
            )
        return profile

    @staticmethod
    def _ensure_no_active_fleet(db: Session, driver_id: int, exclude_fleet_id: int | None = None):
        query = (
            db.query(FleetDriver)
            .filter(
                FleetDriver.driver_id == driver_id,
                FleetDriver.end_date.is_(None)
            )
        )
        if exclude_fleet_id:
            query = query.filter(FleetDriver.fleet_id != exclude_fleet_id)

        active = query.first()
        if active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Driver already has an active fleet association"
            )

    @staticmethod
    def _ensure_no_active_vehicle(db: Session, driver_id: int):
        active = (
            db.query(DriverVehicleAssignment)
            .filter(
                DriverVehicleAssignment.driver_id == driver_id,
                DriverVehicleAssignment.end_time.is_(None)
            )
            .first()
        )
        if active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Driver already has an active vehicle assignment"
            )

    # ---------------------- Discovery ----------------------
    @staticmethod
    def discover_fleets(
        db: Session,
        user: AppUser,
        city_id: Optional[int] = None,
        tenant_id: Optional[int] = None
    ) -> List[tuple]:
        DriverFleetService._get_driver_profile(db, user)

        query = (
            db.query(Fleet, FleetCity, City)
            .join(FleetCity, FleetCity.fleet_id == Fleet.fleet_id)
            .join(City, City.city_id == FleetCity.city_id)
            .filter(
                Fleet.fleet_type == "BUSINESS",
                Fleet.approval_status == "APPROVED"
            )
        )

        if city_id:
            query = query.filter(FleetCity.city_id == city_id)
        if tenant_id:
            query = query.filter(Fleet.tenant_id == tenant_id)

        return query.all()

    # ---------------------- Invitations ----------------------
    @staticmethod
    def list_invites(db: Session, user: AppUser):
        DriverFleetService._get_driver_profile(db, user)

        rows = (
            db.query(FleetDriver, Fleet, FleetCity, City)
            .join(Fleet, Fleet.fleet_id == FleetDriver.fleet_id)
            .join(FleetCity, FleetCity.fleet_id == Fleet.fleet_id)
            .join(City, City.city_id == FleetCity.city_id)
            .filter(
                FleetDriver.driver_id == user.user_id,
                FleetDriver.end_date.is_(None),
                Fleet.fleet_type == "BUSINESS",
                Fleet.approval_status == "APPROVED"
            )
            .all()
        )
        return rows

    @staticmethod
    def accept_invite(db: Session, user: AppUser, fleet_id: int) -> FleetDriver:
        DriverFleetService._get_driver_profile(db, user)

        # Validate invitation exists
        invite = (
            db.query(FleetDriver)
            .filter(
                FleetDriver.fleet_id == fleet_id,
                FleetDriver.driver_id == user.user_id,
                FleetDriver.end_date.is_(None)
            )
            .first()
        )
        if not invite:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active invite found"
            )

        # Validate fleet
        fleet = db.query(Fleet).filter(Fleet.fleet_id == fleet_id).first()
        if not fleet or fleet.fleet_type != "BUSINESS" or fleet.approval_status != "APPROVED":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Fleet is not eligible"
            )

        # Ensure no other active fleet or vehicle assignment
        DriverFleetService._ensure_no_active_fleet(db, user.user_id, exclude_fleet_id=fleet_id)
        DriverFleetService._ensure_no_active_vehicle(db, user.user_id)

        # Accept: ensure start_date set to now (overwrite invite time)
        invite.start_date = datetime.now(timezone.utc)
        invite.updated_by = user.user_id

        # End any other associations (safety)
        other = (
            db.query(FleetDriver)
            .filter(
                FleetDriver.driver_id == user.user_id,
                FleetDriver.fleet_id != fleet_id,
                FleetDriver.end_date.is_(None)
            )
            .all()
        )
        now = invite.start_date
        for assoc in other:
            assoc.end_date = now
            assoc.updated_by = user.user_id

        db.commit()
        db.refresh(invite)
        return invite

    @staticmethod
    def reject_invite(db: Session, user: AppUser, fleet_id: int):
        DriverFleetService._get_driver_profile(db, user)

        invite = (
            db.query(FleetDriver)
            .filter(
                FleetDriver.fleet_id == fleet_id,
                FleetDriver.driver_id == user.user_id,
                FleetDriver.end_date.is_(None)
            )
            .first()
        )
        if not invite:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active invite found"
            )

        # Soft rejection: delete invite to avoid active association
        db.delete(invite)
        db.commit()
        return {"message": "Invite rejected"}
