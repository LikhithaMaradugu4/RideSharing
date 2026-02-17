from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from decimal import Decimal

from app.models.trips import Trip
from app.models.payments import Payment, DriverWallet
from app.models.ledger import DriverLedger, PlatformLedger, TenantLedger, FleetLedger
from app.models.fleet import DriverProfile
from app.models.vehicle import Vehicle


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
        2. Get fleet_id from vehicle (if applicable)
        3. Lock driver wallet (SELECT FOR UPDATE)
        4. Insert DEBIT ledger entries for driver (commission amounts)
        5. Insert CREDIT ledger entries for platform/tenant/fleet (receivables)
        6. Update wallet: balance -= total_commission
        7. Update trip: payment_status='paid', settlement_status='unsettled'
        8. Update payment record status
        9. Apply blocking rule if balance < MAX_NEGATIVE_LIMIT
        10. Commit transaction
        
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
        platform_fee = Decimal(str(trip.platform_fee or 0))
        tenant_commission = Decimal(str(trip.tenant_commission or 0))
        fleet_commission = Decimal(str(trip.fleet_commission or 0))

        total_commission = platform_fee + tenant_commission + fleet_commission
        currency = trip.currency or "INR"

        # 3️⃣ Get fleet_id from vehicle (if applicable)
        fleet_id = None
        if trip.vehicle_id:
            vehicle = db.query(Vehicle).filter(Vehicle.vehicle_id == trip.vehicle_id).first()
            if vehicle and vehicle.fleet_id:
                fleet_id = vehicle.fleet_id

        # 4️⃣ Lock driver wallet row (SELECT FOR UPDATE)
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

        # 5️⃣ Insert DEBIT ledger entries for DRIVER (commission amounts)
        # ❌ DO NOT INSERT EARNING CREDIT ENTRY - driver keeps cash physically

        if platform_fee > 0:
            db.add(DriverLedger(
                driver_id=driver_id,
                trip_id=trip.trip_id,
                currency=currency,
                amount=float(platform_fee),
                entry_type="DEBIT",
                reason=f"Platform commission for trip {trip.trip_id}",
                settlement_status="unsettled"
            ))

        if tenant_commission > 0:
            db.add(DriverLedger(
                driver_id=driver_id,
                trip_id=trip.trip_id,
                currency=currency,
                amount=float(tenant_commission),
                entry_type="DEBIT",
                reason=f"Tenant commission for trip {trip.trip_id}",
                settlement_status="unsettled"
            ))

        if fleet_commission > 0:
            db.add(DriverLedger(
                driver_id=driver_id,
                trip_id=trip.trip_id,
                currency=currency,
                amount=float(fleet_commission),
                entry_type="DEBIT",
                reason=f"Fleet commission for trip {trip.trip_id}",
                settlement_status="unsettled"
            ))

        # 6️⃣ Insert CREDIT ledger entries for Platform/Tenant/Fleet (RECEIVABLES)
        # These track amounts owed TO these entities BY the driver
        # settlement_status tracks whether driver has paid this back

        if platform_fee > 0:
            db.add(PlatformLedger(
                trip_id=trip.trip_id,
                currency=currency,
                amount=float(platform_fee),
                entry_type="CREDIT",
                reason=f"Platform commission receivable for trip {trip.trip_id}"
            ))

        if tenant_commission > 0 and trip.tenant_id:
            db.add(TenantLedger(
                tenant_id=trip.tenant_id,
                trip_id=trip.trip_id,
                currency=currency,
                amount=float(tenant_commission),
                entry_type="CREDIT",
                reason=f"Tenant commission receivable for trip {trip.trip_id}"
            ))

        if fleet_commission > 0 and fleet_id:
            db.add(FleetLedger(
                fleet_id=fleet_id,
                trip_id=trip.trip_id,
                currency=currency,
                amount=float(fleet_commission),
                entry_type="CREDIT",
                reason=f"Fleet commission receivable for trip {trip.trip_id}"
            ))

        # 7️⃣ Update wallet balance (driver owes commission - goes negative)
        wallet.balance = float(Decimal(str(wallet.balance)) - total_commission)

        # 8️⃣ Update trip status
        trip.payment_status = "paid"
        trip.settlement_status = "unsettled"

        # 9️⃣ Update payment record if exists
        payment = PaymentService.get_payment_for_trip(db, trip_id)
        if payment:
            payment.status = "SUCCESS"
            payment.confirmed_at = datetime.now(timezone.utc)

        # 🔟 Apply blocking rule if balance exceeds limit
        if Decimal(str(wallet.balance)) < MAX_NEGATIVE_LIMIT:
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
            "currency": currency,
            "ledger_entries_created": {
                "driver_ledger": True,
                "platform_ledger": platform_fee > 0,
                "tenant_ledger": tenant_commission > 0 and trip.tenant_id is not None,
                "fleet_ledger": fleet_commission > 0 and fleet_id is not None
            }
        }
