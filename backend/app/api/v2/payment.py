"""
Payment Routes - Cash payment endpoints.

Endpoints:
- GET /payments/trip/{trip_id} - Get payment for a trip
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps.jwt_auth import get_current_user
from app.core.database import SessionLocal
from app.services.payment_service import PaymentService
from app.models.trips import Trip

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/trip/{trip_id}")
def get_payment_for_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get payment record for a trip.
    Accessible by both rider and driver of the trip.
    """
    user_id = current_user.get("user_id")
    
    # Validate access to trip
    trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()
    if not trip:
        raise HTTPException(404, "Trip not found")
    
    if trip.rider_id != user_id and trip.driver_id != user_id:
        raise HTTPException(403, "Access denied to this trip")
    
    payment = PaymentService.get_payment_for_trip(db, trip_id)
    
    if not payment:
        raise HTTPException(404, "Payment not found for this trip")
    
    return {
        "payment_id": payment.payment_id,
        "trip_id": payment.trip_id,
        "amount": float(payment.amount),
        "currency": payment.currency,
        "payment_mode": payment.payment_mode,
        "status": payment.status,
        "confirmed_at": payment.confirmed_at.isoformat() if payment.confirmed_at else None
    }
