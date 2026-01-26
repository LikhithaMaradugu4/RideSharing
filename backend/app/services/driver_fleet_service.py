from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.fleet import Fleet, FleetDriver, DriverProfile, FleetCity, FleetDriverInvite
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
        """
        List all pending invites for the driver.
        
        Returns: List of (FleetDriverInvite, Fleet, FleetCity, City) tuples
        """
        DriverFleetService._get_driver_profile(db, user)

        rows = (
            db.query(FleetDriverInvite, Fleet, FleetCity, City)
            .join(Fleet, Fleet.fleet_id == FleetDriverInvite.fleet_id)
            .join(FleetCity, FleetCity.fleet_id == Fleet.fleet_id)
            .join(City, City.city_id == FleetCity.city_id)
            .filter(
                FleetDriverInvite.driver_id == user.user_id,
                FleetDriverInvite.status == "PENDING",
                Fleet.fleet_type == "BUSINESS",
                Fleet.approval_status == "APPROVED"
            )
            .all()
        )
        return rows

    @staticmethod
    def accept_invite(db: Session, user: AppUser, fleet_id: int) -> FleetDriver:
        """
        Accept a fleet invite and create active fleet_driver association.
        
        Preconditions:
        - Driver must be APPROVED
        - Driver must be OFFLINE (no active shift)
        - Driver must have no active trip (checked via fleet_driver and active shift)
        - Pending invite exists from this fleet
        
        Actions:
        1. End current fleet_driver row (driver's current INDIVIDUAL fleet)
        2. End any active vehicle assignment
        3. Create new fleet_driver row for BUSINESS fleet
        4. Update invite status to ACCEPTED
        
        Returns: FleetDriver (new active association)
        """
        DriverFleetService._get_driver_profile(db, user)

        # Validate invitation exists
        invite = (
            db.query(FleetDriverInvite)
            .filter(
                FleetDriverInvite.fleet_id == fleet_id,
                FleetDriverInvite.driver_id == user.user_id,
                FleetDriverInvite.status == "PENDING"
            )
            .first()
        )
        if not invite:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No pending invite found for this fleet"
            )

        # Validate fleet
        fleet = db.query(Fleet).filter(Fleet.fleet_id == fleet_id).first()
        if not fleet or fleet.fleet_type != "BUSINESS" or fleet.approval_status != "APPROVED":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Fleet is not eligible"
            )

        # Check: Driver is OFFLINE (no active shift)
        # This assumes driver uses DriverShift model; adapt if using different tracking
        from app.models.operations import DriverShift
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
                detail="Driver must be offline to join a fleet. End your shift first."
            )

        # End current active fleet_driver association (INDIVIDUAL fleet)
        current_fleet_assoc = (
            db.query(FleetDriver)
            .filter(
                FleetDriver.driver_id == user.user_id,
                FleetDriver.end_date.is_(None)
            )
            .first()
        )
        now = datetime.now(timezone.utc)
        if current_fleet_assoc:
            current_fleet_assoc.end_date = now
            current_fleet_assoc.updated_by = user.user_id
            current_fleet_assoc.updated_on = now

        # End any active vehicle assignment
        active_assignment = (
            db.query(DriverVehicleAssignment)
            .filter(
                DriverVehicleAssignment.driver_id == user.user_id,
                DriverVehicleAssignment.end_time.is_(None)
            )
            .first()
        )
        if active_assignment:
            active_assignment.end_time = now
            active_assignment.updated_by = user.user_id
            active_assignment.updated_on = now

        # Create new fleet_driver row for BUSINESS fleet
        new_association = FleetDriver(
            fleet_id=fleet_id,
            driver_id=user.user_id,
            start_date=now,
            end_date=None,
            created_by=user.user_id
        )
        db.add(new_association)

        # Update invite status
        invite.status = "ACCEPTED"
        invite.responded_at = now
        invite.updated_by = user.user_id
        invite.updated_on = now

        db.commit()
        db.refresh(new_association)

        return new_association

    @staticmethod
    def reject_invite(db: Session, user: AppUser, fleet_id: int):
        """Reject a fleet invite (soft delete)."""
        DriverFleetService._get_driver_profile(db, user)

        invite = (
            db.query(FleetDriverInvite)
            .filter(
                FleetDriverInvite.fleet_id == fleet_id,
                FleetDriverInvite.driver_id == user.user_id,
                FleetDriverInvite.status == "PENDING"
            )
            .first()
        )
        if not invite:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No pending invite found for this fleet"
            )

        now = datetime.now(timezone.utc)
        invite.status = "REJECTED"
        invite.responded_at = now
        invite.updated_by = user.user_id
        invite.updated_on = now

        db.commit()

        return {"message": "Invite rejected"}
