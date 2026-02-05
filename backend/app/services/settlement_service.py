"""
Settlement Service - CASH-ONLY Fare Split and Ledger Entries

This service handles:
1. Hybrid fare split calculation (using commission_config.py)
2. Ledger entries for platform, tenant, fleet, driver
3. Trip closure (mark as PAID)

Wallet updates are handled by DB triggers (NOT in this file).

CASH Payment Flow:
- Driver collects full fare from rider
- Settlement creates ledger entries:
  - Platform: CREDIT (platform earns commission)
  - Tenant: CREDIT (tenant earns commission)
  - Fleet: CREDIT (fleet earns commission, if applicable)
  - Driver: CREDIT (driver earning) + DEBIT (commissions owed)
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from app.models.trips import Trip
from app.models.fleet import FleetDriver
from app.models.ledger import PlatformLedger, TenantLedger, FleetLedger, DriverLedger
from app.core.commission_config import calculate_fare_split


def get_driver_fleet_id(db: Session, driver_id: int) -> Optional[int]:
    """
    Get the fleet_id for a driver if they belong to a fleet.
    
    Returns None if driver is independent (no fleet).
    """
    fleet_driver = (
        db.query(FleetDriver)
        .filter(
            FleetDriver.driver_id == driver_id,
            FleetDriver.end_date.is_(None)  # Active association
        )
        .first()
    )
    
    if fleet_driver:
        return fleet_driver.fleet_id
    
    return None


def run_cash_settlement(
    db: Session, 
    trip: Trip, 
    amount: float, 
    payment_mode: str
) -> dict:
    """
    Run settlement for CASH payment.
    
    This is the main entry point for settlement.
    ONLY runs when:
    - payment.status == SUCCESS
    - payment.payment_mode == CASH
    
    Args:
        db: Database session
        trip: Trip object (must have driver_id, tenant_id set)
        amount: Payment amount (fare)
        payment_mode: Must be "CASH"
    
    Returns:
        Settlement result dict with fare split details
    """
    # Validate payment mode
    if payment_mode != "CASH":
        raise HTTPException(400, "Settlement only supported for CASH payments")
    
    # Get currency
    currency = trip.currency if hasattr(trip, 'currency') and trip.currency else "INR"
    
    # Check if driver belongs to a fleet
    fleet_id = get_driver_fleet_id(db, trip.driver_id)
    has_fleet = fleet_id is not None
    
    # Calculate fare split using hybrid formula
    fare_split = calculate_fare_split(
        final_fare=Decimal(str(amount)),
        has_fleet=has_fleet
    )
    
    # Insert ledger entries
    _insert_ledger_entries(
        db=db,
        trip=trip,
        fare_split=fare_split,
        currency=currency,
        fleet_id=fleet_id
    )
    
    # Store earnings on trip
    trip.platform_fee = float(fare_split["platform_commission"])
    trip.driver_earning = float(fare_split["driver_earning"])
    
    # Mark trip as PAID (final state after settlement)
    trip.status = "PAID"
    trip.payment_status = "SUCCESS"
    
    return {
        "trip_id": trip.trip_id,
        "fare_amount": float(fare_split["total"]),
        "platform_commission": float(fare_split["platform_commission"]),
        "tenant_commission": float(fare_split["tenant_commission"]),
        "fleet_commission": float(fare_split["fleet_commission"]),
        "driver_earning": float(fare_split["driver_earning"]),
        "fleet_id": fleet_id,
        "currency": currency,
        "status": "SETTLED"
    }


def _insert_ledger_entries(
    db: Session,
    trip: Trip,
    fare_split: dict,
    currency: str,
    fleet_id: Optional[int]
):
    """
    Insert all ledger entries for a settled payment.
    
    For CASH payments:
    - Platform: CREDIT (earns commission)
    - Tenant: CREDIT (earns commission)
    - Fleet: CREDIT (earns commission, if applicable)
    - Driver: 
      - CREDIT driver_earning
      - DEBIT platform_commission
      - DEBIT tenant_commission
      - DEBIT fleet_commission (if applicable)
    
    Wallet updates are handled by AFTER INSERT triggers.
    """
    trip_id = trip.trip_id
    driver_id = trip.driver_id
    tenant_id = trip.tenant_id
    
    platform_commission = fare_split["platform_commission"]
    tenant_commission = fare_split["tenant_commission"]
    fleet_commission = fare_split["fleet_commission"]
    driver_earning = fare_split["driver_earning"]
    
    # 1. Platform Ledger - CREDIT
    if platform_commission > 0:
        db.add(PlatformLedger(
            trip_id=trip_id,
            currency=currency,
            amount=float(platform_commission),
            entry_type="CREDIT",
            reason=f"Commission from trip {trip_id} (CASH)"
        ))
    
    # 2. Tenant Ledger - CREDIT
    if tenant_commission > 0 and tenant_id:
        db.add(TenantLedger(
            tenant_id=tenant_id,
            trip_id=trip_id,
            currency=currency,
            amount=float(tenant_commission),
            entry_type="CREDIT",
            reason=f"Commission from trip {trip_id} (CASH)"
        ))
    
    # 3. Fleet Ledger - CREDIT (only if driver has fleet)
    if fleet_commission > 0 and fleet_id:
        db.add(FleetLedger(
            fleet_id=fleet_id,
            trip_id=trip_id,
            currency=currency,
            amount=float(fleet_commission),
            entry_type="CREDIT",
            reason=f"Commission from trip {trip_id} (CASH)"
        ))
    
    # 4. Driver Ledger entries
    # For CASH: Driver collected full amount, so we record:
    # - CREDIT: Driver earning (their share)
    # - DEBIT: Each commission (amounts they owe)
    
    # CREDIT: Driver earning
    if driver_earning > 0:
        db.add(DriverLedger(
            driver_id=driver_id,
            trip_id=trip_id,
            currency=currency,
            amount=float(driver_earning),
            entry_type="CREDIT",
            reason=f"Earning from trip {trip_id}"
        ))
    
    # DEBIT: Platform commission (driver owes platform)
    if platform_commission > 0:
        db.add(DriverLedger(
            driver_id=driver_id,
            trip_id=trip_id,
            currency=currency,
            amount=float(platform_commission),
            entry_type="DEBIT",
            reason=f"Platform commission for trip {trip_id}"
        ))
    
    # DEBIT: Tenant commission (driver owes tenant)
    if tenant_commission > 0:
        db.add(DriverLedger(
            driver_id=driver_id,
            trip_id=trip_id,
            currency=currency,
            amount=float(tenant_commission),
            entry_type="DEBIT",
            reason=f"Tenant commission for trip {trip_id}"
        ))
    
    # DEBIT: Fleet commission (driver owes fleet, if applicable)
    if fleet_commission > 0 and fleet_id:
        db.add(DriverLedger(
            driver_id=driver_id,
            trip_id=trip_id,
            currency=currency,
            amount=float(fleet_commission),
            entry_type="DEBIT",
            reason=f"Fleet commission for trip {trip_id}"
        ))
    
    # Flush to ensure triggers fire
    db.flush()


# Legacy function name for backward compatibility
def settle_payment(db: Session, trip: Trip, amount: float, payment_mode: str):
    """
    Legacy wrapper for run_cash_settlement.
    
    Kept for backward compatibility with existing code.
    """
    return run_cash_settlement(db, trip, amount, payment_mode)
