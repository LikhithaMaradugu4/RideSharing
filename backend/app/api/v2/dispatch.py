"""
Dispatch Routes - Driver-facing dispatch endpoints.

Endpoints:
- GET /driver/dispatches/pending - Get pending dispatch offers
- POST /dispatch/{attempt_id}/accept - Accept a dispatch offer
- POST /dispatch/{attempt_id}/reject - Reject a dispatch offer
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from decimal import Decimal

from app.api.deps.jwt_auth import get_current_user
from app.core.database import SessionLocal
from app.models.identity import AppUser
from app.models.trips import Trip
from app.models.dispatch import DispatchAttempt
from app.schemas.dispatch import (
    DriverDispatchNotification,
    DispatchAttemptResponse
)
from app.services.dispatch_service import DispatchService
from app.utils.haversine import haversine

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
    
    Each offer includes:
    - Pickup/drop coordinates
    - Masked rider name (e.g., "Likhitha M.")
    - Estimated distance
    - Expiration time
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
            # Get rider info for masked name
            rider = db.query(AppUser).filter(AppUser.user_id == trip.rider_id).first()
            rider_name = DispatchService.get_rider_display_name(
                rider.full_name if rider else None
            )
            
            # Calculate estimated distance
            distance_km = None
            if trip.drop_lat and trip.drop_lng:
                distance_km = round(
                    haversine(
                        float(trip.pickup_lat),
                        float(trip.pickup_lng),
                        float(trip.drop_lat),
                        float(trip.drop_lng)
                    ),
                    2
                )
            
            notifications.append(
                DriverDispatchNotification(
                    attempt_id=attempt.attempt_id,
                    trip_id=trip.trip_id,
                    pickup_lat=trip.pickup_lat,
                    pickup_lng=trip.pickup_lng,
                    drop_lat=trip.drop_lat,
                    drop_lng=trip.drop_lng,
                    rider_name=rider_name,
                    estimated_distance_km=distance_km,
                    sent_at=attempt.sent_at,
                    expires_in_seconds=15
                )
            )

    return {"pending_dispatches": notifications, "total": len(notifications)}


@router.post("/dispatch/{attempt_id}/accept")
def accept_dispatch(
    attempt_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Driver accepts a dispatch offer.
    
    Preconditions:
    - Driver is still ONLINE
    - Driver is not BUSY
    - Dispatch attempt is still PENDING
    - Trip is still in DISPATCHING status
    
    Actions:
    - Assign driver to trip (atomic: first wins)
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
    attempt = (
        db.query(DispatchAttempt)
        .filter(DispatchAttempt.attempt_id == attempt_id)
        .first()
    )

    if not attempt:
        raise HTTPException(status_code=404, detail="Dispatch attempt not found")

    # Verify this attempt belongs to the current driver
    if attempt.driver_id != user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to accept this dispatch")

    # Assign driver to trip
    trip = DispatchService.assign_driver_to_trip(
        db=db,
        trip_id=attempt.trip_id,
        driver_id=user.user_id,
        attempt_id=attempt_id
    )

    return {
        "message": "Trip accepted successfully",
        "trip_id": trip.trip_id,
        "status": trip.status,
        "assigned_at": trip.assigned_at,
        "fare_amount": float(trip.fare_amount) if trip.fare_amount else None
    }


@router.post("/dispatch/{attempt_id}/reject")
def reject_dispatch(
    attempt_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Driver rejects a dispatch offer.
    
    Actions:
    - Mark dispatch_attempt as REJECTED
    - System will automatically offer to next driver
    
    Response: Confirmation
    """
    user_id = current_user.get("user_id")
    user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Verify this attempt belongs to the current driver
    attempt = (
        db.query(DispatchAttempt)
        .filter(DispatchAttempt.attempt_id == attempt_id)
        .first()
    )
    
    if attempt and attempt.driver_id != user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to reject this dispatch")

    attempt = DispatchService.reject_dispatch_attempt(
        db=db,
        attempt_id=attempt_id,
        driver_id=user.user_id
    )

    return {
        "message": "Trip rejected successfully",
        "attempt_id": attempt.attempt_id,
        "responded_at": attempt.responded_at
    }


# ---------------------- Driver Trip Lifecycle Endpoints ----------------------

@router.get("/driver/trips/active")
def get_active_trip(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get driver's current active trip (if any).
    
    Returns trip in ASSIGNED or PICKED_UP status.
    """
    user_id = current_user.get("user_id")
    user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    trip = (
        db.query(Trip)
        .filter(
            Trip.driver_id == user.user_id,
            Trip.status.in_(["ASSIGNED", "PICKED_UP"])
        )
        .first()
    )
    
    if not trip:
        return {"active_trip": None}
    
    # Get rider info for masked name
    rider = db.query(AppUser).filter(AppUser.user_id == trip.rider_id).first()
    rider_name = DispatchService.get_rider_display_name(
        rider.full_name if rider else None
    )
    
    return {
        "active_trip": {
            "trip_id": trip.trip_id,
            "status": trip.status,
            "pickup_lat": float(trip.pickup_lat),
            "pickup_lng": float(trip.pickup_lng),
            "drop_lat": float(trip.drop_lat) if trip.drop_lat else None,
            "drop_lng": float(trip.drop_lng) if trip.drop_lng else None,
            "rider_name": rider_name,
            "fare_amount": float(trip.fare_amount) if trip.fare_amount else None,
            "assigned_at": trip.assigned_at,
            "picked_up_at": trip.picked_up_at
        }
    }


@router.post("/driver/trips/{trip_id}/pickup")
def pickup_rider(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Driver confirms rider pickup.
    
    Transitions trip from ASSIGNED to PICKED_UP.
    """
    user_id = current_user.get("user_id")
    user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()
    
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    if trip.driver_id != user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized for this trip")
    
    if trip.status != "ASSIGNED":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot pickup rider for trip in '{trip.status}' status"
        )
    
    from datetime import datetime, timezone
    trip.status = "PICKED_UP"
    trip.picked_up_at = datetime.now(timezone.utc)
    trip.updated_by = user.user_id
    
    db.commit()
    db.refresh(trip)
    
    return {
        "message": "Rider picked up successfully",
        "trip_id": trip.trip_id,
        "status": trip.status,
        "picked_up_at": trip.picked_up_at
    }


@router.post("/driver/trips/{trip_id}/complete")
def complete_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Driver completes the trip.
    
    Transitions trip from PICKED_UP to COMPLETED.
    Sets driver shift status back to ONLINE.
    """
    user_id = current_user.get("user_id")
    user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()
    
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    if trip.driver_id != user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized for this trip")
    
    if trip.status != "PICKED_UP":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot complete trip in '{trip.status}' status"
        )
    
    from datetime import datetime, timezone
    from app.models.operations import DriverShift
    
    trip.status = "COMPLETED"
    trip.completed_at = datetime.now(timezone.utc)
    trip.updated_by = user.user_id
    
    # Set driver shift back to ONLINE
    db.query(DriverShift).filter(
        DriverShift.driver_id == user.user_id,
        DriverShift.ended_at.is_(None)
    ).update(
        {"status": "ONLINE"},
        synchronize_session=False
    )
    
    db.commit()
    db.refresh(trip)
    
    return {
        "message": "Trip completed successfully",
        "trip_id": trip.trip_id,
        "status": trip.status,
        "completed_at": trip.completed_at,
        "fare_amount": float(trip.fare_amount) if trip.fare_amount else None
    }
