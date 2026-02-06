from pydantic import BaseModel
from typing import Optional


class PaymentStatusResponse(BaseModel):
    """Response with payment status for a trip."""
    payment_id: int
    trip_id: int
    amount: float
    currency: str
    payment_mode: str
    status: str
    confirmed_at: Optional[str] = None
