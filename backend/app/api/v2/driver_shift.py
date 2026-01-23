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
    return DriverShiftResponse.from_attributes(shift)


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
    return DriverShiftResponse.from_attributes(shift)


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
