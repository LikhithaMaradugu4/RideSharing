"""
Payment Routes - Payment processing endpoints.

Endpoints:
- POST /payments/webhook - Process payment gateway webhook
- POST /payments/{payment_id}/cash-received - Driver confirms cash payment
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.api.deps.jwt_auth import get_current_user
from app.core.database import SessionLocal
from app.services.payment_service import PaymentService
from app.schemas.payment import (
    PaymentWebhookRequest,
    PaymentWebhookResponse,
    CashReceivedRequest,
    CashReceivedResponse
)

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/webhook", response_model=PaymentWebhookResponse)
def payment_webhook(
    request: PaymentWebhookRequest,
    db: Session = Depends(get_db)
):
    """
    Process payment gateway webhook.
    
    Called by payment gateway (Razorpay, Stripe, etc.) when payment status changes.
    
    Phase 2a of payment flow (ONLINE payments):
    - Verifies signature
    - Checks idempotency using gateway_payment_id
    - Updates payment.status = SUCCESS or FAILED
    - Stores gateway references
    - NO wallet updates
    - NO ledger entries
    
    Returns:
        Payment status update confirmation
    """
    payment = PaymentService.process_webhook(
        db=db,
        gateway_name=request.gateway_name,
        gateway_order_id=request.gateway_order_id,
        gateway_payment_id=request.gateway_payment_id,
        gateway_signature=request.gateway_signature,
        webhook_status=request.status,
        payload=request.payload
    )
    
    return PaymentWebhookResponse(
        payment_id=payment.payment_id,
        trip_id=payment.trip_id,
        status=payment.status,
        message=f"Payment {payment.status.lower()}"
    )


@router.post("/{payment_id}/cash-received", response_model=CashReceivedResponse)
def confirm_cash_received(
    payment_id: int,
    request: CashReceivedRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Driver confirms cash payment received.
    
    Only the driver assigned to the trip can call this endpoint.
    
    Phase 2b of payment flow (CASH payments):
    - Validates driver is assigned to the trip
    - Updates payment.status = SUCCESS
    - Records confirmed_by_driver_id
    - Timestamps confirmation
    - NO wallet updates
    - NO ledger entries
    
    Returns:
        Payment confirmation details
    """
    driver_id = current_user.get("user_id")
    
    payment = PaymentService.confirm_cash_received(
        db=db,
        payment_id=payment_id,
        driver_id=driver_id
    )
    
    return CashReceivedResponse(
        payment_id=payment.payment_id,
        trip_id=payment.trip_id,
        status=payment.status,
        confirmed_by_driver_id=payment.confirmed_by_driver_id,
        confirmed_at=payment.confirmed_at.isoformat(),
        message="Cash payment confirmed"
    )
