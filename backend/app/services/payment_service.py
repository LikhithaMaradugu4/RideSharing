from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import uuid

from app.models.trips import Trip
from app.models.payments import Payment
from app.services.settlement_service import run_cash_settlement


# =============================================================================
# CASH-ONLY PAYMENT POLICY
# =============================================================================
# Online payments are disabled. Only CASH payments are supported.
# Message to show users: "In-app payments are under development. Cash payments supported."
# =============================================================================

ALLOWED_PAYMENT_MODES = ["CASH"]  # ONLINE is disabled


class PaymentService:

    @staticmethod
    def auto_create_cash_payment(
        db: Session,
        trip: Trip
    ):
        """
        Auto-create cash payment record when trip is completed.
        Called automatically by trip service.
        
        Args:
            db: Database session
            trip: Completed Trip object
            
        Returns:
            Payment object with status=PENDING_CASH
        """
        # Check if payment record already exists
        existing_payment = db.query(Payment).filter(Payment.trip_id == trip.trip_id).first()
        if existing_payment:
            return existing_payment

        # Get currency and amount from trip
        currency = trip.currency if trip.currency else "INR"
        amount = float(trip.fare_amount) if trip.fare_amount else 0.0

        # Create payment record with status=PENDING_CASH
        payment = Payment(
            trip_id=trip.trip_id,
            amount=amount,
            currency=currency,
            payment_mode="CASH",
            status="PENDING_CASH",  # Waiting for driver confirmation
            created_by=trip.driver_id,
            created_on=datetime.now(timezone.utc)
        )
        db.add(payment)
        db.flush()  # Get ID without committing

        return payment

    @staticmethod
    def get_payment_for_trip(
        db: Session,
        trip_id: int
    ):
        """
        Get payment record for a trip.
        
        Args:
            db: Database session
            trip_id: Trip ID
            
        Returns:
            Payment object or None
        """
        return db.query(Payment).filter(Payment.trip_id == trip_id).first()



    @staticmethod
    def confirm_cash_received(
        db: Session,
        trip_id: int,
        driver_id: int
    ):
        """
        Driver confirms cash payment received.
        
        Args:
            db: Database session
            trip_id: Trip ID
            driver_id: Driver user ID confirming payment
            
        Returns:
            Updated Payment object with settlement info
        """
        # 1. Get trip and validate driver
        trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()
        if not trip:
            raise HTTPException(404, "Trip not found")
        
        if trip.driver_id != driver_id:
            raise HTTPException(403, "Only the assigned driver can confirm this payment")
        
        if trip.status != "COMPLETED":
            raise HTTPException(400, "Trip must be completed before confirming payment")
        
        # 2. Get or create payment record
        payment = db.query(Payment).filter(Payment.trip_id == trip_id).first()
        
        if not payment:
            # Auto-create if doesn't exist
            payment = PaymentService.auto_create_cash_payment(db, trip)
        
        # 3. Validate payment
        if payment.payment_mode != "CASH":
            raise HTTPException(400, "This payment is not a CASH payment")
        
        if payment.status == "SUCCESS":
            raise HTTPException(400, "Payment already confirmed")
        
        # 4. Update payment status
        payment.status = "SUCCESS"
        payment.confirmed_by_driver_id = driver_id
        payment.confirmed_at = datetime.now(timezone.utc)
        payment.updated_on = datetime.now(timezone.utc)
        payment.updated_by = driver_id
        
        # 5. Update trip payment status
        trip.payment_status = "PAID"
        
        # 6. Run settlement - creates ledger entries and triggers wallet updates
        settlement_result = run_cash_settlement(
            db=db,
            trip=trip,
            amount=float(payment.amount),
            payment_mode="CASH"
        )
        
        db.commit()
        db.refresh(payment)
        
        return {
            "payment": payment,
            "settlement": settlement_result
        }
