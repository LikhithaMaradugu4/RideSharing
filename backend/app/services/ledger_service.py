"""
Ledger Service - Handle all ledger entries (CREDIT/DEBIT).

Ledger entries track all financial transactions.
Wallet updates are done via wallet_service (not DB triggers).

settlement_status:
- 'unsettled': Not yet settled
- 'settled': Already settled via payout request
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from fastapi import HTTPException, status
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, List, Dict

from app.models.ledger import PlatformLedger, TenantLedger, FleetLedger, DriverLedger
from app.models.trips import Trip
from app.services.wallet_service import WalletService


class LedgerService:
    """Service for ledger operations."""
    
    # ============================================
    # PLATFORM LEDGER
    # ============================================
    
    @staticmethod
    def create_platform_entry(
        db: Session,
        trip_id: int,
        amount: Decimal,
        entry_type: str,
        reason: str,
        currency: str = 'INR'
    ) -> PlatformLedger:
        """Create platform ledger entry and update wallet."""
        entry = PlatformLedger(
            trip_id=trip_id,
            currency=currency,
            amount=float(amount),
            entry_type=entry_type,
            reason=reason
        )
        db.add(entry)
        
        # Update platform wallet
        operation = 'credit' if entry_type == 'CREDIT' else 'debit'
        WalletService.update_platform_wallet(db, amount, operation, currency)
        
        return entry
    
    # ============================================
    # TENANT LEDGER
    # ============================================
    
    @staticmethod
    def create_tenant_entry(
        db: Session,
        tenant_id: int,
        trip_id: int,
        amount: Decimal,
        entry_type: str,
        reason: str,
        currency: str = 'INR'
    ) -> TenantLedger:
        """Create tenant ledger entry and update wallet."""
        entry = TenantLedger(
            tenant_id=tenant_id,
            trip_id=trip_id,
            currency=currency,
            amount=float(amount),
            entry_type=entry_type,
            reason=reason
        )
        db.add(entry)
        
        # Update tenant wallet
        operation = 'credit' if entry_type == 'CREDIT' else 'debit'
        WalletService.update_tenant_wallet(db, tenant_id, amount, operation, currency)
        
        return entry
    
    # ============================================
    # FLEET LEDGER
    # ============================================
    
    @staticmethod
    def create_fleet_entry(
        db: Session,
        fleet_id: int,
        trip_id: int,
        amount: Decimal,
        entry_type: str,
        reason: str,
        currency: str = 'INR'
    ) -> FleetLedger:
        """Create fleet ledger entry and update wallet."""
        entry = FleetLedger(
            fleet_id=fleet_id,
            trip_id=trip_id,
            currency=currency,
            amount=float(amount),
            entry_type=entry_type,
            reason=reason
        )
        db.add(entry)
        
        # Update fleet wallet
        operation = 'credit' if entry_type == 'CREDIT' else 'debit'
        WalletService.update_fleet_wallet(db, fleet_id, amount, operation, currency)
        
        return entry
    
    # ============================================
    # DRIVER LEDGER
    # ============================================
    
    @staticmethod
    def create_driver_entry(
        db: Session,
        driver_id: int,
        trip_id: Optional[int],
        amount: Decimal,
        entry_type: str,
        reason: str,
        currency: str = 'INR',
        settlement_status: str = 'unsettled'
    ) -> DriverLedger:
        """
        Create driver ledger entry.
        
        Note: Driver wallet is updated separately during payment confirmation.
        """
        entry = DriverLedger(
            driver_id=driver_id,
            trip_id=trip_id,
            currency=currency,
            amount=float(amount),
            entry_type=entry_type,
            reason=reason,
            settlement_status=settlement_status
        )
        db.add(entry)
        db.flush()
        
        return entry
    
    @staticmethod
    def get_driver_ledger(
        db: Session,
        driver_id: int,
        currency: Optional[str] = None,
        settlement_status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict:
        """
        Get paginated driver ledger entries.
        
        Args:
            db: Database session
            driver_id: Driver ID
            currency: Filter by currency
            settlement_status: Filter by settlement status
            page: Page number
            page_size: Items per page
        
        Returns:
            Dict with entries, total, page, page_size
        """
        query = (
            db.query(DriverLedger)
            .filter(DriverLedger.driver_id == driver_id)
        )
        
        if currency:
            query = query.filter(DriverLedger.currency == currency)
        
        if settlement_status:
            query = query.filter(DriverLedger.settlement_status == settlement_status)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        entries = (
            query
            .order_by(DriverLedger.created_on.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        
        return {
            'entries': entries,
            'total': total,
            'page': page,
            'page_size': page_size
        }
    
    @staticmethod
    def get_unsettled_entries(
        db: Session,
        driver_id: int,
        currency: str = 'INR',
        trip_ids: Optional[List[int]] = None
    ) -> List[DriverLedger]:
        """
        Get unsettled driver ledger entries.
        
        Args:
            db: Database session
            driver_id: Driver ID
            currency: Currency filter
            trip_ids: Optional list of trip IDs to filter
        
        Returns:
            List of unsettled ledger entries
        """
        query = (
            db.query(DriverLedger)
            .filter(
                DriverLedger.driver_id == driver_id,
                DriverLedger.currency == currency,
                DriverLedger.settlement_status == 'unsettled'
            )
        )
        
        if trip_ids:
            query = query.filter(DriverLedger.trip_id.in_(trip_ids))
        
        return query.order_by(DriverLedger.created_on.asc()).all()
    
    @staticmethod
    def mark_entries_settled(
        db: Session,
        entry_ids: List[int]
    ) -> int:
        """
        Mark ledger entries as settled.
        
        Args:
            db: Database session
            entry_ids: List of entry IDs to mark as settled
        
        Returns:
            Number of entries updated
        """
        if not entry_ids:
            return 0
        
        updated = (
            db.query(DriverLedger)
            .filter(
                DriverLedger.entry_id.in_(entry_ids),
                DriverLedger.settlement_status == 'unsettled'  # Safety check
            )
            .update(
                {'settlement_status': 'settled'},
                synchronize_session=False
            )
        )
        
        return updated
    
    @staticmethod
    def calculate_net_amount(entries: List[DriverLedger]) -> Decimal:
        """
        Calculate net amount from ledger entries.
        
        CREDIT = positive (platform owes driver)
        DEBIT = negative (driver owes platform)
        
        Returns:
            Net amount (positive or negative)
        """
        net = Decimal('0.00')
        
        for entry in entries:
            amount = Decimal(str(entry.amount))
            if entry.entry_type == 'CREDIT':
                net += amount
            else:  # DEBIT
                net -= amount
        
        return net
