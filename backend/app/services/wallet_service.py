"""
Wallet Service - Wallet operations with row locking.

SAFETY RULES:
- All financial operations must be transactional
- Use SELECT FOR UPDATE when updating wallet
- Prevent race conditions
- Multi-currency support: UNIQUE(entity_id, currency)

Driver wallet meaning:
    Positive → platform owes driver
    Negative → driver owes platform
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from sqlalchemy.sql import text
from fastapi import HTTPException, status
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, List, Dict

from app.models.payments import DriverWallet, TenantWallet, FleetWallet, PlatformWallet
from app.models.ledger import DriverLedger


# Maximum negative balance before blocking driver
MAX_NEGATIVE_LIMIT = Decimal('-3000.00')


class WalletService:
    """Service for wallet operations with row locking."""
    
    # ============================================
    # DRIVER WALLET
    # ============================================
    
    @staticmethod
    def get_driver_wallet(db: Session, driver_id: int, currency: str = 'INR') -> DriverWallet:
        """
        Get driver wallet, create if doesn't exist.
        """
        wallet = (
            db.query(DriverWallet)
            .filter(
                DriverWallet.driver_id == driver_id,
                DriverWallet.currency == currency
            )
            .first()
        )
        
        if not wallet:
            wallet = DriverWallet(
                driver_id=driver_id,
                currency=currency,
                balance=Decimal('0.00')
            )
            db.add(wallet)
            db.flush()
        
        return wallet
    
    @staticmethod
    def get_driver_wallet_for_update(db: Session, driver_id: int, currency: str = 'INR') -> DriverWallet:
        """
        Get driver wallet with row lock for update.
        Uses SELECT FOR UPDATE to prevent race conditions.
        """
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
            # Create wallet
            wallet = DriverWallet(
                driver_id=driver_id,
                currency=currency,
                balance=Decimal('0.00')
            )
            db.add(wallet)
            db.flush()
            
            # Re-fetch with lock
            wallet = (
                db.query(DriverWallet)
                .filter(
                    DriverWallet.driver_id == driver_id,
                    DriverWallet.currency == currency
                )
                .with_for_update()
                .first()
            )
        
        return wallet
    
    @staticmethod
    def get_driver_all_balances(db: Session, driver_id: int) -> List[Dict]:
        """
        Get all currency balances for a driver.
        """
        wallets = (
            db.query(DriverWallet)
            .filter(DriverWallet.driver_id == driver_id)
            .all()
        )
        
        return [
            {'currency': w.currency, 'balance': Decimal(str(w.balance))}
            for w in wallets
        ]
    
    @staticmethod
    def get_driver_unsettled_totals(db: Session, driver_id: int) -> List[Dict]:
        """
        Get total unsettled amounts per currency from driver ledger.
        
        Returns net amount (credits - debits) that is unsettled.
        """
        results = (
            db.query(
                DriverLedger.currency,
                func.sum(
                    func.case(
                        (DriverLedger.entry_type == 'CREDIT', DriverLedger.amount),
                        else_=-DriverLedger.amount
                    )
                ).label('net_amount')
            )
            .filter(
                DriverLedger.driver_id == driver_id,
                DriverLedger.settlement_status == 'unsettled'
            )
            .group_by(DriverLedger.currency)
            .all()
        )
        
        return [
            {'currency': r.currency, 'balance': Decimal(str(r.net_amount or 0))}
            for r in results
        ]
    
    @staticmethod
    def update_driver_wallet(
        db: Session,
        driver_id: int,
        amount: Decimal,
        operation: str,
        currency: str = 'INR'
    ) -> DriverWallet:
        """
        Update driver wallet balance with row locking.
        
        Args:
            db: Database session
            driver_id: Driver ID
            amount: Amount to add/subtract
            operation: 'credit' or 'debit'
            currency: Currency code
        
        Returns:
            Updated wallet
        """
        # Get wallet with lock
        wallet = WalletService.get_driver_wallet_for_update(db, driver_id, currency)
        
        if operation == 'credit':
            wallet.balance = Decimal(str(wallet.balance)) + Decimal(str(amount))
        elif operation == 'debit':
            wallet.balance = Decimal(str(wallet.balance)) - Decimal(str(amount))
        else:
            raise ValueError(f"Invalid operation: {operation}")
        
        wallet.updated_on = datetime.now(timezone.utc)
        
        return wallet
    
    @staticmethod
    def check_driver_blocked(db: Session, driver_id: int, currency: str = 'INR') -> bool:
        """
        Check if driver should be blocked based on negative balance.
        
        Returns True if driver wallet balance < MAX_NEGATIVE_LIMIT
        """
        wallet = WalletService.get_driver_wallet(db, driver_id, currency)
        return Decimal(str(wallet.balance)) < MAX_NEGATIVE_LIMIT
    
    # ============================================
    # TENANT WALLET
    # ============================================
    
    @staticmethod
    def get_tenant_wallet(db: Session, tenant_id: int, currency: str = 'INR') -> TenantWallet:
        """Get tenant wallet, create if doesn't exist."""
        wallet = (
            db.query(TenantWallet)
            .filter(
                TenantWallet.tenant_id == tenant_id,
                TenantWallet.currency == currency
            )
            .first()
        )
        
        if not wallet:
            wallet = TenantWallet(
                tenant_id=tenant_id,
                currency=currency,
                balance=Decimal('0.00')
            )
            db.add(wallet)
            db.flush()
        
        return wallet
    
    @staticmethod
    def get_tenant_wallet_for_update(db: Session, tenant_id: int, currency: str = 'INR') -> TenantWallet:
        """Get tenant wallet with row lock."""
        wallet = (
            db.query(TenantWallet)
            .filter(
                TenantWallet.tenant_id == tenant_id,
                TenantWallet.currency == currency
            )
            .with_for_update()
            .first()
        )
        
        if not wallet:
            wallet = TenantWallet(
                tenant_id=tenant_id,
                currency=currency,
                balance=Decimal('0.00')
            )
            db.add(wallet)
            db.flush()
            
            wallet = (
                db.query(TenantWallet)
                .filter(
                    TenantWallet.tenant_id == tenant_id,
                    TenantWallet.currency == currency
                )
                .with_for_update()
                .first()
            )
        
        return wallet
    
    @staticmethod
    def update_tenant_wallet(
        db: Session,
        tenant_id: int,
        amount: Decimal,
        operation: str,
        currency: str = 'INR'
    ) -> TenantWallet:
        """Update tenant wallet with row locking."""
        wallet = WalletService.get_tenant_wallet_for_update(db, tenant_id, currency)
        
        if operation == 'credit':
            wallet.balance = Decimal(str(wallet.balance)) + Decimal(str(amount))
        elif operation == 'debit':
            wallet.balance = Decimal(str(wallet.balance)) - Decimal(str(amount))
        else:
            raise ValueError(f"Invalid operation: {operation}")
        
        wallet.updated_on = datetime.now(timezone.utc)
        return wallet
    
    # ============================================
    # FLEET WALLET
    # ============================================
    
    @staticmethod
    def get_fleet_wallet(db: Session, fleet_id: int, currency: str = 'INR') -> FleetWallet:
        """Get fleet wallet, create if doesn't exist."""
        wallet = (
            db.query(FleetWallet)
            .filter(
                FleetWallet.fleet_id == fleet_id,
                FleetWallet.currency == currency
            )
            .first()
        )
        
        if not wallet:
            wallet = FleetWallet(
                fleet_id=fleet_id,
                currency=currency,
                balance=Decimal('0.00')
            )
            db.add(wallet)
            db.flush()
        
        return wallet
    
    @staticmethod
    def get_fleet_wallet_for_update(db: Session, fleet_id: int, currency: str = 'INR') -> FleetWallet:
        """Get fleet wallet with row lock."""
        wallet = (
            db.query(FleetWallet)
            .filter(
                FleetWallet.fleet_id == fleet_id,
                FleetWallet.currency == currency
            )
            .with_for_update()
            .first()
        )
        
        if not wallet:
            wallet = FleetWallet(
                fleet_id=fleet_id,
                currency=currency,
                balance=Decimal('0.00')
            )
            db.add(wallet)
            db.flush()
            
            wallet = (
                db.query(FleetWallet)
                .filter(
                    FleetWallet.fleet_id == fleet_id,
                    FleetWallet.currency == currency
                )
                .with_for_update()
                .first()
            )
        
        return wallet
    
    @staticmethod
    def update_fleet_wallet(
        db: Session,
        fleet_id: int,
        amount: Decimal,
        operation: str,
        currency: str = 'INR'
    ) -> FleetWallet:
        """Update fleet wallet with row locking."""
        wallet = WalletService.get_fleet_wallet_for_update(db, fleet_id, currency)
        
        if operation == 'credit':
            wallet.balance = Decimal(str(wallet.balance)) + Decimal(str(amount))
        elif operation == 'debit':
            wallet.balance = Decimal(str(wallet.balance)) - Decimal(str(amount))
        else:
            raise ValueError(f"Invalid operation: {operation}")
        
        wallet.updated_on = datetime.now(timezone.utc)
        return wallet
    
    # ============================================
    # PLATFORM WALLET
    # ============================================
    
    @staticmethod
    def get_platform_wallet(db: Session, currency: str = 'INR') -> PlatformWallet:
        """Get platform wallet, create if doesn't exist."""
        wallet = (
            db.query(PlatformWallet)
            .filter(PlatformWallet.currency == currency)
            .first()
        )
        
        if not wallet:
            wallet = PlatformWallet(
                currency=currency,
                balance=Decimal('0.00')
            )
            db.add(wallet)
            db.flush()
        
        return wallet
    
    @staticmethod
    def get_platform_wallet_for_update(db: Session, currency: str = 'INR') -> PlatformWallet:
        """Get platform wallet with row lock."""
        wallet = (
            db.query(PlatformWallet)
            .filter(PlatformWallet.currency == currency)
            .with_for_update()
            .first()
        )
        
        if not wallet:
            wallet = PlatformWallet(
                currency=currency,
                balance=Decimal('0.00')
            )
            db.add(wallet)
            db.flush()
            
            wallet = (
                db.query(PlatformWallet)
                .filter(PlatformWallet.currency == currency)
                .with_for_update()
                .first()
            )
        
        return wallet
    
    @staticmethod
    def update_platform_wallet(
        db: Session,
        amount: Decimal,
        operation: str,
        currency: str = 'INR'
    ) -> PlatformWallet:
        """Update platform wallet with row locking."""
        wallet = WalletService.get_platform_wallet_for_update(db, currency)
        
        if operation == 'credit':
            wallet.balance = Decimal(str(wallet.balance)) + Decimal(str(amount))
        elif operation == 'debit':
            wallet.balance = Decimal(str(wallet.balance)) - Decimal(str(amount))
        else:
            raise ValueError(f"Invalid operation: {operation}")
        
        wallet.updated_on = datetime.now(timezone.utc)
        return wallet
