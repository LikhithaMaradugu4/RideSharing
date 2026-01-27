from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timezone
from typing import Optional

from app.models.fleet import DriverProfile, Fleet, FleetDriver
from app.models.operations import DriverShift
from app.models.vehicle import Vehicle, DriverVehicleAssignment, VehicleDocument
from app.models.identity import AppUser


class DriverShiftServiceV2:
    """
    Phase-2 Driver Shift Lifecycle Management.
    
    Semantics:
    - Planning (work_availability) → Assignment (vehicle_assignment) → Shift (goes online)
    - One active shift per driver (DB enforced)
    - One active vehicle assignment per driver (DB enforced)
    - Shift status: ONLINE (available) | BUSY (on trip) | OFFLINE (not working)
    """

    @staticmethod
    def validate_shift_eligibility(db: Session, user: AppUser) -> tuple:
        """
        Validate driver is eligible for shift operations.
        
        Returns: (driver_profile, active_fleet, active_assignment, vehicle, tenant_id)
        Raises: HTTPException if any validation fails
        """
        # Check 1: User is authenticated
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not authenticated"
            )

        # Check 2: Driver profile exists and is APPROVED
        driver_profile = (
            db.query(DriverProfile)
            .filter(DriverProfile.driver_id == user.user_id)
            .first()
        )
        if not driver_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver profile not found"
            )
        if driver_profile.approval_status != "APPROVED":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Driver is not approved"
            )

        # Check 3: Has exactly ONE active fleet association
        active_fleet_assoc = (
            db.query(FleetDriver, Fleet)
            .join(Fleet, Fleet.fleet_id == FleetDriver.fleet_id)
            .filter(
                FleetDriver.driver_id == user.user_id,
                FleetDriver.end_date.is_(None),  # Active association
                Fleet.approval_status == "APPROVED"
            )
            .first()
        )
        if not active_fleet_assoc:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Driver has no active fleet association"
            )

        active_fleet = active_fleet_assoc[1]

        # Check 4: Has exactly ONE active vehicle assignment
        active_assignment = (
            db.query(DriverVehicleAssignment, Vehicle)
            .join(Vehicle, Vehicle.vehicle_id == DriverVehicleAssignment.vehicle_id)
            .filter(
                DriverVehicleAssignment.driver_id == user.user_id,
                DriverVehicleAssignment.end_time.is_(None),  # Active assignment
                Vehicle.approval_status == "APPROVED"
            )
            .first()
        )
        if not active_assignment:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Driver has no active vehicle assignment"
            )

        assignment, vehicle = active_assignment

        # Check 5: Vehicle belongs to driver's active fleet
        if vehicle.fleet_id != active_fleet.fleet_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Vehicle does not belong to driver's active fleet"
            )

        # Check 6: Vehicle documents are complete
        required_docs = {"RC", "INSURANCE", "VEHICLE_PHOTO"}
        actual_docs = set(
            db.query(VehicleDocument.document_type)
            .filter(VehicleDocument.vehicle_id == vehicle.vehicle_id)
            .all()
        )
        actual_docs = {doc[0] for doc in actual_docs}
        
        if not required_docs.issubset(actual_docs):
            missing = required_docs - actual_docs
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Vehicle missing documents: {', '.join(missing)}"
            )

        return driver_profile, active_fleet, assignment, vehicle, active_fleet.tenant_id

    @staticmethod
    def start_shift(db: Session, user: AppUser) -> DriverShift:
        """
        Start shift (GO ONLINE).
        
        Preconditions:
        - No active shift (ended_at IS NULL)
        - All eligibility checks pass
        
        Actions:
        - Create DriverShift with status=ONLINE
        
        Returns: DriverShift object
        """
        # Validate eligibility
        driver_profile, active_fleet, assignment, vehicle, tenant_id = (
            DriverShiftServiceV2.validate_shift_eligibility(db, user)
        )

        # Check: No active shift
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

        # Create shift
        shift = DriverShift(
            driver_id=user.user_id,
            tenant_id=tenant_id,
            vehicle_id=vehicle.vehicle_id,
            status="ONLINE",
            started_at=datetime.now(timezone.utc),
            created_by=user.user_id
        )

        db.add(shift)
        db.commit()
        db.refresh(shift)

        return shift

    @staticmethod
    def end_shift(db: Session, user: AppUser) -> DriverShift:
        """
        End shift (GO OFFLINE).
        
        Preconditions:
        - Active shift exists
        - Shift status != BUSY
        
        Actions:
        - Update DriverShift: status=OFFLINE, ended_at=now()
        
        Returns: Updated DriverShift object
        """
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
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active shift found"
            )

        if shift.status == "BUSY":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot go offline while on a trip"
            )

        shift.status = "OFFLINE"
        shift.ended_at = datetime.now(timezone.utc)
        shift.updated_by = user.user_id
        shift.updated_on = datetime.now(timezone.utc)

        db.commit()
        db.refresh(shift)

        return shift

    @staticmethod
    def get_active_shift(db: Session, user: AppUser) -> Optional[DriverShift]:
        """
        Get driver's active shift if exists.
        
        Returns: DriverShift or None
        """
        return (
            db.query(DriverShift)
            .filter(
                DriverShift.driver_id == user.user_id,
                DriverShift.ended_at.is_(None)
            )
            .first()
        )

    @staticmethod
    def set_shift_busy(db: Session, driver_id: int) -> DriverShift:
        """
        Set shift status to BUSY (system-controlled on trip acceptance).
        
        Used internally by trip service when driver accepts a trip.
        """
        shift = (
            db.query(DriverShift)
            .filter(
                DriverShift.driver_id == driver_id,
                DriverShift.ended_at.is_(None)
            )
            .first()
        )

        if not shift:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active shift found"
            )

        shift.status = "BUSY"
        shift.updated_on = datetime.now(timezone.utc)

        db.commit()
        db.refresh(shift)

        return shift

    @staticmethod
    def set_shift_online(db: Session, driver_id: int) -> DriverShift:
        """
        Set shift status back to ONLINE (system-controlled on trip complete/cancel).
        
        Used internally by trip service when driver completes or cancels a trip.
        """
        shift = (
            db.query(DriverShift)
            .filter(
                DriverShift.driver_id == driver_id,
                DriverShift.ended_at.is_(None)
            )
            .first()
        )

        if not shift:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active shift found"
            )

        if shift.status != "BUSY":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Shift is not busy"
            )

        shift.status = "ONLINE"
        shift.updated_on = datetime.now(timezone.utc)

        db.commit()
        db.refresh(shift)

        return shift

    @staticmethod
    def end_assignment(db: Session, user: AppUser) -> DriverVehicleAssignment:
        """
        End vehicle assignment (driver is done with this vehicle).
        
        Preconditions:
        - No active shift (must be OFFLINE)
        - Active assignment exists
        
        Actions:
        - Update DriverVehicleAssignment: end_time=now()
        
        Returns: Updated assignment
        """
        # Check: No active shift
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
                detail="Must go offline before ending assignment"
            )

        # Get active assignment
        assignment = (
            db.query(DriverVehicleAssignment)
            .filter(
                DriverVehicleAssignment.driver_id == user.user_id,
                DriverVehicleAssignment.end_time.is_(None)
            )
            .first()
        )

        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active vehicle assignment found"
            )

        assignment.end_time = datetime.now(timezone.utc)
        assignment.updated_by = user.user_id
        assignment.updated_on = datetime.now(timezone.utc)

        db.commit()
        db.refresh(assignment)

        return assignment

    @staticmethod
    def get_shift_status(db: Session, user: AppUser) -> dict:
        """
        Get current shift and vehicle assignment status.
        
        Returns: {shift, assignment, vehicle, fleet} or appropriate 404
        """
        # Get active shift if exists
        shift = DriverShiftServiceV2.get_active_shift(db, user)

        # Get active assignment if exists
        assignment = (
            db.query(DriverVehicleAssignment, Vehicle)
            .join(Vehicle, Vehicle.vehicle_id == DriverVehicleAssignment.vehicle_id)
            .filter(
                DriverVehicleAssignment.driver_id == user.user_id,
                DriverVehicleAssignment.end_time.is_(None)
            )
            .first()
        )

        result = {
            "shift": shift,
            "assignment": assignment[0] if assignment else None,
            "vehicle": assignment[1] if assignment else None
        }

        return result
