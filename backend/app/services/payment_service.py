from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime, timezone

from app.models.trips import Trip
from app.models.payments import Payment
from app.services.settlement_service import settle_payment

class PaymentService:

    @staticmethod
    def create_payment(
        db: Session,
        trip_id: int,
        rider_id: int,
        payment_mode: str,
        amount: float
    ):
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

        # 2. Create payment record
        payment = Payment(
            trip_id=trip.trip_id,
            amount=amount,
            currency="INR",
            payment_mode=payment_mode,
            status="SUCCESS",
            created_by=rider_id,
            created_on=datetime.now(timezone.utc)
        )
        db.add(payment)

        # 3. Update trip payment status
        trip.payment_status = "SUCCESS"

        # 4. Settlement (THIS IS THE CORE)
        settle_payment(
            db=db,
            trip=trip,
            amount=amount,
            payment_mode=payment_mode
        )

        db.commit()
        db.refresh(payment)

        return payment
