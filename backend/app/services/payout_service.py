"""
Payout Service - CASH-ONLY Settlement System

Driver settles outstanding commission debits immediately.

Settlement Flow (CASH-ONLY):
1) Fetch unsettled DEBIT entries (driver owes commission)
2) Calculate total_amount (sum of debits - should be positive)
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
from app.models.ledger import DriverLedger
from app.models.trips import Trip
from app.models.fleet import DriverProfile
from app.models.payments import DriverWallet

# Import constant
MAX_NEGATIVE_LIMIT = Decimal("-3000")


class PayoutService:
    """Service for driver payout/settlement operations."""
    
    @staticmethod
    def create_payout_request(
        db: Session,
        driver_id: int,
        payout_type: str,
        trip_ids: Optional[List[int]] = None,
        currency: str = 'INR'
    ) -> Dict:
        """
        Create and execute immediate payout/settlement.
        
        Args:
            db: Database session
            driver_id: Driver ID
            payout_type: 'single' | 'batch' | 'full'
            trip_ids: Optional list of trip IDs (for single/batch)
            currency: Currency code
        
        Returns:
            Settlement result dict
        """
        # Validate payout type
        if payout_type not in ['single', 'batch', 'full']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="payout_type must be 'single', 'batch', or 'full'"
            )
        
        # For single, exactly one trip_id required
        if payout_type == 'single':
            if not trip_ids or len(trip_ids) != 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Single settlement requires exactly one trip_id"
                )
        
        # For batch, at least one trip_id required
        if payout_type == 'batch':
            if not trip_ids or len(trip_ids) == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Batch settlement requires at least one trip_id"
                )
        
        # Step 1: Fetch eligible ledger entries
        entries = LedgerService.get_unsettled_entries(
            db=db,
            driver_id=driver_id,
            currency=currency,
            trip_ids=trip_ids if payout_type != 'full' else None
        )
        
        if not entries:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No unsettled entries found for the specified criteria"
            )
        
        # Verify all entries are same currency
        currencies = set(e.currency for e in entries)
        if len(currencies) > 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot mix currencies in one settlement. Create separate requests."
            )
        
        # Step 2-3: Lock driver wallet row
        wallet = WalletService.get_driver_wallet_for_update(db, driver_id, currency)
        current_balance = Decimal(str(wallet.balance))
        
        # Step 4: Calculate total amount (net of credits and debits)
        total_amount = LedgerService.calculate_net_amount(entries)
        
        # Step 5: Insert payout_request (status = 'completed' for immediate settlement)
        payout = PayoutRequest(
            driver_id=driver_id,
            total_amount=float(abs(total_amount)),
            currency=currency,
            payout_type=payout_type,
            status='completed',
            processed_on=datetime.now(timezone.utc)
        )
        db.add(payout)
        db.flush()
        
        # Step 6: Insert payout_request_item rows
        entry_ids = []
        for entry in entries:
            item = PayoutRequestItem(
                payout_request_id=payout.id,
                ledger_id=entry.entry_id
            )
            db.add(item)
            entry_ids.append(entry.entry_id)
        
        # Step 7: Insert settlement ledger entry
        # If balance > 0 (platform owes driver): DEBIT to reduce balance
        # If balance < 0 (driver owes platform): CREDIT to increase balance
        if total_amount > 0:
            # Platform owes driver - DEBIT settlement entry
            settlement_entry = DriverLedger(
                driver_id=driver_id,
                trip_id=None,
                currency=currency,
                amount=float(abs(total_amount)),
                entry_type='DEBIT',
                reason=f"Settlement payout #{payout.id}",
                settlement_status='settled'
            )
            db.add(settlement_entry)
            
            # Debit from wallet (driver received money)
            new_balance = current_balance - abs(total_amount)
        else:
            # Driver owes platform - CREDIT settlement entry
            settlement_entry = DriverLedger(
                driver_id=driver_id,
                trip_id=None,
                currency=currency,
                amount=float(abs(total_amount)),
                entry_type='CREDIT',
                reason=f"Settlement payment #{payout.id}",
                settlement_status='settled'
            )
            db.add(settlement_entry)
            
            # Credit to wallet (driver paid money)
            new_balance = current_balance + abs(total_amount)
        
        # Step 8: Update driver_wallet.balance
        wallet.balance = float(new_balance)
        wallet.updated_on = datetime.now(timezone.utc)
        
        # Step 9: Mark selected ledger entries as 'settled'
        LedgerService.mark_entries_settled(db, entry_ids)
        
        # Step 10: Update trip.settlement_status if fully settled
        trip_ids_to_update = set(e.trip_id for e in entries if e.trip_id)
        for trip_id in trip_ids_to_update:
            # Check if all entries for this trip are settled
            unsettled_count = (
                db.query(DriverLedger)
                .filter(
                    DriverLedger.trip_id == trip_id,
                    DriverLedger.settlement_status == 'unsettled'
                )
                .count()
            )
            
            if unsettled_count == 0:
                db.query(Trip).filter(Trip.trip_id == trip_id).update(
                    {'settlement_status': 'settled'},
                    synchronize_session=False
                )
        
        # Step 11: Check blocking rule
        is_blocked = new_balance < MAX_NEGATIVE_LIMIT
        
        # Flush all changes
        db.flush()
        
        return {
            'success': True,
            'payout_id': payout.id,
            'total_amount': total_amount,
            'currency': currency,
            'trips_settled': len(trip_ids_to_update),
            'ledger_entries_settled': len(entry_ids),
            'new_wallet_balance': new_balance,
            'is_blocked': is_blocked,
            'message': f"Successfully settled {len(entry_ids)} entries"
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
