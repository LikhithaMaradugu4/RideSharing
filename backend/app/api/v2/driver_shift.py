from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps.jwt_auth import get_current_user
from app.core.database import SessionLocal
from app.models.identity import AppUser
from app.schemas.driver_shift import (
    DriverShiftResponse,
    ShiftStatusResponse,
    EndShiftRequest,
    EndAssignmentRequest,
    EndAssignmentResponse
)
from app.services.driver_shift_service_v2 import DriverShiftServiceV2

router = APIRouter(tags=["Driver Shift"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------- Start Shift (Go Online) ----------------------

@router.post("/driver/availability/online", response_model=DriverShiftResponse)
def start_shift(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Start shift (GO ONLINE).
    
    Preconditions:
    - Driver has APPROVED profile
    - Driver has active fleet association
    - Driver has active vehicle assignment
    - Vehicle has all required documents (RC, INSURANCE, VEHICLE_PHOTO)
    - No active shift exists
    
    Response: DriverShift object with status=ONLINE
    """
    user_id = current_user.get("user_id")
    user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    shift = DriverShiftServiceV2.start_shift(db=db, user=user)
    return DriverShiftResponse.model_validate(shift)


# ---------------------- End Shift (Go Offline) ----------------------

@router.post("/driver/availability/offline", response_model=DriverShiftResponse)
def end_shift(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    End shift (GO OFFLINE).
    
    Preconditions:
    - Active shift exists
    - Shift status is not BUSY
    
    Response: DriverShift object with status=OFFLINE, ended_at=now()
    
    Note: Vehicle assignment remains active (use /driver/shift/end to terminate assignment)
    """
    user_id = current_user.get("user_id")
    user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    shift = DriverShiftServiceV2.end_shift(db=db, user=user)
    return DriverShiftResponse.model_validate(shift)


# ---------------------- End Assignment ----------------------

@router.post("/driver/shift/end", response_model=EndAssignmentResponse)
def end_assignment(
    request: EndAssignmentRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    End vehicle assignment (driver is done with this vehicle).
    
    Preconditions:
    - No active shift (driver must be OFFLINE)
    - Active vehicle assignment exists
    
    Response: Updated DriverVehicleAssignment with end_time=now()
    
    Note: After ending assignment, driver must be reassigned before next shift
    """
    user_id = current_user.get("user_id")
    user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    assignment = DriverShiftServiceV2.end_assignment(db=db, user=user)
    
    return EndAssignmentResponse(
        assignment_id=assignment.assignment_id,
        driver_id=assignment.driver_id,
        vehicle_id=assignment.vehicle_id,
        start_time=assignment.start_time,
        end_time=assignment.end_time,
        message="Assignment ended successfully"
    )


# ---------------------- Get Shift Status ----------------------

@router.get("/driver/shift/active", response_model=ShiftStatusResponse)
def get_shift_status(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get current shift and vehicle assignment status.
    
    Returns:
    - is_online: True if shift is ONLINE or BUSY
    - shift_id, shift_status: Current shift info (null if none)
    - vehicle_id, vehicle_registration: Current assignment info (null if none)
    - started_at: When driver went online
    
    Note: Call this to understand driver's current state before any operations
    """
    user_id = current_user.get("user_id")
    user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    status_data = DriverShiftServiceV2.get_shift_status(db=db, user=user)

    shift = status_data.get("shift")
    assignment = status_data.get("assignment")
    vehicle = status_data.get("vehicle")

    return ShiftStatusResponse(
        is_online=shift is not None and shift.status in ("ONLINE", "BUSY"),
        shift_id=shift.shift_id if shift else None,
        shift_status=shift.status if shift else None,
        vehicle_id=vehicle.vehicle_id if vehicle else None,
        vehicle_registration=vehicle.registration_no if vehicle else None,
        fleet_name=None,  # Could be populated with vehicle's fleet name if needed
        assignment_start=assignment.start_time if assignment else None,
        started_at=shift.started_at if shift else None
    )


# ---------------------- Shift Readiness Check ----------------------

@router.get("/driver/shift/readiness")
def check_shift_readiness(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Check if driver meets all prerequisites to go online.
    
    Returns detailed checklist of requirements with status.
    Useful for diagnosing why a driver cannot start a shift.
    """
    from app.models.fleet import DriverProfile, Fleet, FleetDriver
    from app.models.vehicle import Vehicle, DriverVehicleAssignment, VehicleDocument
    from app.models.operations import DriverShift
    
    user_id = current_user.get("user_id")
    user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    
    result = {
        "can_go_online": False,
        "checks": {}
    }
    
    # Check 1: Driver profile exists and is APPROVED
    driver_profile = db.query(DriverProfile).filter(DriverProfile.driver_id == user_id).first()
    result["checks"]["driver_profile"] = {
        "exists": driver_profile is not None,
        "approval_status": driver_profile.approval_status if driver_profile else None,
        "is_approved": driver_profile.approval_status == "APPROVED" if driver_profile else False
    }
    
    # Check 2: Has active fleet association
    fleet_assoc = (
        db.query(FleetDriver, Fleet)
        .join(Fleet, Fleet.fleet_id == FleetDriver.fleet_id)
        .filter(
            FleetDriver.driver_id == user_id,
            FleetDriver.end_date.is_(None)
        )
        .first()
    )
    if fleet_assoc:
        fleet_driver, fleet = fleet_assoc
        result["checks"]["fleet_association"] = {
            "exists": True,
            "fleet_id": fleet.fleet_id,
            "fleet_name": fleet.fleet_name,
            "fleet_type": fleet.fleet_type,
            "fleet_approval_status": fleet.approval_status,
            "is_fleet_approved": fleet.approval_status == "APPROVED"
        }
    else:
        result["checks"]["fleet_association"] = {
            "exists": False,
            "fleet_id": None,
            "fleet_name": None,
            "fleet_type": None,
            "fleet_approval_status": None,
            "is_fleet_approved": False
        }
    
    # Check 3: Has active vehicle assignment
    vehicle_assoc = (
        db.query(DriverVehicleAssignment, Vehicle)
        .join(Vehicle, Vehicle.vehicle_id == DriverVehicleAssignment.vehicle_id)
        .filter(
            DriverVehicleAssignment.driver_id == user_id,
            DriverVehicleAssignment.end_time.is_(None)
        )
        .first()
    )
    if vehicle_assoc:
        assignment, vehicle = vehicle_assoc
        # Check vehicle documents
        required_docs = {"RC", "INSURANCE", "VEHICLE_PHOTO"}
        actual_docs = set(
            doc[0] for doc in db.query(VehicleDocument.document_type)
            .filter(VehicleDocument.vehicle_id == vehicle.vehicle_id)
            .all()
        )
        missing_docs = required_docs - actual_docs
        
        result["checks"]["vehicle_assignment"] = {
            "exists": True,
            "assignment_id": assignment.assignment_id,
            "vehicle_id": vehicle.vehicle_id,
            "registration_no": vehicle.registration_no,
            "vehicle_approval_status": vehicle.approval_status,
            "is_vehicle_approved": vehicle.approval_status == "APPROVED",
            "required_documents": list(required_docs),
            "present_documents": list(actual_docs),
            "missing_documents": list(missing_docs),
            "documents_complete": len(missing_docs) == 0
        }
        
        # Check if vehicle belongs to driver's fleet
        if fleet_assoc:
            result["checks"]["vehicle_assignment"]["belongs_to_fleet"] = vehicle.fleet_id == fleet_assoc[1].fleet_id
        else:
            result["checks"]["vehicle_assignment"]["belongs_to_fleet"] = False
    else:
        result["checks"]["vehicle_assignment"] = {
            "exists": False,
            "assignment_id": None,
            "vehicle_id": None,
            "registration_no": None,
            "vehicle_approval_status": None,
            "is_vehicle_approved": False,
            "documents_complete": False
        }
    
    # Check 4: No active shift already
    active_shift = db.query(DriverShift).filter(
        DriverShift.driver_id == user_id,
        DriverShift.ended_at.is_(None)
    ).first()
    result["checks"]["no_active_shift"] = {
        "has_active_shift": active_shift is not None,
        "shift_id": active_shift.shift_id if active_shift else None,
        "shift_status": active_shift.status if active_shift else None
    }
    
    # Determine overall readiness
    checks = result["checks"]
    result["can_go_online"] = (
        checks["driver_profile"]["is_approved"] and
        checks["fleet_association"]["exists"] and
        checks["fleet_association"]["is_fleet_approved"] and
        checks["vehicle_assignment"]["exists"] and
        checks["vehicle_assignment"]["is_vehicle_approved"] and
        checks["vehicle_assignment"].get("documents_complete", False) and
        checks["vehicle_assignment"].get("belongs_to_fleet", False) and
        not checks["no_active_shift"]["has_active_shift"]
    )
    
    return result
