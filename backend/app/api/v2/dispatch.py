from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps.jwt_auth import get_current_user
from app.core.database import SessionLocal
from app.models.identity import AppUser
from app.models.trips import Trip
from app.schemas.dispatch import (
    AcceptDispatchRequest,
    RejectDispatchRequest,
    DispatchAttemptResponse,
    DriverDispatchNotification
)
from app.services.dispatch_service import DispatchService

router = APIRouter(tags=["Dispatch"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------- Driver Endpoints ----------------------

@router.get("/driver/dispatches/pending")
def get_pending_dispatches(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all pending dispatch attempts for driver.
    
    Used by driver app to show incoming trip requests.
    Returns list of trips awaiting driver response.
    """
    user_id = current_user.get("user_id")
    user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    attempts = DispatchService.get_pending_dispatches(db=db, driver_id=user.user_id)

    # Enrich with trip details
    notifications = []
    for attempt in attempts:
        trip = db.query(Trip).filter(Trip.trip_id == attempt.trip_id).first()
        if trip:
            notifications.append(
                DriverDispatchNotification(
                    attempt_id=attempt.attempt_id,
                    trip_id=trip.trip_id,
                    pickup_lat=trip.pickup_lat,
                    pickup_lng=trip.pickup_lng,
                    drop_lat=trip.drop_lat,
                    drop_lng=trip.drop_lng,
                    rider_name=None,  # Could be fetched if needed
                    estimated_distance_km=None,  # Could be calculated
                    sent_at=attempt.sent_at,
                    expires_in_seconds=30
                )
            )

    return {"pending_dispatches": notifications, "total": len(notifications)}


@router.post("/driver/dispatches/accept")
def accept_dispatch(
    request: AcceptDispatchRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Driver accepts trip request.
    
    Preconditions:
    - Driver is still ONLINE
    - Driver is not BUSY
    - Dispatch attempt is still PENDING
    
    Actions:
    - Assign driver to trip
    - Set driver_shift status to BUSY
    - Mark dispatch_attempt as ACCEPTED
    - Cancel other pending attempts for this trip
    
    Response: Trip details with assigned driver
    """
    user_id = current_user.get("user_id")
    user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get attempt to find trip_id
    from app.models.dispatch import DispatchAttempt
    attempt = (
        db.query(DispatchAttempt)
        .filter(DispatchAttempt.attempt_id == request.attempt_id)
        .first()
    )

    if not attempt:
        raise HTTPException(status_code=404, detail="Dispatch attempt not found")

    # Assign driver to trip
    trip = DispatchService.assign_driver_to_trip(
        db=db,
        trip_id=attempt.trip_id,
        driver_id=user.user_id,
        attempt_id=request.attempt_id
    )

    return {
        "message": "Trip accepted successfully",
        "trip_id": trip.trip_id,
        "status": trip.status,
        "assigned_at": trip.assigned_at
    }


@router.post("/driver/dispatches/reject")
def reject_dispatch(
    request: RejectDispatchRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Driver rejects trip request.
    
    Actions:
    - Mark dispatch_attempt as REJECTED
    - System will automatically escalate to next driver/wave
    
    Response: Confirmation
    """
    user_id = current_user.get("user_id")
    user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    attempt = DispatchService.reject_dispatch_attempt(
        db=db,
        attempt_id=request.attempt_id,
        driver_id=user.user_id
    )

    return {
        "message": "Trip rejected successfully",
        "attempt_id": attempt.attempt_id,
        "responded_at": attempt.responded_at
    }


# ---------------------- Internal/System Endpoints ----------------------

@router.post("/internal/dispatch/trip/{trip_id}")
def dispatch_trip_internal(
    trip_id: int,
    vehicle_category: str = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Internal endpoint to dispatch a trip.
    
    Called automatically after trip creation or manually by system.
    This initiates the wave-based dispatch process.
    
    Args:
        trip_id: Trip to dispatch
        vehicle_category: Optional filter by vehicle category
    
    Returns: Dispatch status
    
    Note: This is a synchronous MVP implementation.
          Production should use async/celery for wave timeouts.
    """
    trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    user_id = current_user.get("user_id")

    # Dispatch trip
    assigned_driver_id = DispatchService.dispatch_trip(
        db=db,
        trip=trip,
        vehicle_category=vehicle_category,
        created_by=user_id
    )

    if assigned_driver_id:
        return {
            "message": "Trip dispatched successfully",
            "trip_id": trip.trip_id,
            "status": "DISPATCHING",
            "assigned_driver_id": assigned_driver_id
        }
    else:
        # Update trip status to NO_DRIVER_AVAILABLE
        trip.status = "NO_DRIVER_AVAILABLE"
        db.commit()

        return {
            "message": "No drivers available",
            "trip_id": trip.trip_id,
            "status": "NO_DRIVER_AVAILABLE"
        }
