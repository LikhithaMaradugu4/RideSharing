from pydantic import BaseModel
from typing import Optional, Dict, Any


class PaymentWebhookRequest(BaseModel):
    """Request payload from payment gateway webhook."""
    gateway_name: str  # "razorpay", "stripe", etc.
    gateway_order_id: str
    gateway_payment_id: str
    gateway_signature: str
    status: str  # "SUCCESS" or "FAILED"
    payload: Optional[Dict[str, Any]] = None  # Full webhook payload


class PaymentWebhookResponse(BaseModel):
    """Response after processing webhook."""
    payment_id: int
    trip_id: int
    status: str
    message: str


class CashReceivedRequest(BaseModel):
    """Request from driver confirming cash payment received."""
    pass  # No body needed, driver_id comes from auth


class CashReceivedResponse(BaseModel):
    """Response after driver confirms cash payment."""
    payment_id: int
    trip_id: int
    status: str
    confirmed_by_driver_id: int
    confirmed_at: str  # ISO timestamp
    message: str
