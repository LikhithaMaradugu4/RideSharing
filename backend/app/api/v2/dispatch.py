"""
Dispatch Routes - Driver-facing dispatch endpoints.

Endpoints:
- POST /drivers/location - Update driver location (Redis GEO + Postgres)
- GET /driver/dispatches/pending - Get pending dispatch offers
- POST /dispatch/{attempt_id}/accept - Accept a dispatch offer
- POST /dispatch/{attempt_id}/reject - Reject a dispatch offer
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from decimal import Decimal

from app.api.deps.jwt_auth import get_current_user
from app.api.deps.authorization import require_approved_driver
from app.core.database import SessionLocal
from app.models.identity import AppUser
from app.models.fleet import DriverProfile
from app.models.trips import Trip
from app.models.dispatch import DispatchAttempt
from app.schemas.dispatch import (
    DriverDispatchNotification,
    DispatchAttemptResponse
)
from app.schemas.trip import VerifyPickupOTPRequest
from app.schemas.driver import UpdateDriverLocationRequest
from app.services.dispatch_service import DispatchService
from app.services.driver_location_service import DriverLocationService
from app.utils.haversine import haversine

router = APIRouter(prefix="/dispatch", tags=["Dispatch"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------- Driver Location Endpoint ----------------------

@router.post("/drivers/location")
def update_driver_location(
    data: UpdateDriverLocationRequest,
    db: Session = Depends(get_db),
    driver_profile: DriverProfile = Depends(require_approved_driver)
):
    """
    Update driver location in Redis GEO and Postgres.
    
    Requires: Approved driver profile
    
    This endpoint should be called periodically by the driver app
    (e.g., every 5-10 seconds when driver is ONLINE).
    
    Redis: GEOADD drivers:geo longitude latitude driver_id
    Postgres: UPDATE driver_location, INSERT driver_location_history
    
    Returns:
        Location update confirmation with timestamp
    """
    result = DriverLocationService.update_location(
        db=db,
        driver_id=driver_profile.driver_id,
        latitude=data.latitude,
        longitude=data.longitude
    )
    
    return result


# ---------------------- Driver Dispatch Endpoints ----------------------

@router.get("/driver/dispatches/pending")
def get_pending_dispatches(
    db: Session = Depends(get_db),
    driver_profile: DriverProfile = Depends(require_approved_driver)
):
    """
    Get all pending dispatch attempts for driver.
    
    Requires: Approved driver profile
    
    Used by driver app to show incoming trip requests.
    Returns list of trips awaiting driver response.
    
    Each offer includes:
    - Pickup/drop coordinates
    - Masked rider name (e.g., "Likhitha M.")
    - Estimated distance
    - Expiration time
    """
    attempts = DispatchService.get_pending_dispatches(db=db, driver_id=driver_profile.driver_id)

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
                    expires_in_seconds=400
                )
            )

    return {"pending_dispatches": notifications, "total": len(notifications)}


@router.post("/{attempt_id}/accept")
def accept_dispatch(
    attempt_id: int,
    db: Session = Depends(get_db),
    driver_profile: DriverProfile = Depends(require_approved_driver)
):
    """
    Driver accepts a dispatch offer.
    
    Requires: Approved driver profile
    
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
    driver_id = driver_profile.driver_id

    # Get attempt to find trip_id
    attempt = (
        db.query(DispatchAttempt)
        .filter(DispatchAttempt.attempt_id == attempt_id)
        .first()
    )

    if not attempt:
        raise HTTPException(status_code=404, detail="Dispatch attempt not found")

    # Verify this attempt belongs to the current driver
    if attempt.driver_id != driver_id:
        raise HTTPException(status_code=403, detail="Not authorized to accept this dispatch")

    # Assign driver to trip
    trip = DispatchService.assign_driver_to_trip(
        db=db,
        trip_id=attempt.trip_id,
        driver_id=driver_id,
        attempt_id=attempt_id
    )

    return {
        "message": "Trip accepted successfully",
        "trip_id": trip.trip_id,
        "status": trip.status,
        "assigned_at": trip.assigned_at,
        "fare_amount": float(trip.fare_amount) if trip.fare_amount else None
    }


@router.post("/{attempt_id}/reject")
def reject_dispatch(
    attempt_id: int,
    db: Session = Depends(get_db),
    driver_profile: DriverProfile = Depends(require_approved_driver)
):
    """
    Driver rejects a dispatch offer.
    
    Requires: Approved driver profile
    
    Actions:
    - Mark dispatch_attempt as REJECTED
    - System will automatically offer to next driver
    
    Response: Confirmation
    """
    driver_id = driver_profile.driver_id

    # Verify this attempt belongs to the current driver
    attempt = (
        db.query(DispatchAttempt)
        .filter(DispatchAttempt.attempt_id == attempt_id)
        .first()
    )
    
    if attempt and attempt.driver_id != driver_id:
        raise HTTPException(status_code=403, detail="Not authorized to reject this dispatch")

    attempt = DispatchService.reject_dispatch_attempt(
        db=db,
        attempt_id=attempt_id,
        driver_id=driver_id
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
    driver_profile: DriverProfile = Depends(require_approved_driver)
):
    """
    Get driver's current active trip (if any).
    
    Requires: Approved driver profile
    
    Returns trip in ASSIGNED, ARRIVED, PICKED_UP, or IN_PROGRESS status.
    """
    driver_id = driver_profile.driver_id
    
    trip = (
        db.query(Trip)
        .filter(
            Trip.driver_id == driver_id,
            Trip.status.in_(["ASSIGNED", "ARRIVED", "PICKED_UP", "IN_PROGRESS"])
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
    driver_profile: DriverProfile = Depends(require_approved_driver)
):
    """
    Driver confirms rider pickup.
    
    Requires: Approved driver profile
    
    Transitions trip from ARRIVED to PICKED_UP.
    Requires OTP verification before pickup.
    
    Flow:
    1. Driver arrives (ASSIGNED -> ARRIVED)
    2. Rider generates OTP
    3. Driver verifies OTP
    4. Driver confirms pickup (ARRIVED -> PICKED_UP)
    """
    from app.services.pickup_otp_service import PickupOTPService
    
    driver_id = driver_profile.driver_id
    
    trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()
    
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    if trip.driver_id != driver_id:
        raise HTTPException(status_code=403, detail="Not authorized for this trip")
    
    if trip.status != "ARRIVED":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot pickup rider for trip in '{trip.status}' status. Driver must arrive first."
        )
    
    # Check OTP verification
    if not PickupOTPService.is_otp_verified(db=db, trip_id=trip_id):
        raise HTTPException(
            status_code=400,
            detail="OTP verification required before pickup. Please verify the OTP from rider."
        )
    
    from datetime import datetime, timezone
    trip.status = "PICKED_UP"
    trip.picked_up_at = datetime.now(timezone.utc)
    trip.updated_by = driver_id
    
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
    driver_profile: DriverProfile = Depends(require_approved_driver)
):
    """
    Driver completes the trip.
    
    Requires: Approved driver profile
    
    Transitions trip from PICKED_UP to COMPLETED.
    Sets driver shift status back to ONLINE.
    """
    driver_id = driver_profile.driver_id
    
    trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()
    
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    if trip.driver_id != driver_id:
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
    trip.updated_by = driver_id
    
    # Set driver shift back to ONLINE
    db.query(DriverShift).filter(
        DriverShift.driver_id == driver_id,
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


# ---------------------- Dispatch Wave Management ----------------------

@router.post("/trip/{trip_id}/advance-wave")
def advance_dispatch_wave(
    trip_id: int,
    vehicle_category: str = Query(..., description="Vehicle category for driver matching"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Advance dispatch to the next wave.
    
    This endpoint should be called when:
    - All dispatch attempts in current wave have been rejected/timed out
    - No driver has accepted yet
    
    Logic:
    - If more waves available: creates dispatch attempts for next wave
    - If all waves exhausted: marks trip as CANCELLED
    
    Args:
        trip_id: Trip ID
        vehicle_category: Vehicle category for driver matching
    
    Returns:
        Dispatch wave status
    """
    user_id = current_user.get("user_id")
    
    result = DispatchService.advance_dispatch_wave(
        db=db,
        trip_id=trip_id,
        vehicle_category=vehicle_category,
        created_by=user_id
    )
    
    return result


@router.get("/trip/{trip_id}/status")
def get_dispatch_status(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get current dispatch status for a trip.
    
    Returns:
    - Trip status
    - Current wave number
    - Pending attempts count
    - Total attempts count
    """
    trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()
    
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    current_wave = DispatchService.get_current_wave(db, trip_id)
    pending_count = DispatchService.count_pending_attempts(db, trip_id)
    total_attempts = (
        db.query(DispatchAttempt)
        .filter(DispatchAttempt.trip_id == trip_id)
        .count()
    )
    
    return {
        "trip_id": trip_id,
        "trip_status": trip.status,
        "driver_id": trip.driver_id,
        "current_wave": current_wave,
        "pending_attempts": pending_count,
        "total_attempts": total_attempts,
        "assigned_at": trip.assigned_at
    }


# ---------------------- Driver Arrival & OTP Endpoints ----------------------

@router.post("/driver/trips/{trip_id}/arrive")
def driver_arrive_at_pickup(
    trip_id: int,
    db: Session = Depends(get_db),
    driver_profile: DriverProfile = Depends(require_approved_driver)
):
    """
    Driver marks arrival at pickup location.
    
    Requires: Approved driver profile
    
    Transitions trip from ASSIGNED to ARRIVED.
    After this, the rider can generate an OTP for pickup verification.
    """
    from datetime import datetime, timezone
    
    driver_id = driver_profile.driver_id
    
    trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()
    
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    if trip.driver_id != driver_id:
        raise HTTPException(status_code=403, detail="Not authorized for this trip")
    
    if trip.status != "ASSIGNED":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot mark arrival for trip in '{trip.status}' status"
        )
    
    trip.status = "ARRIVED"
    trip.updated_by = driver_id
    
    db.commit()
    db.refresh(trip)
    
    return {
        "message": "Driver arrived at pickup location. Waiting for rider OTP.",
        "trip_id": trip.trip_id,
        "status": trip.status
    }


@router.post("/rider/trips/{trip_id}/generate-otp")
def generate_pickup_otp(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Rider generates pickup OTP.
    
    After driver arrives (ARRIVED status), rider generates an OTP.
    The OTP is displayed to the rider who shares it with the driver.
    
    Returns:
        OTP (6-digit code) and expiration time
    """
    from app.services.pickup_otp_service import PickupOTPService
    from app.schemas.trip import GeneratePickupOTPResponse
    
    # Verify the trip belongs to this rider
    trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()
    
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    rider_id = current_user.get("user_id")
    if trip.rider_id != rider_id:
        raise HTTPException(status_code=403, detail="Not authorized for this trip")
    
    result = PickupOTPService.generate_pickup_otp(db=db, trip_id=trip_id)
    
    return GeneratePickupOTPResponse(**result)


@router.post("/driver/trips/{trip_id}/verify-otp")
def verify_pickup_otp(
    trip_id: int,
    request: "VerifyPickupOTPRequest",
    db: Session = Depends(get_db),
    driver_profile: DriverProfile = Depends(require_approved_driver)
):
    """
    Driver verifies pickup OTP.
    
    Driver enters the OTP shared by the rider.
    On successful verification, driver can proceed to pickup the rider.
    
    Returns:
        Verification result (success/failure) and message
    """
    from app.services.pickup_otp_service import PickupOTPService
    from app.schemas.trip import VerifyPickupOTPResponse
    
    driver_id = driver_profile.driver_id
    
    # Verify the trip belongs to this driver
    trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()
    
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    if trip.driver_id != driver_id:
        raise HTTPException(status_code=403, detail="Not authorized for this trip")
    
    result = PickupOTPService.verify_pickup_otp(
        db=db,
        trip_id=trip_id,
        entered_otp=request.otp
    )
    
    return VerifyPickupOTPResponse(**result)


# ---------------------- Rider Active Trip Endpoint ----------------------

@router.get("/rider/active-trip")
def get_rider_active_trip(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get rider's current active trip (if any).
    
    Returns trip in REQUESTED, DISPATCHING, ASSIGNED, ARRIVED, or PICKED_UP status.
    """
    rider_id = current_user.get("user_id")
    
    trip = (
        db.query(Trip)
        .filter(
            Trip.rider_id == rider_id,
            Trip.status.in_(["REQUESTED", "DISPATCHING", "ASSIGNED", "ARRIVED", "PICKED_UP", "IN_PROGRESS"])
        )
        .order_by(Trip.created_on.desc())
        .first()
    )
    
    if not trip:
        return {"active_trip": None}
    
    # Get driver info if assigned
    driver_info = None
    vehicle_info = None
    
    if trip.driver_id:
        driver = db.query(DriverProfile).filter(DriverProfile.driver_id == trip.driver_id).first()
        if driver:
            driver_user = db.query(AppUser).filter(AppUser.user_id == driver.user_id).first()
            driver_info = {
                "driver_id": driver.driver_id,
                "full_name": driver_user.full_name if driver_user else None,
                "phone_number": DispatchService.get_rider_display_name(driver_user.phone_number) if driver_user else None
            }
        
        # Get vehicle info from driver's active assignment
        from app.models.fleet import DriverVehicleAssignment, Vehicle
        assignment = (
            db.query(DriverVehicleAssignment)
            .filter(
                DriverVehicleAssignment.driver_id == trip.driver_id,
                DriverVehicleAssignment.status == "ACTIVE"
            )
            .first()
        )
        if assignment:
            vehicle = db.query(Vehicle).filter(Vehicle.vehicle_id == assignment.vehicle_id).first()
            if vehicle:
                vehicle_info = {
                    "vehicle_id": vehicle.vehicle_id,
                    "registration_number": vehicle.registration_number,
                    "vehicle_category": vehicle.vehicle_category
                }
    
    return {
        "active_trip": {
            "trip_id": trip.trip_id,
            "status": trip.status,
            "pickup_lat": float(trip.pickup_lat),
            "pickup_lng": float(trip.pickup_lng),
            "drop_lat": float(trip.drop_lat) if trip.drop_lat else None,
            "drop_lng": float(trip.drop_lng) if trip.drop_lng else None,
            "fare_amount": float(trip.fare_amount) if trip.fare_amount else None,
            "created_at": trip.created_on,
            "assigned_at": trip.assigned_at,
            "picked_up_at": trip.picked_up_at,
            "driver": driver_info,
            "vehicle": vehicle_info
        }
    }
