from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from decimal import Decimal

from app.models.trips import Trip
from app.models.payments import Payment, DriverWallet
from app.models.ledger import DriverLedger
from app.models.fleet import DriverProfile


# =============================================================================
# CASH-ONLY PAYMENT POLICY
# =============================================================================
# Online payments are disabled. Only CASH payments are supported.
# Driver receives full fare physically in cash from rider.
# Ledger tracks ONLY commission DEBIT entries (no earning CREDIT).
# Wallet balance becomes negative (driver owes commission).
# Negative balance > MAX_NEGATIVE_LIMIT triggers blocking.
# =============================================================================


ALLOWED_PAYMENT_MODES = ["CASH"]
MAX_NEGATIVE_LIMIT = Decimal("-3000")



class PaymentService:

    # -------------------------------------------------------------------------
    # Auto-create payment record when trip completes
    # -------------------------------------------------------------------------
    @staticmethod
    def auto_create_cash_payment(
        db: Session,
        trip: Trip
    ) -> Payment:

        existing_payment = (
            db.query(Payment)
            .filter(Payment.trip_id == trip.trip_id)
            .first()
        )

        if existing_payment:
            return existing_payment

        currency = trip.currency or "INR"
        amount = float(trip.fare_amount or 0)

        payment = Payment(
            trip_id=trip.trip_id,
            amount=amount,
            currency=currency,
            payment_mode="CASH",
            status="PENDING_CASH",
            created_by=trip.driver_id,
            created_on=datetime.now(timezone.utc)
        )

        db.add(payment)
        db.flush()

        return payment

    # -------------------------------------------------------------------------
    # Get payment record
    # -------------------------------------------------------------------------
    @staticmethod
    def get_payment_for_trip(
        db: Session,
        trip_id: int
    ) -> Optional[Payment]:

        return (
            db.query(Payment)
            .filter(Payment.trip_id == trip_id)
            .first()
        )

    # -------------------------------------------------------------------------
    # Confirm CASH payment (Core Financial Logic)
    # -------------------------------------------------------------------------
    @staticmethod
    def confirm_cash_received(
        db: Session,
        trip_id: int,
        driver_id: int
    ) -> Dict[str, Any]:
        """
        Confirm cash payment received from rider.
        
        CASH-ONLY LOGIC:
        1. Validate trip (exists, status=COMPLETED, mode=CASH, not already paid)
        2. Insert DEBIT ledger entries for commissions ONLY
        3. Update wallet: balance -= total_commission
        4. Update trip: payment_status='paid', settlement_status='unsettled'
        5. Apply blocking rule if balance < MAX_NEGATIVE_LIMIT
        
        NO EARNING CREDIT ENTRY - driver keeps cash physically.
        """

        # 1️⃣ Validate trip
        trip = (
            db.query(Trip)
            .filter(
                Trip.trip_id == trip_id,
                Trip.driver_id == driver_id
            )
            .first()
        )

        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found")

        if trip.status != "COMPLETED":
            raise HTTPException(
                status_code=400,
                detail=f"Cannot confirm payment for trip with status '{trip.status}'"
            )

        if trip.payment_mode != "CASH":
            raise HTTPException(status_code=400, detail="Trip is not cash payment")

        if trip.payment_status == "paid":
            raise HTTPException(status_code=400, detail="Payment already confirmed")

        # 2️⃣ Get commission values from trip
        platform_fee = Decimal(trip.platform_fee or 0)
        tenant_commission = Decimal(trip.tenant_commission or 0)
        fleet_commission = Decimal(trip.fleet_commission or 0)

        total_commission = (
            platform_fee +
            tenant_commission +
            fleet_commission
        )

        currency = trip.currency or "INR"

        # 3️⃣ Lock driver wallet row (SELECT FOR UPDATE)
        wallet = (
            db.query(DriverWallet)
            .filter(
                DriverWallet.driver_id == driver_id,
                DriverWallet.currency == currency
            )
            .with_for_update()
            .first()
        )

        if not wallet:
            # Create wallet if doesn't exist
            wallet = DriverWallet(
                driver_id=driver_id,
                currency=currency,
                balance=Decimal("0")
            )
            db.add(wallet)
            db.flush()
            # Re-lock after creation
            wallet = (
                db.query(DriverWallet)
                .filter(
                    DriverWallet.driver_id == driver_id,
                    DriverWallet.currency == currency
                )
                .with_for_update()
                .first()
            )

        # 4️⃣ Insert DEBIT ledger entries (commission only)
        # ❌ DO NOT INSERT EARNING CREDIT ENTRY

        if platform_fee > 0:
            db.add(DriverLedger(
                driver_id=driver_id,
                trip_id=trip.trip_id,
                currency=currency,
                amount=platform_fee,
                entry_type="DEBIT",
                reason=f"Platform commission for trip {trip.trip_id}",
                settlement_status="unsettled"
            ))

        if tenant_commission > 0:
            db.add(DriverLedger(
                driver_id=driver_id,
                trip_id=trip.trip_id,
                currency=currency,
                amount=tenant_commission,
                entry_type="DEBIT",
                reason=f"Tenant commission for trip {trip.trip_id}",
                settlement_status="unsettled"
            ))

        if fleet_commission > 0:
            db.add(DriverLedger(
                driver_id=driver_id,
                trip_id=trip.trip_id,
                currency=currency,
                amount=fleet_commission,
                entry_type="DEBIT",
                reason=f"Fleet commission for trip {trip.trip_id}",
                settlement_status="unsettled"
            ))

        # 5️⃣ Update wallet balance (driver owes commission)
        wallet.balance -= total_commission

        # 6️⃣ Update trip status
        trip.payment_status = "paid"
        trip.settlement_status = "unsettled"

        # Update payment record if exists
        payment = PaymentService.get_payment_for_trip(db, trip_id)
        if payment:
            payment.status = "SUCCESS"
            payment.confirmed_at = datetime.now(timezone.utc)

        # 7️⃣ Apply blocking rule
        if wallet.balance < MAX_NEGATIVE_LIMIT:
            driver_profile = (
                db.query(DriverProfile)
                .filter(DriverProfile.driver_id == driver_id)
                .first()
            )
            if driver_profile:
                driver_profile.is_blocked = True
                driver_profile.blocked_reason = f"Commission limit exceeded ({wallet.balance} {currency})"

        db.commit()

        return {
            "success": True,
            "message": "Cash payment confirmed",
            "trip_id": trip.trip_id,
            "payment_status": trip.payment_status,
            "settlement_status": trip.settlement_status,
            "commission": {
                "platform_fee": float(platform_fee),
                "tenant_commission": float(tenant_commission),
                "fleet_commission": float(fleet_commission),
                "total_commission": float(total_commission)
            },
            "wallet_balance": float(wallet.balance),
            "currency": currency
        }
