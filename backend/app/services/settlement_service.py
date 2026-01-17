from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.trips import Trip
from app.models.payments import PlatformWallet, TenantWallet, DriverWallet
from app.models.ledger import PlatformLedger, TenantLedger

PLATFORM_PERCENT = 0.20   # 20%
TENANT_PERCENT = 0.10     # 10%
# Driver gets remaining 70%

def settle_payment(db: Session, trip: Trip, amount: float, payment_mode: str):
    # -----------------------------
    # 1. Calculate split
    # -----------------------------
    platform_fee = round(amount * PLATFORM_PERCENT, 2)
    tenant_fee = round(amount * TENANT_PERCENT, 2)
    driver_earning = round(amount - platform_fee - tenant_fee, 2)

    # -----------------------------
    # 2. Load or create wallets
    # -----------------------------
    platform_wallet = db.query(PlatformWallet).first()
    if not platform_wallet:
        platform_wallet = PlatformWallet(balance=0)
        db.add(platform_wallet)

    tenant_wallet = (
        db.query(TenantWallet)
        .filter(TenantWallet.tenant_id == trip.tenant_id)
        .first()
    )
    if not tenant_wallet:
        tenant_wallet = TenantWallet(
            tenant_id=trip.tenant_id,
            balance=0
        )
        db.add(tenant_wallet)

    driver_wallet = (
        db.query(DriverWallet)
        .filter(DriverWallet.driver_id == trip.driver_id)
        .first()
    )
    if not driver_wallet:
        driver_wallet = DriverWallet(
            driver_id=trip.driver_id,
            balance=0
        )
        db.add(driver_wallet)

    # -----------------------------
    # 3. Apply ONLINE / CASH logic
    # -----------------------------
    if payment_mode == "ONLINE":
        # Money collected by platform
        platform_wallet.balance += amount
        tenant_wallet.balance += tenant_fee
        driver_wallet.balance += driver_earning

    elif payment_mode == "CASH":
        # Money collected by driver
        platform_wallet.balance += platform_fee
        tenant_wallet.balance += tenant_fee
        driver_wallet.balance -= (platform_fee + tenant_fee)

    else:
        raise HTTPException(400, "Invalid payment mode")

    # -----------------------------
    # 4. Ledger entries (audit)
    # -----------------------------
    db.add(PlatformLedger(
        trip_id=trip.trip_id,
        amount=platform_fee,
        entry_type="COMMISSION"
    ))

    db.add(TenantLedger(
        tenant_id=trip.tenant_id,
        trip_id=trip.trip_id,
        amount=tenant_fee,
        entry_type="COMMISSION"
    ))

    # -----------------------------
    # 5. Store earnings on trip
    # -----------------------------
    trip.platform_fee = platform_fee
    trip.driver_earning = driver_earning
