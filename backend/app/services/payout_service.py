"""
Payout Service - CASH-ONLY Settlement System

Driver settles outstanding commission debits immediately.

Settlement Flow (CASH-ONLY):
1) Fetch unsettled DEBIT entries (driver owes commission)
2) Calculate total_amount (sum of debits)
3) settlement_amount = total_amount (driver pays this back)
4) Insert CREDIT settlement entry to offset debits
5) Update wallet: balance += settlement_amount (reduces negative balance)
6) Mark original DEBIT entries as 'settled'
7) Update trip.settlement_status = 'settled'
8) Apply unblocking rule if balance >= MAX_NEGATIVE_LIMIT
9) Commit transaction

IMPORTANT:
- Wallet balance is ALWAYS <= 0 in cash-only system
- Negative balance = driver owes platform
- Settlement CREDIT reduces the debt
- NO positive balance scenario (removed)
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from fastapi import HTTPException, status
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, List, Dict

from app.models.financial import PayoutRequest, PayoutRequestItem
from app.models.ledger import DriverLedger, PlatformLedger, TenantLedger, FleetLedger
from app.models.trips import Trip
from app.models.fleet import DriverProfile
from app.models.payments import DriverWallet

# Import constant
MAX_NEGATIVE_LIMIT = Decimal("-3000")


class PayoutService:
    """Service for driver payout/settlement operations (CASH-ONLY)."""
    
    @staticmethod
    def process_settlement(
        db: Session,
        driver_id: int,
        trip_ids: List[int],
        currency: str = 'INR'
    ) -> Dict:
        """
        Process settlement for CASH-ONLY system (trip-based).
        
        Settlement Flow:
        1) Validate trip_ids not empty
        2) Verify driver exists
        3) Fetch all unsettled DEBIT entries for the given trip_ids
        4) Validate all entries are DEBIT type and currency matches
        5) Calculate settlement_amount = sum of debit amounts
        6) Validate settlement_amount > 0
        7) Lock wallet row (SELECT FOR UPDATE)
        8) Check wallet.balance: if >= 0, throw "Nothing to settle"
        9) Insert CREDIT settlement entry
        10) Update wallet: balance += settlement_amount (reduces debt)
        11) Mark original DEBIT entries as settled
        12) Mark trips as settled
        13) Apply unblocking rule if balance >= MAX_NEGATIVE_LIMIT
        14) Create payout_request and payout_request_item records
        15) Return success response
        
        Args:
            db: Database session (with transaction)
            driver_id: Driver ID
            trip_ids: List of trip IDs to settle
            currency: Currency code
        
        Returns:
            Settlement result dict
        
        Raises:
            HTTPException 400: No entries to settle, nothing to settle, currency mismatch
            HTTPException 404: Driver not found
        """
        if not trip_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="trip_ids cannot be empty"
            )
        
        # Step 1: Verify driver exists
        driver = db.query(DriverProfile).filter(DriverProfile.driver_id == driver_id).first()
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found"
            )
        
        # Step 2: Fetch all unsettled DEBIT entries for these trips
        entries = (
            db.query(DriverLedger)
            .filter(
                DriverLedger.driver_id == driver_id,
                DriverLedger.trip_id.in_(trip_ids),
                DriverLedger.entry_type == 'DEBIT',
                DriverLedger.settlement_status == 'unsettled',
                DriverLedger.currency == currency
            )
            .all()
        )
        
        if not entries:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No unsettled DEBIT entries found for the specified trips"
            )
        
        # Step 3: Validate all entries are same currency (should be by query filter, but be safe)
        currencies = set(e.currency for e in entries)
        if len(currencies) > 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Entries have mixed currencies (should not happen)"
            )
        
        # Step 4: Calculate settlement amount
        settlement_amount = sum(Decimal(str(e.amount)) for e in entries)
        
        if settlement_amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Settlement amount must be positive"
            )
        
        # Step 5: Lock wallet row
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
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Wallet not found for currency {currency}"
            )
        
        current_balance = Decimal(str(wallet.balance))
        
        # Step 6: Check if there's anything to settle
        if current_balance >= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Nothing to settle - wallet balance is {current_balance} (must be negative)"
            )
        
        # Step 7: Create settlement entry (CREDIT to offset debits)
        settlement_entry = DriverLedger(
            driver_id=driver_id,
            trip_id=None,
            currency=currency,
            amount=float(settlement_amount),
            entry_type='CREDIT',
            reason=f"Settlement payment for {len(trip_ids)} trips",
            settlement_status='settled'
        )
        db.add(settlement_entry)
        db.flush()
        
        # Step 8: Update wallet balance (CREDIT increases balance, reduces debt)
        new_balance = current_balance + settlement_amount
        wallet.balance = float(new_balance)
        wallet.updated_on = datetime.now(timezone.utc)
        
        # Step 9: Mark original driver ledger entries as settled
        for entry in entries:
            entry.settlement_status = 'settled'
        
        # Step 9b: Mark corresponding platform/tenant/fleet ledger entries as settled
        # These were created during cash confirmation and need to be marked when driver pays
        platform_entries_settled = 0
        tenant_entries_settled = 0
        fleet_entries_settled = 0
        
        for trip_id in trip_ids:
            # Mark platform ledger entries for this trip as settled
            platform_updated = (
                db.query(PlatformLedger)
                .filter(
                    PlatformLedger.trip_id == trip_id,
                    PlatformLedger.settlement_status == 'unsettled'
                )
                .update({"settlement_status": "settled"})
            )
            platform_entries_settled += platform_updated
            
            # Mark tenant ledger entries for this trip as settled
            tenant_updated = (
                db.query(TenantLedger)
                .filter(
                    TenantLedger.trip_id == trip_id,
                    TenantLedger.settlement_status == 'unsettled'
                )
                .update({"settlement_status": "settled"})
            )
            tenant_entries_settled += tenant_updated
            
            # Mark fleet ledger entries for this trip as settled
            fleet_updated = (
                db.query(FleetLedger)
                .filter(
                    FleetLedger.trip_id == trip_id,
                    FleetLedger.settlement_status == 'unsettled'
                )
                .update({"settlement_status": "settled"})
            )
            fleet_entries_settled += fleet_updated
        
        # Step 10: Mark trips as settled
        settled_trip_count = 0
        for trip_id in trip_ids:
            # Check if ALL ledger entries for this trip are now settled
            unsettled_count = (
                db.query(DriverLedger)
                .filter(
                    DriverLedger.trip_id == trip_id,
        db.flush()
        
        return {
            'success': True,
            'payout_request_id': payout_request.id,
            'settlement_entry_id': settlement_entry.entry_id,
            'driver_id': driver_id,
            'trips_processed': len(trip_ids),
            'trips_settled': settled_trip_count,
            'entries_settled': {
                'driver_ledger': len(entry_ids),
                'platform_ledger': platform_entries_settled,
                'tenant_ledger': tenant_entries_settled,
                'fleet_ledger': fleet_entries_settled,
                'total': len(entry_ids) + platform_entries_settled + tenant_entries_settled + fleet_entries_settled
            },
            'settlement_amount': float(settlement_amount),
            'old_balance': float(current_balance),
            'new_balance': float(new_balance),
            'currency': currency,
            'is_blocked': is_blocked,
            'message': f"Settlement successful: {len(entry_ids)} driver entries settled, {settled_trip_count} trips settled, driver {'blocked' if is_blocked else 'unblocked'}"
        }
        # Step 12: Create payout request record
        from app.models.financial import PayoutRequest, PayoutRequestItem
        
        payout_request = PayoutRequest(
            driver_id=driver_id,
            total_amount=float(settlement_amount),
            payout_type='trip_batch',
            status='completed',
            processed_on=datetime.now(timezone.utc)
            # currency will use default 'INR' from model - database may not have this column yet
        )
        db.add(payout_request)
        db.flush()
        
        # Step 13: Create payout request items for each ledger entry
        entry_ids = [e.entry_id for e in entries]
        for entry_id in entry_ids:
            item = PayoutRequestItem(
                payout_request_id=payout_request.id,
                ledger_id=entry_id
            )
            db.add(item)
        
        db.flush()
        
        return {
            'success': True,
            'payout_request_id': payout_request.id,
            'settlement_entry_id': settlement_entry.entry_id,
            'driver_id': driver_id,
            'trips_processed': len(trip_ids),
            'trips_settled': settled_trip_count,
            'entries_settled': len(entry_ids),
            'settlement_amount': float(settlement_amount),
            'old_balance': float(current_balance),
            'new_balance': float(new_balance),
            'currency': currency,
            'is_blocked': is_blocked,
            'message': f"Settlement successful: {len(entry_ids)} entries settled, {settled_trip_count} trips settled, driver {'blocked' if is_blocked else 'unblocked'}"
        }
    
    @staticmethod
    def get_payout_history(
        db: Session,
        driver_id: int,
        page: int = 1,
        page_size: int = 20
    ) -> Dict:
        """
        Get driver's payout request history.
        """
        query = (
            db.query(PayoutRequest)
            .filter(PayoutRequest.driver_id == driver_id)
        )
        
        total = query.count()
        
        payouts = (
            query
            .order_by(PayoutRequest.created_on.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        
        return {
            'payouts': payouts,
            'total': total,
            'page': page,
            'page_size': page_size
        }
    
    @staticmethod
    def get_payout_details(
        db: Session,
        driver_id: int,
        payout_id: int
    ) -> Dict:
        """
        Get payout request details with items.
        """
        payout = (
            db.query(PayoutRequest)
            .filter(
                PayoutRequest.id == payout_id,
                PayoutRequest.driver_id == driver_id
            )
            .first()
        )
        
        if not payout:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payout request not found"
            )
        
        items = (
            db.query(PayoutRequestItem)
            .filter(PayoutRequestItem.payout_request_id == payout_id)
            .all()
        )
        
        ledger_ids = [item.ledger_id for item in items]
        ledger_entries = (
            db.query(DriverLedger)
            .filter(DriverLedger.entry_id.in_(ledger_ids))
            .all()
        )
        
        return {
            'payout': payout,
            'items': items,
            'ledger_entries': ledger_entries
        }
