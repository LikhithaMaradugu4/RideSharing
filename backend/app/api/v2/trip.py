"""
Trip Routes - Rider trip endpoints.

Endpoints:
- POST /trips - Create a new trip
- GET /trips/{id} - Get trip details
- POST /trips/{id}/cancel - Cancel a trip
- POST /trips/estimate - Get fare estimate
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.api.deps.jwt_auth import get_current_user
from app.core.database import SessionLocal
from app.models.identity import AppUser
from app.models.trips import Trip
from app.schemas.trip import (
    CreateTripRequest,
    CreateTripResponse,
    TripStatusResponse,
    CancelTripResponse,
    FareEstimateRequest,
    FareEstimateResponse,
    ValidateLocationRequest,
    ValidateLocationResponse,
    LocationInfo,
    DriverInfo,
    VehicleInfo,
    PaymentOptionsResponse,
    CreatePaymentRequest,
    CreatePaymentResponse,
    CashConfirmResponse
)
from app.services.trip_service import TripService
from app.services.dispatch_service import DispatchService
from app.services.pricing_service import PricingService
from app.services.geo_service import GeoService


router = APIRouter(prefix="/trips", tags=["Trips"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/validate-location", response_model=ValidateLocationResponse)
def validate_location(
    request: ValidateLocationRequest,
    db: Session = Depends(get_db)
):
    """
    Validate that pickup and drop locations are in a supported city.
    
    Use this before showing fare estimates to ensure locations are valid.
    """
    city, error = GeoService.validate_location(
        db=db,
        pickup_lat=request.pickup_lat,
        pickup_lng=request.pickup_lng,
        drop_lat=request.drop_lat,
        drop_lng=request.drop_lng
    )
    
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    return ValidateLocationResponse(
        city_id=city.city_id,
        city_name=city.name
    )


@router.post("/estimate", response_model=FareEstimateResponse)
def estimate_fare(
    request: FareEstimateRequest,
    db: Session = Depends(get_db)
):
    """
    Get fare estimate for a potential trip.
    
    Returns distance, base fare, surge multiplier, final fare, and nearby driver count.
    Does not create a trip - use POST /trips for that.
    """
    # First validate location to get city_id
    city, error = GeoService.validate_location(
        db=db,
        pickup_lat=request.pickup_lat,
        pickup_lng=request.pickup_lng,
        drop_lat=request.drop_lat,
        drop_lng=request.drop_lng
    )
    
    city_id = city.city_id if city else None
    
    result = PricingService.estimate_fare(
        db=db,
        pickup_lat=request.pickup_lat,
        pickup_lng=request.pickup_lng,
        drop_lat=request.drop_lat,
        drop_lng=request.drop_lng,
        vehicle_category=request.vehicle_category
    )
    
    # Get nearby driver count for this vehicle category using dispatch logic
    nearby_drivers_count = 0
    if city_id:
        try:
            from app.services.dispatch_service import MAX_RADIUS_KM
            eligible_drivers = DispatchService.find_eligible_drivers(
                db=db,
                pickup_lat=request.pickup_lat,
                pickup_lng=request.pickup_lng,
                city_id=city_id,
                vehicle_category=request.vehicle_category,
                radius_km=MAX_RADIUS_KM
            )
            nearby_drivers_count = len(eligible_drivers)
        except Exception as e:
            # Log but don't fail - this is informational only
            print(f"Warning: Could not get nearby driver count: {e}")
            nearby_drivers_count = 0
    
    return FareEstimateResponse(
        distance_km=result["distance_km"],
        base_fare=result["base_fare"],
        surge_multiplier=result["surge_multiplier"],
        final_fare=result["final_fare"],
        surge_zone_id=result["surge_zone_id"],
        nearby_drivers_count=nearby_drivers_count
    )


@router.post("", response_model=CreateTripResponse)
def create_trip(
    request: CreateTripRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new trip request.
    
    Steps:
    1. Validate user and locations
    2. Calculate and lock fare
    3. Create trip with status=REQUESTED
    4. Initiate dispatch to drivers
    
    The fare is LOCKED at this point and will not change.
    """
    user_id = current_user.get("user_id")
    user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create trip
    trip = TripService.create_trip(
        db=db,
        user=user,
        pickup_lat=request.pickup_lat,
        pickup_lng=request.pickup_lng,
        drop_lat=request.drop_lat,
        drop_lng=request.drop_lng,
        vehicle_category=request.vehicle_category
    )
    
    # Initiate dispatch (Wave 1)
    dispatch_success = DispatchService.dispatch_trip(
        db=db,
        trip=trip,
        vehicle_category=request.vehicle_category,
        created_by=user_id
    )
    
    # Refresh trip to get updated status
    db.refresh(trip)
    
    # Note: dispatch_success=False just means no drivers in wave 1
    # Trip stays in DISPATCHING status for advance_dispatch_wave to handle
    
    return CreateTripResponse(
        trip_id=trip.trip_id,
        status=trip.status,
        fare_amount=float(trip.fare_amount) if trip.fare_amount else 0.0,
        currency=trip.currency,
        country_code=trip.country_code,
        fare_snapshot=trip.fare_snapshot
    )


@router.get("/{trip_id}", response_model=TripStatusResponse)
def get_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get trip details.
    
    Returns current trip status, locations, fare, and assigned driver (if any).
    """
    user_id = current_user.get("user_id")
    
    trip = TripService.get_trip_for_rider(
        db=db,
        trip_id=trip_id,
        rider_id=user_id
    )
    
    # Build response with all trip details
    response = TripStatusResponse(
        trip_id=trip.trip_id,
        status=trip.status,
        driver_id=trip.driver_id,
        fare_amount=float(trip.fare_amount) if trip.fare_amount else 0.0,
        currency=trip.currency,
        country_code=trip.country_code,
        fare_snapshot=trip.fare_snapshot,
        pickup_location=LocationInfo(
            lat=float(trip.pickup_lat),
            lng=float(trip.pickup_lng)
        ) if trip.pickup_lat and trip.pickup_lng else None,
        drop_location=LocationInfo(
            lat=float(trip.drop_lat),
            lng=float(trip.drop_lng)
        ) if trip.drop_lat and trip.drop_lng else None,
        pickup_otp=trip.pickup_otp
    )
    
    # Add driver info if assigned
    if trip.driver_id:
        driver = db.query(AppUser).filter(AppUser.user_id == trip.driver_id).first()
        if driver:
            response.driver = DriverInfo(
                driver_id=driver.user_id,
                full_name=driver.full_name,
                phone_number=driver.phone
            )
    
    # Add vehicle info if available
    if trip.vehicle_id:
        from app.models.vehicle import Vehicle
        vehicle = db.query(Vehicle).filter(Vehicle.vehicle_id == trip.vehicle_id).first()
        if vehicle:
            response.vehicle = VehicleInfo(
                vehicle_id=vehicle.vehicle_id,
                vehicle_category=vehicle.category,
                registration_number=vehicle.registration_no
            )
    
    return response


@router.post("/{trip_id}/cancel", response_model=CancelTripResponse)
def cancel_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Cancel a trip.
    
    Only trips in REQUESTED or DISPATCHING status can be cancelled.
    """
    user_id = current_user.get("user_id")
    
    trip = TripService.cancel_trip(
        db=db,
        trip_id=trip_id,
        user_id=user_id
    )
    
    return CancelTripResponse(
        trip_id=trip.trip_id,
        status=trip.status
    )


@router.get("/{trip_id}/payment-options", response_model=PaymentOptionsResponse)
def get_payment_options(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get payment options for a completed trip.
    
    Returns:
    - final_fare: The amount to be paid
    - currency: Currency code (e.g., INR, USD)
    - available_payment_modes: Only CASH (ONLINE disabled)
    - fare_breakdown: Optional detailed breakdown from fare_snapshot
    
    Only available for trips with status=COMPLETED.
    """
    user_id = current_user.get("user_id")
    
    # Get trip - allow both rider and driver to access
    trip = (
        db.query(Trip)
        .filter(
            Trip.trip_id == trip_id,
            Trip.status == "COMPLETED"
        )
        .first()
    )
    
    if not trip:
        raise HTTPException(
            status_code=404,
            detail="Trip not found or not completed"
        )
    
    # Validate user has access to this trip (rider or driver)
    if trip.rider_id != user_id and trip.driver_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this trip"
        )
    
    # Build response - CASH only
    return PaymentOptionsResponse(
        trip_id=trip.trip_id,
        final_fare=float(trip.fare_amount) if trip.fare_amount else 0.0,
        currency=trip.currency,
        available_payment_modes=["CASH"],  # ONLINE disabled
        fare_breakdown=trip.fare_snapshot
    )


@router.get("/{trip_id}/payment", response_model=CreatePaymentResponse)
def get_trip_payment(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get payment info for a trip.
    """
    from app.services.payment_service import PaymentService
    
    user_id = current_user.get("user_id")
    
    # Validate access to trip
    trip = (
        db.query(Trip)
        .filter(Trip.trip_id == trip_id)
        .first()
    )
    
    if not trip:
        raise HTTPException(404, "Trip not found")
    
    # Allow both rider and driver to access
    if trip.rider_id != user_id and trip.driver_id != user_id:
        raise HTTPException(403, "Access denied to this trip")
    
    payment = PaymentService.get_payment_for_trip(db, trip_id)
    
    if not payment:
        raise HTTPException(404, "Payment not found for this trip")
    
    return CreatePaymentResponse(
        payment_id=payment.payment_id,
        trip_id=payment.trip_id,
        amount=float(payment.amount),
        currency=payment.currency,
        payment_mode=payment.payment_mode,
        status=payment.status
    )


@router.post("/{trip_id}/confirm-cash", response_model=CashConfirmResponse)
def confirm_cash_payment(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Driver confirms cash payment received.
    
    This automatically:
    1. Creates payment record if it doesn't exist
    2. Updates payment status to SUCCESS
    3. Runs settlement (commission splits and wallet updates)
    4. Updates trip payment_status to PAID
    
    Returns payment info + settlement breakdown.
    """
    try:
        from app.services.payment_service import PaymentService
        
        driver_id = current_user.get("user_id")
        if not driver_id:
            raise HTTPException(status_code=401, detail="User ID not found")
        
        print(f"Confirming cash payment for trip {trip_id} by driver {driver_id}")
        
        result = PaymentService.confirm_cash_received(
            db=db,
            trip_id=trip_id,
            driver_id=driver_id
        )
        
        payment = result["payment"]
        settlement = result.get("settlement", {})
        
        return CashConfirmResponse(
            payment_id=payment.payment_id,
            trip_id=payment.trip_id,
            amount=float(payment.amount),
            currency=payment.currency,
            payment_mode=payment.payment_mode,
            status=payment.status,
            driver_earning=settlement.get("driver_earning"),
            platform_commission=settlement.get("platform_commission"),
            tenant_commission=settlement.get("tenant_commission"),
            fleet_commission=settlement.get("fleet_commission")
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        print(f"Error in confirm_cash_payment: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to confirm payment: {str(e)}"
        )
