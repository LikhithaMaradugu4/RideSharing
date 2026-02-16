"""
Financial Summary Service - Tenant Admin and Fleet Owner financial visibility.

Read-only views of driver financial data.

GET /tenant/drivers/financial-summary
GET /fleet/drivers/financial-summary
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from fastapi import HTTPException, status
from decimal import Decimal
from typing import List, Dict, Optional

from app.models.payments import DriverWallet
from app.models.ledger import DriverLedger
from app.models.fleet import DriverProfile, FleetDriver, Fleet
from app.models.identity import AppUser
from app.services.wallet_service import WalletService, MAX_NEGATIVE_LIMIT


class FinancialSummaryService:
    """Service for financial summary views."""
    
    @staticmethod
    def get_tenant_drivers_summary(
        db: Session,
        tenant_id: int
    ) -> List[Dict]:
        """
        Get financial summary for all drivers under a tenant.
        
        Returns:
        [
          {
            driver_id,
            driver_name,
            balances: [{ currency, balance }],
            total_unsettled_per_currency: [{ currency, balance }],
            is_blocked
          }
        ]
        """
        # Get all approved drivers for this tenant
        drivers = (
            db.query(DriverProfile, AppUser)
            .join(AppUser, DriverProfile.driver_id == AppUser.user_id)
            .filter(
                DriverProfile.tenant_id == tenant_id,
                DriverProfile.approval_status == 'APPROVED'
            )
            .all()
        )
        
        result = []
        for driver_profile, user in drivers:
            driver_id = driver_profile.driver_id
            
            # Get wallet balances
            balances = WalletService.get_driver_all_balances(db, driver_id)
            
            # Get unsettled totals
            unsettled = WalletService.get_driver_unsettled_totals(db, driver_id)
            
            # Check if blocked (any currency below limit)
            is_blocked = any(
                Decimal(str(b['balance'])) < MAX_NEGATIVE_LIMIT 
                for b in balances
            )
            
            result.append({
                'driver_id': driver_id,
                'driver_name': f"{user.first_name or ''} {user.last_name or ''}".strip() or user.phone,
                'balances': balances,
                'total_unsettled_per_currency': unsettled,
                'is_blocked': is_blocked
            })
        
        return result
    
    @staticmethod
    def get_fleet_drivers_summary(
        db: Session,
        fleet_id: int
    ) -> List[Dict]:
        """
        Get financial summary for all drivers under a fleet.
        
        Same structure as tenant summary.
        """
        # Get all active drivers in this fleet
        drivers = (
            db.query(FleetDriver, AppUser)
            .join(AppUser, FleetDriver.driver_id == AppUser.user_id)
            .filter(
                FleetDriver.fleet_id == fleet_id,
                FleetDriver.end_date.is_(None)  # Active
            )
            .all()
        )
        
        result = []
        for fleet_driver, user in drivers:
            driver_id = fleet_driver.driver_id
            
            # Get wallet balances
            balances = WalletService.get_driver_all_balances(db, driver_id)
            
            # Get unsettled totals
            unsettled = WalletService.get_driver_unsettled_totals(db, driver_id)
            
            # Check if blocked
            is_blocked = any(
                Decimal(str(b['balance'])) < MAX_NEGATIVE_LIMIT 
                for b in balances
            )
            
            result.append({
                'driver_id': driver_id,
                'driver_name': f"{user.first_name or ''} {user.last_name or ''}".strip() or user.phone,
                'balances': balances,
                'total_unsettled_per_currency': unsettled,
                'is_blocked': is_blocked
            })
        
        return result
    
    @staticmethod
    def get_driver_financial_details(
        db: Session,
        driver_id: int
    ) -> Dict:
        """
        Get detailed financial information for a single driver.
        """
        # Get driver info
        user = db.query(AppUser).filter(AppUser.user_id == driver_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found"
            )
        
        # Get wallet balances
        balances = WalletService.get_driver_all_balances(db, driver_id)
        
        # Get unsettled totals
        unsettled = WalletService.get_driver_unsettled_totals(db, driver_id)
        
        # Check if blocked
        is_blocked = any(
            Decimal(str(b['balance'])) < MAX_NEGATIVE_LIMIT 
            for b in balances
        )
        
        # Get recent ledger entries
        recent_entries = (
            db.query(DriverLedger)
            .filter(DriverLedger.driver_id == driver_id)
            .order_by(DriverLedger.created_on.desc())
            .limit(10)
            .all()
        )
        
        return {
            'driver_id': driver_id,
            'driver_name': f"{user.first_name or ''} {user.last_name or ''}".strip() or user.phone,
            'balances': balances,
            'total_unsettled_per_currency': unsettled,
            'is_blocked': is_blocked,
            'recent_entries': [
                {
                    'entry_id': e.entry_id,
                    'trip_id': e.trip_id,
                    'currency': e.currency,
                    'amount': float(e.amount),
                    'entry_type': e.entry_type,
                    'reason': e.reason,
                    'settlement_status': e.settlement_status,
                    'created_on': e.created_on
                }
                for e in recent_entries
            ]
        }
