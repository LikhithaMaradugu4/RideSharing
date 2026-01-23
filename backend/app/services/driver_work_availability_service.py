from datetime import date, datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.vehicle import DriverWorkAvailability
from app.models.fleet import Fleet, FleetDriver, DriverProfile
from app.models.identity import AppUser


class DriverWorkAvailabilityService:
    """Driver work availability for BUSINESS fleets."""

    @staticmethod
    def _get_active_fleet(db: Session, user: AppUser) -> Fleet:
        """Get driver's active BUSINESS fleet association."""
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

        # Get active fleet association
        fleet_assoc = (
            db.query(FleetDriver, Fleet)
            .join(Fleet, Fleet.fleet_id == FleetDriver.fleet_id)
            .filter(
                FleetDriver.driver_id == user.user_id,
                FleetDriver.end_date.is_(None),
                Fleet.fleet_type == "BUSINESS",
                Fleet.approval_status == "APPROVED"
            )
            .first()
        )

        if not fleet_assoc:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Driver has no active BUSINESS fleet association"
            )

        return fleet_assoc[1]

    @staticmethod
    def declare_availability(
        db: Session,
        user: AppUser,
        data_date: date,
        is_available: bool,
        note: Optional[str] = None
    ) -> DriverWorkAvailability:
        """Create or update work availability for a date."""
        fleet = DriverWorkAvailabilityService._get_active_fleet(db, user)

        # Prevent updating past dates (optional MVP rule - can be removed)
        # if data_date < date.today():
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail="Cannot update past availability"
        #     )

        # Check if record exists
        existing = (
            db.query(DriverWorkAvailability)
            .filter(
                DriverWorkAvailability.driver_id == user.user_id,
                DriverWorkAvailability.fleet_id == fleet.fleet_id,
                DriverWorkAvailability.date == data_date
            )
            .first()
        )

        if existing:
            existing.is_available = is_available
            existing.note = note
            existing.updated_by = user.user_id
            existing.updated_on = datetime.now(timezone.utc)
        else:
            existing = DriverWorkAvailability(
                driver_id=user.user_id,
                fleet_id=fleet.fleet_id,
                date=data_date,
                is_available=is_available,
                note=note,
                created_by=user.user_id
            )
            db.add(existing)

        db.commit()
        db.refresh(existing)
        return existing

    @staticmethod
    def list_driver_availability(
        db: Session,
        user: AppUser,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[DriverWorkAvailability]:
        """List driver's availability records."""
        fleet = DriverWorkAvailabilityService._get_active_fleet(db, user)

        query = (
            db.query(DriverWorkAvailability)
            .filter(
                DriverWorkAvailability.driver_id == user.user_id,
                DriverWorkAvailability.fleet_id == fleet.fleet_id
            )
        )

        if start_date:
            query = query.filter(DriverWorkAvailability.date >= start_date)
        if end_date:
            query = query.filter(DriverWorkAvailability.date <= end_date)

        return query.order_by(DriverWorkAvailability.date.desc()).all()

    @staticmethod
    def list_fleet_driver_availability(
        db: Session,
        user: AppUser,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[tuple]:
        """List all drivers' availability in fleet (Fleet Owner view)."""
        # Verify fleet ownership
        fleet = (
            db.query(Fleet)
            .filter(Fleet.owner_user_id == user.user_id)
            .first()
        )
        if not fleet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fleet not found"
            )
        if fleet.fleet_type != "BUSINESS" or fleet.approval_status != "APPROVED":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Fleet is not eligible"
            )

        query = (
            db.query(DriverWorkAvailability, AppUser)
            .join(AppUser, AppUser.user_id == DriverWorkAvailability.driver_id)
            .filter(DriverWorkAvailability.fleet_id == fleet.fleet_id)
        )

        if start_date:
            query = query.filter(DriverWorkAvailability.date >= start_date)
        if end_date:
            query = query.filter(DriverWorkAvailability.date <= end_date)

        return query.order_by(DriverWorkAvailability.date.desc()).all()

    @staticmethod
    def check_availability(
        db: Session,
        driver_id: int,
        fleet_id: int,
        check_date: date
    ) -> bool:
        """Check if driver is available on given date (for assignment validation)."""
        record = (
            db.query(DriverWorkAvailability)
            .filter(
                DriverWorkAvailability.driver_id == driver_id,
                DriverWorkAvailability.fleet_id == fleet_id,
                DriverWorkAvailability.date == check_date
            )
            .first()
        )

        # MVP: If no record exists, allow assignment (soft rule)
        if not record:
            return True

        return record.is_available
