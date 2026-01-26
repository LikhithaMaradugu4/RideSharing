from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.fleet import Fleet, FleetDriver, DriverProfile, FleetCity, FleetDriverInvite
from app.models.vehicle import Vehicle, DriverVehicleAssignment
from app.models.identity import AppUser
from app.models.core import City
from app.models.tenant import TenantCity


class FleetOwnerService:
    """Actions available to an APPROVED BUSINESS fleet owner."""

    # ---------------------- Helpers ----------------------
    @staticmethod
    def _get_owner_fleet(db: Session, user: AppUser) -> Fleet:
        fleet = (
            db.query(Fleet)
            .filter(Fleet.owner_user_id == user.user_id)
            .first()
        )

        if not fleet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fleet not found. Apply and get approval first."
            )

        if fleet.fleet_type != "BUSINESS":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only BUSINESS fleets are allowed for these actions"
            )

        if fleet.approval_status != "APPROVED":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Fleet is not approved"
            )

        return fleet

    @staticmethod
    def _get_driver_profile(db: Session, driver_id: int) -> DriverProfile:
        profile = (
            db.query(DriverProfile)
            .filter(DriverProfile.driver_id == driver_id)
            .first()
        )
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver profile not found"
            )
        if profile.approval_status != "APPROVED":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Driver is not approved"
            )
        return profile

    @staticmethod
    def _ensure_no_active_fleet(db: Session, driver_id: int):
        active = (
            db.query(FleetDriver)
            .filter(
                FleetDriver.driver_id == driver_id,
                FleetDriver.end_date.is_(None)
            )
            .first()
        )
        if active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Driver already has an active fleet association"
            )

    @staticmethod
    def _ensure_no_active_vehicle_assignment(db: Session, driver_id: int):
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

    # ---------------------- Driver Management ----------------------
    @staticmethod
    def invite_driver(db: Session, user: AppUser, driver_id: int) -> FleetDriverInvite:
        """
        Invite a driver to join the fleet.
        
        Creates a FleetDriverInvite record (invitation pending driver acceptance).
        Does NOT immediately create fleet_driver association.
        
        Preconditions:
        - Fleet owner must have approved BUSINESS fleet
        - Driver must be APPROVED
        - Driver must be in same tenant
        - Driver must not have another pending invite from this fleet
        
        Returns: FleetDriverInvite object
        """
        fleet = FleetOwnerService._get_owner_fleet(db, user)

        # Validate driver profile
        profile = FleetOwnerService._get_driver_profile(db, driver_id)

        # Enforce tenant match
        if profile.tenant_id != fleet.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Driver belongs to a different tenant"
            )

        # Check for existing pending invite
        existing = (
            db.query(FleetDriverInvite)
            .filter(
                FleetDriverInvite.fleet_id == fleet.fleet_id,
                FleetDriverInvite.driver_id == driver_id,
                FleetDriverInvite.status == "PENDING"
            )
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Pending invite already exists for this driver"
            )

        # Create invite
        invite = FleetDriverInvite(
            fleet_id=fleet.fleet_id,
            driver_id=driver_id,
            status="PENDING",
            invited_at=datetime.now(timezone.utc)
        )

        db.add(invite)
        db.commit()
        db.refresh(invite)

        return invite

    @staticmethod
    def list_drivers(db: Session, user: AppUser):
        fleet = FleetOwnerService._get_owner_fleet(db, user)

        drivers = (
            db.query(FleetDriver, AppUser)
            .join(AppUser, AppUser.user_id == FleetDriver.driver_id)
            .filter(
                FleetDriver.fleet_id == fleet.fleet_id,
                FleetDriver.end_date.is_(None)
            )
            .all()
        )

        return drivers

    @staticmethod
    def remove_driver(db: Session, user: AppUser, driver_id: int):
        fleet = FleetOwnerService._get_owner_fleet(db, user)

        association = (
            db.query(FleetDriver)
            .filter(
                FleetDriver.fleet_id == fleet.fleet_id,
                FleetDriver.driver_id == driver_id,
                FleetDriver.end_date.is_(None)
            )
            .first()
        )

        if not association:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver is not associated with this fleet"
            )

        now = datetime.now(timezone.utc)
        association.end_date = now
        association.updated_by = user.user_id

        # End any active vehicle assignment for this driver
        active_assignment = (
            db.query(DriverVehicleAssignment)
            .filter(
                DriverVehicleAssignment.driver_id == driver_id,
                DriverVehicleAssignment.end_time.is_(None)
            )
            .first()
        )
        if active_assignment:
            active_assignment.end_time = now
            active_assignment.updated_by = user.user_id

        db.commit()
        db.refresh(association)
        return association

    # ---------------------- Vehicle Assignment ----------------------
    @staticmethod
    def create_assignment(db: Session, user: AppUser, driver_id: int, vehicle_id: int) -> DriverVehicleAssignment:
        fleet = FleetOwnerService._get_owner_fleet(db, user)

        # Ensure driver is in fleet (active association)
        association = (
            db.query(FleetDriver)
            .filter(
                FleetDriver.driver_id == driver_id,
                FleetDriver.fleet_id == fleet.fleet_id,
                FleetDriver.end_date.is_(None)
            )
            .first()
        )
        if not association:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Driver is not active in this fleet"
            )

        # Ensure driver has no active assignment
        FleetOwnerService._ensure_no_active_vehicle_assignment(db, driver_id)

        # Verify vehicle ownership
        vehicle = (
            db.query(Vehicle)
            .filter(Vehicle.vehicle_id == vehicle_id)
            .first()
        )
        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found"
            )
        if vehicle.fleet_id != fleet.fleet_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vehicle does not belong to this fleet"
            )

        # Ensure vehicle has no active assignment
        active_vehicle = (
            db.query(DriverVehicleAssignment)
            .filter(
                DriverVehicleAssignment.vehicle_id == vehicle_id,
                DriverVehicleAssignment.end_time.is_(None)
            )
            .first()
        )
        if active_vehicle:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vehicle already has an active assignment"
            )

        assignment = DriverVehicleAssignment(
            driver_id=driver_id,
            vehicle_id=vehicle_id,
            start_time=datetime.now(timezone.utc),
            end_time=None,
            created_by=user.user_id
        )

        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        return assignment

    @staticmethod
    def end_assignment(db: Session, user: AppUser, assignment_id: int) -> DriverVehicleAssignment:
        fleet = FleetOwnerService._get_owner_fleet(db, user)

        assignment = (
            db.query(DriverVehicleAssignment)
            .join(Vehicle, Vehicle.vehicle_id == DriverVehicleAssignment.vehicle_id)
            .filter(
                DriverVehicleAssignment.assignment_id == assignment_id,
                Vehicle.fleet_id == fleet.fleet_id
            )
            .first()
        )

        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignment not found for this fleet"
            )

        if assignment.end_time:
            return assignment

        assignment.end_time = datetime.now(timezone.utc)
        assignment.updated_by = user.user_id

        db.commit()
        db.refresh(assignment)
        return assignment

    @staticmethod
    def list_active_assignments(db: Session, user: AppUser):
        fleet = FleetOwnerService._get_owner_fleet(db, user)

        assignments = (
            db.query(DriverVehicleAssignment)
            .join(Vehicle, Vehicle.vehicle_id == DriverVehicleAssignment.vehicle_id)
            .filter(
                Vehicle.fleet_id == fleet.fleet_id,
                DriverVehicleAssignment.end_time.is_(None)
            )
            .all()
        )

        return assignments

    # ---------------------- Fleet Cities ----------------------
    @staticmethod
    def add_city(db: Session, user: AppUser, city_id: int) -> FleetCity:
        fleet = FleetOwnerService._get_owner_fleet(db, user)

        # Ensure city exists and belongs to tenant
        tenant_city = (
            db.query(TenantCity)
            .filter(
                TenantCity.tenant_id == fleet.tenant_id,
                TenantCity.city_id == city_id
            )
            .first()
        )
        if not tenant_city:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="City not allowed for this tenant"
            )

        # Prevent duplicates
        existing = (
            db.query(FleetCity)
            .filter(
                FleetCity.fleet_id == fleet.fleet_id,
                FleetCity.city_id == city_id
            )
            .first()
        )
        if existing:
            return existing

        record = FleetCity(
            fleet_id=fleet.fleet_id,
            city_id=city_id,
            created_by=user.user_id
        )

        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def list_cities(db: Session, user: AppUser):
        fleet = FleetOwnerService._get_owner_fleet(db, user)

        rows = (
            db.query(FleetCity, City)
            .join(City, City.city_id == FleetCity.city_id)
            .filter(FleetCity.fleet_id == fleet.fleet_id)
            .all()
        )
        return rows

    @staticmethod
    def remove_city(db: Session, user: AppUser, city_id: int):
        fleet = FleetOwnerService._get_owner_fleet(db, user)

        record = (
            db.query(FleetCity)
            .filter(
                FleetCity.fleet_id == fleet.fleet_id,
                FleetCity.city_id == city_id
            )
            .first()
        )
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="City not associated with this fleet"
            )

        # Ensure at least one city remains
        city_count = (
            db.query(FleetCity)
            .filter(FleetCity.fleet_id == fleet.fleet_id)
            .count()
        )
        if city_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Fleet must have at least one city"
            )

        db.delete(record)
        db.commit()
        return {"message": "City removed"}
