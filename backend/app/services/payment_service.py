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
    def create_payment_record(
        db: Session,
        trip_id: int,
        rider_id: int,
        payment_mode: str
    ):
        """
        Create a payment record with status=CREATED (no money movement).
        
        CASH-ONLY: Only payment_mode = CASH is allowed.
        ONLINE payments are rejected at this level.
        
        Args:
            db: Database session
            trip_id: Trip ID
            rider_id: Rider user ID
            payment_mode: Must be "CASH" (ONLINE is rejected)
            
        Returns:
            Payment object with status=CREATED
        """
        # ENFORCE CASH-ONLY POLICY
        if payment_mode not in ALLOWED_PAYMENT_MODES:
            raise HTTPException(
                status_code=400, 
                detail="In-app payments are under development. Cash payments supported."
            )

        # 1. Validate trip
        trip = (
            db.query(Trip)
            .filter(
                Trip.trip_id == trip_id,
                Trip.rider_id == rider_id,
                Trip.status == "COMPLETED"
            )
            .first()
        )

        if not trip:
            raise HTTPException(400, "Trip not found or not completed")

        # Check if payment record already exists
        existing_payment = db.query(Payment).filter(Payment.trip_id == trip_id).first()
        if existing_payment:
            raise HTTPException(400, "Payment record already exists for this trip")

        # 2. Get currency and amount from trip
        currency = trip.currency if trip.currency else "INR"
        amount = float(trip.fare_amount) if trip.fare_amount else 0.0

        # 3. For CASH payments, no gateway_order_id needed
        gateway_order_id = None

        # 4. Create payment record with status=CREATED (no money movement)
        payment = Payment(
            trip_id=trip.trip_id,
            amount=amount,
            currency=currency,
            payment_mode=payment_mode,
            status="CREATED",  # NOT "SUCCESS" - no money moved yet
            gateway_order_id=gateway_order_id,
            created_by=rider_id,
            created_on=datetime.now(timezone.utc)
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)

        return payment

    @staticmethod
    def create_payment(
        db: Session,
        trip_id: int,
        rider_id: int,
        payment_mode: str,
        amount: float,
        gateway_name: Optional[str] = None,
        gateway_order_id: Optional[str] = None,
        gateway_payment_id: Optional[str] = None,
        gateway_signature: Optional[str] = None,
        gateway_payload: Optional[Dict[str, Any]] = None
    ):
        """
        LEGACY METHOD: Creates payment and immediately settles (moves money).
        
        CASH-ONLY: ONLINE payments are rejected.
        """
        # ENFORCE CASH-ONLY POLICY
        if payment_mode not in ALLOWED_PAYMENT_MODES:
            raise HTTPException(
                status_code=400, 
                detail="In-app payments are under development. Cash payments supported."
            )
        
        # 1. Validate trip
        trip = (
            db.query(Trip)
            .filter(
                Trip.trip_id == trip_id,
                Trip.rider_id == rider_id,
                Trip.status == "COMPLETED"
            )
            .first()
        )

        if not trip:
            raise HTTPException(400, "Invalid or incomplete trip")

        if trip.payment_status == "SUCCESS":
            raise HTTPException(400, "Payment already done")

        # 2. Get currency from trip (multi-currency support)
        currency = trip.currency if hasattr(trip, 'currency') else "INR"

        # 3. Create payment record
        payment = Payment(
            trip_id=trip.trip_id,
            amount=amount,
            currency=currency,
            payment_mode=payment_mode,
            status="SUCCESS",
            gateway_name=gateway_name,
            gateway_order_id=gateway_order_id,
            gateway_payment_id=gateway_payment_id,
            gateway_signature=gateway_signature,
            gateway_payload=gateway_payload,
            created_by=rider_id,
            created_on=datetime.now(timezone.utc)
        )
        db.add(payment)

        # 4. Update trip payment status
        trip.payment_status = "SUCCESS"

        # 5. Settlement (CASH only)
        run_cash_settlement(
            db=db,
            trip=trip,
            amount=amount,
            payment_mode=payment_mode
        )

        db.commit()
        db.refresh(payment)

        return payment

    @staticmethod
    def process_webhook(
        db: Session,
        gateway_name: str,
        gateway_order_id: str,
        gateway_payment_id: str,
        gateway_signature: str,
        webhook_status: str,
        payload: Optional[Dict[str, Any]] = None
    ):
        """
        Process payment gateway webhook.
        
        This is Phase 2a of payment flow (ONLINE payments):
        - Verify signature (basic check)
        - Check idempotency using gateway_payment_id
        - Update payment.status = SUCCESS or FAILED
        - Store gateway references
        - NO wallet updates
        - NO ledger entries
        
        Args:
            db: Database session
            gateway_name: Payment gateway name (razorpay, stripe, etc.)
            gateway_order_id: Gateway order ID
            gateway_payment_id: Gateway payment ID (for idempotency)
            gateway_signature: Gateway signature for verification
            webhook_status: "SUCCESS" or "FAILED"
            payload: Full webhook payload
            
        Returns:
            Updated Payment object
        """
        # TODO: Add proper signature verification based on gateway_name
        # For now, basic validation
        
        # 1. Check idempotency - find payment by gateway_payment_id
        payment = db.query(Payment).filter(
            Payment.gateway_order_id == gateway_order_id
        ).first()
        
        if not payment:
            raise HTTPException(404, "Payment not found for this gateway order")
        
        # If payment already processed with this gateway_payment_id, return (idempotent)
        if payment.gateway_payment_id == gateway_payment_id and payment.status in ["SUCCESS", "FAILED"]:
            return payment
        
        # 2. Validate payment mode
        if payment.payment_mode != "ONLINE":
            raise HTTPException(400, "This payment is not an ONLINE payment")
        
        # 3. Update payment status based on webhook
        if webhook_status == "SUCCESS":
            payment.status = "SUCCESS"
        elif webhook_status == "FAILED":
            payment.status = "FAILED"
        else:
            raise HTTPException(400, f"Invalid webhook status: {webhook_status}")
        
        # 4. Store gateway references
        payment.gateway_name = gateway_name
        payment.gateway_payment_id = gateway_payment_id
        payment.gateway_signature = gateway_signature
        payment.gateway_payload = payload
        payment.updated_on = datetime.now(timezone.utc)
        payment.updated_by = payment.created_by  # Same as creator
        
        db.commit()
        db.refresh(payment)
        
        return payment

    @staticmethod
    def confirm_cash_received(
        db: Session,
        payment_id: int,
        driver_id: int
    ):
        """
        Driver confirms cash payment received.
        
        This is Phase 2b of payment flow (CASH payments):
        - Validate driver is assigned to the trip
        - Update payment.status = SUCCESS
        - Record confirmed_by_driver_id
        - Timestamp confirmation
        - NO wallet updates
        - NO ledger entries
        
        Args:
            db: Database session
            payment_id: Payment ID
            driver_id: Driver user ID confirming payment
            
        Returns:
            Updated Payment object
        """
        # 1. Get payment
        payment = db.query(Payment).filter(Payment.payment_id == payment_id).first()
        
        if not payment:
            raise HTTPException(404, "Payment not found")
        
        # 2. Validate payment mode
        if payment.payment_mode != "CASH":
            raise HTTPException(400, "This payment is not a CASH payment")
        
        # 3. Check payment status
        if payment.status == "SUCCESS":
            raise HTTPException(400, "Payment already confirmed")
        
        if payment.status != "CREATED":
            raise HTTPException(400, f"Payment cannot be confirmed in status: {payment.status}")
        
        # 4. Validate driver is assigned to this trip
        trip = db.query(Trip).filter(Trip.trip_id == payment.trip_id).first()
        if not trip:
            raise HTTPException(404, "Trip not found")
        
        if trip.driver_id != driver_id:
            raise HTTPException(403, "Only the assigned driver can confirm this payment")
        
        # 5. Update payment status
        payment.status = "SUCCESS"
        payment.confirmed_by_driver_id = driver_id
        payment.confirmed_at = datetime.now(timezone.utc)
        payment.updated_on = datetime.now(timezone.utc)
        payment.updated_by = driver_id
        
        # 6. Run settlement ONLY when:
        #    - payment.status == SUCCESS
        #    - payment.payment_mode == CASH
        # This creates ledger entries and triggers wallet updates
        settlement_result = run_cash_settlement(
            db=db,
            trip=trip,
            amount=float(payment.amount),
            payment_mode="CASH"
        )
        
        db.commit()
        db.refresh(payment)
        
        # Return payment with settlement info
        return {
            "payment": payment,
            "settlement": settlement_result
        }
