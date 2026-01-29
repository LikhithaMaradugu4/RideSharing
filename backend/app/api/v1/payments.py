"""from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.api.deps.auth import get_current_user
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["Payments"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/trip/{trip_id}")
def pay_for_trip(
    trip_id: int,
    daGetta: dict,  # {"payment_mode": "ONLINE", "amount": 120}
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    payment = PaymentService.create_payment(
        db=db,
        trip_id=trip_id,
        rider_id=current_user.user_id,
        payment_mode=data["payment_mode"],
        amount=data["amount"]
    )

    return {
        "payment_id": payment.payment_id,
        "status": payment.status
    }
"""