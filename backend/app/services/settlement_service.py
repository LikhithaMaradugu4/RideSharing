from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime, timezone

from app.models.trips import Trip
from app.models.payments import PlatformWallet, TenantWallet, DriverWallet
from app.models.ledger import PlatformLedger, TenantLedger

PLATFORM_PERCENT = 0.20   # 20%
TENANT_PERCENT = 0.10     # 10%
# Driver gets remaining 70%

def settle_payment(db: Session, trip: Trip, amount: float, payment_mode: str):
    # -----------------------------
    # 0. Get currency from trip
    # -----------------------------
    currency = trip.currency if hasattr(trip, 'currency') else "INR"
    
    # -----------------------------
    # 1. Calculate split
    # -----------------------------
    platform_fee = round(amount * PLATFORM_PERCENT, 2)
    tenant_fee = round(amount * TENANT_PERCENT, 2)
    driver_earning = round(amount - platform_fee - tenant_fee, 2)

    # -----------------------------
    # 2. Load or create wallets (multi-currency)
    # -----------------------------
    platform_wallet = (
        db.query(PlatformWallet)
        .filter(PlatformWallet.currency == currency)
        .first()
    )
    if not platform_wallet:
        platform_wallet = PlatformWallet(
            currency=currency,
            balance=0
        )
        db.add(platform_wallet)

    tenant_wallet = (
        db.query(TenantWallet)
        .filter(
            TenantWallet.tenant_id == trip.tenant_id,
            TenantWallet.currency == currency
        )
        .first()
    )
    if not tenant_wallet:
        tenant_wallet = TenantWallet(
            tenant_id=trip.tenant_id,
            currency=currency,
            balance=0
        )
        db.add(tenant_wallet)

    driver_wallet = (
        db.query(DriverWallet)
        .filter(
            DriverWallet.driver_id == trip.driver_id,
            DriverWallet.currency == currency
        )
        .first()
    )
    if not driver_wallet:
        driver_wallet = DriverWallet(
            driver_id=trip.driver_id,
            currency=currency,
            balance=0
        )
        db.add(driver_wallet)

    # -----------------------------
    # 3. Apply ONLINE / CASH logic
    # -----------------------------
    if payment_mode == "ONLINE":
        # Money collected by platform
        platform_wallet.balance += amount
        platform_wallet.updated_on = datetime.now(timezone.utc)
        
        tenant_wallet.balance += tenant_fee
        tenant_wallet.updated_on = datetime.now(timezone.utc)
        
        driver_wallet.balance += driver_earning
        driver_wallet.updated_on = datetime.now(timezone.utc)

    elif payment_mode == "CASH":
        # Money collected by driver
        platform_wallet.balance += platform_fee
        platform_wallet.updated_on = datetime.now(timezone.utc)
        
        tenant_wallet.balance += tenant_fee
        tenant_wallet.updated_on = datetime.now(timezone.utc)
        
        driver_wallet.balance -= (platform_fee + tenant_fee)
        driver_wallet.updated_on = datetime.now(timezone.utc)

    else:
        raise HTTPException(400, "Invalid payment mode")

    # -----------------------------
    # 4. Ledger entries (audit) with currency
    # -----------------------------
    db.add(PlatformLedger(
        trip_id=trip.trip_id,
        currency=currency,
        amount=platform_fee,
        entry_type="CREDIT",
        reason=f"Commission from trip {trip.trip_id}"
    ))

    db.add(TenantLedger(
        tenant_id=trip.tenant_id,
        trip_id=trip.trip_id,
        currency=currency,
        amount=tenant_fee,
        entry_type="CREDIT",
        reason=f"Commission from trip {trip.trip_id}"
    ))

    # -----------------------------
    # 5. Store earnings on trip
    # -----------------------------
    trip.platform_fee = platform_fee
    trip.driver_earning = driver_earning
