"""
Payment Confirmation Service - Handle payment confirmation flow.

Trip completes:
    trip.status = completed
    trip.payment_status = pending

Only after payment confirmation:

ONLINE:
    - Driver ledger: CREDIT driver_earning
    - Tenant ledger: CREDIT tenant_commission
    - Fleet ledger: CREDIT fleet_commission
    - Platform ledger: CREDIT platform_fee
    - Update respective wallets

CASH:
    - Driver physically receives full fare
    - Driver ledger:
          CREDIT driver_earning
          DEBIT platform_fee
          DEBIT tenant_commission
          DEBIT fleet_commission
    - Platform/Tenant/Fleet ledgers: CREDIT their commissions
    - Update wallets accordingly

All operations must be inside DB transaction.
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, Dict

from app.models.trips import Trip
from app.models.fleet import FleetDriver, Fleet
from app.models.payments import Payment
from app.services.commission_service import CommissionService
from app.services.ledger_service import LedgerService
from app.services.wallet_service import WalletService


def get_driver_business_fleet(db: Session, driver_id: int) -> Optional[int]:
    """
    Get fleet_id if driver belongs to a BUSINESS fleet.
    
    Returns None if driver is independent (INDIVIDUAL fleet) or no fleet.
    Fleet commission only applies to BUSINESS fleet drivers.
    """
    fleet_driver = (
        db.query(FleetDriver, Fleet)
        .join(Fleet, FleetDriver.fleet_id == Fleet.fleet_id)
        .filter(
            FleetDriver.driver_id == driver_id,
            FleetDriver.end_date.is_(None),  # Active association
            Fleet.fleet_type == "BUSINESS"  # Only BUSINESS fleets
        )
        .first()
    )
    
    if fleet_driver:
        return fleet_driver[1].fleet_id  # Return fleet_id
    
    return None


class PaymentConfirmationService:
    """Service for payment confirmation and ledger/wallet updates."""
    
    @staticmethod
    def confirm_payment(
        db: Session,
        trip_id: int,
        payment_mode: str,
        amount: Decimal,
        confirmed_by: int,
        gateway_payment_id: Optional[str] = None
    ) -> Dict:
        """
        Confirm payment for a completed trip.
        
        This is the main entry point for payment confirmation.
        Creates all ledger entries and updates wallets.
        
        Args:
            db: Database session
            trip_id: Trip ID
            payment_mode: 'cash' or 'online'
            amount: Payment amount (must match trip fare)
            confirmed_by: User ID confirming payment
            gateway_payment_id: Payment gateway ID (for online payments)
        
        Returns:
            Payment confirmation result with fare split
        """
        # Validate payment mode
        if payment_mode.lower() not in ['cash', 'online']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="payment_mode must be 'cash' or 'online'"
            )
        
        # Get trip
        trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()
        
        if not trip:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trip not found"
            )
        
        # Validate trip status
        if trip.status != 'COMPLETED':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Trip status must be COMPLETED, current: {trip.status}"
            )
        
        # Check if already paid
        if trip.payment_status == 'SUCCESS':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Trip already paid"
            )
        
        # Validate amount matches fare
        trip_fare = Decimal(str(trip.fare_amount or 0))
        payment_amount = Decimal(str(amount))
        
        if abs(trip_fare - payment_amount) > Decimal('0.01'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Payment amount {amount} does not match trip fare {trip_fare}"
            )
        
        # Get currency
        currency = trip.currency if trip.currency else 'INR'
        
        # Check if driver belongs to a BUSINESS fleet
        fleet_id = get_driver_business_fleet(db, trip.driver_id)
        has_fleet = fleet_id is not None
        
        # Calculate fare split using DB commission rates
        fare_split = CommissionService.calculate_fare_split(
            db=db,
            total_fare=payment_amount,
            tenant_id=trip.tenant_id,
            city_id=trip.city_id,
            vehicle_category=None,  # TODO: Get from trip vehicle
            has_fleet=has_fleet,
            currency=currency
        )
        
        platform_commission = fare_split['platform_commission']
        tenant_commission = fare_split['tenant_commission']
        fleet_commission = fare_split['fleet_commission']
        driver_earning = fare_split['driver_earning']
        
        # Store commission values on trip (immutable snapshot)
        trip.platform_fee = float(platform_commission)
        trip.tenant_commission = float(tenant_commission)
        trip.fleet_commission = float(fleet_commission)
        trip.driver_earning = float(driver_earning)
        trip.payment_mode = payment_mode.lower()
        
        # Process based on payment mode
        if payment_mode.lower() == 'online':
            PaymentConfirmationService._process_online_payment(
                db=db,
                trip=trip,
                platform_commission=platform_commission,
                tenant_commission=tenant_commission,
                fleet_commission=fleet_commission,
                driver_earning=driver_earning,
                fleet_id=fleet_id,
                currency=currency
            )
        else:  # cash
            PaymentConfirmationService._process_cash_payment(
                db=db,
                trip=trip,
                platform_commission=platform_commission,
                tenant_commission=tenant_commission,
                fleet_commission=fleet_commission,
                driver_earning=driver_earning,
                fleet_id=fleet_id,
                currency=currency
            )
        
        # Update trip status
        trip.payment_status = 'SUCCESS'
        trip.settlement_status = 'unsettled'
        
        # Create payment record
        payment = Payment(
            trip_id=trip_id,
            amount=float(payment_amount),
            currency=currency,
            payment_mode=payment_mode.upper(),
            status='SUCCESS',
            gateway_payment_id=gateway_payment_id,
            confirmed_by_driver_id=confirmed_by if payment_mode.lower() == 'cash' else None,
            confirmed_at=datetime.now(timezone.utc) if payment_mode.lower() == 'cash' else None,
            created_by=confirmed_by
        )
        db.add(payment)
        
        db.flush()
        
        return {
            'trip_id': trip_id,
            'status': 'SUCCESS',
            'fare_split': {
                'total_fare': float(payment_amount),
                'platform_commission': float(platform_commission),
                'tenant_commission': float(tenant_commission),
                'fleet_commission': float(fleet_commission),
                'driver_earning': float(driver_earning),
                'currency': currency
            },
            'payment_mode': payment_mode.lower(),
            'message': f"Payment confirmed successfully ({payment_mode})"
        }
    
    @staticmethod
    def _process_online_payment(
        db: Session,
        trip: Trip,
        platform_commission: Decimal,
        tenant_commission: Decimal,
        fleet_commission: Decimal,
        driver_earning: Decimal,
        fleet_id: Optional[int],
        currency: str
    ):
        """
        Process ONLINE payment.
        
        ONLINE:
        - Driver ledger: CREDIT driver_earning
        - Tenant ledger: CREDIT tenant_commission
        - Fleet ledger: CREDIT fleet_commission
        - Platform ledger: CREDIT platform_fee
        - Update respective wallets
        """
        trip_id = trip.trip_id
        driver_id = trip.driver_id
        tenant_id = trip.tenant_id
        
        # Platform Ledger - CREDIT
        if platform_commission > 0:
            LedgerService.create_platform_entry(
                db=db,
                trip_id=trip_id,
                amount=platform_commission,
                entry_type='CREDIT',
                reason=f"Commission from trip {trip_id} (ONLINE)",
                currency=currency
            )
        
        # Tenant Ledger - CREDIT
        if tenant_commission > 0 and tenant_id:
            LedgerService.create_tenant_entry(
                db=db,
                tenant_id=tenant_id,
                trip_id=trip_id,
                amount=tenant_commission,
                entry_type='CREDIT',
                reason=f"Commission from trip {trip_id} (ONLINE)",
                currency=currency
            )
        
        # Fleet Ledger - CREDIT
        if fleet_commission > 0 and fleet_id:
            LedgerService.create_fleet_entry(
                db=db,
                fleet_id=fleet_id,
                trip_id=trip_id,
                amount=fleet_commission,
                entry_type='CREDIT',
                reason=f"Commission from trip {trip_id} (ONLINE)",
                currency=currency
            )
        
        # Driver Ledger - CREDIT earning only
        if driver_earning > 0:
            LedgerService.create_driver_entry(
                db=db,
                driver_id=driver_id,
                trip_id=trip_id,
                amount=driver_earning,
                entry_type='CREDIT',
                reason=f"Earning from trip {trip_id} (ONLINE)",
                currency=currency
            )
            
            # Update driver wallet - CREDIT
            WalletService.update_driver_wallet(
                db=db,
                driver_id=driver_id,
                amount=driver_earning,
                operation='credit',
                currency=currency
            )
    
    @staticmethod
    def _process_cash_payment(
        db: Session,
        trip: Trip,
        platform_commission: Decimal,
        tenant_commission: Decimal,
        fleet_commission: Decimal,
        driver_earning: Decimal,
        fleet_id: Optional[int],
        currency: str
    ):
        """
        Process CASH payment.
        
        CASH:
        - Driver physically receives full fare
        - Driver ledger:
              DEBIT platform_fee (driver owes platform)
              DEBIT tenant_commission (driver owes tenant)
              DEBIT fleet_commission (driver owes fleet, if applicable)
        - Platform/Tenant/Fleet ledgers: CREDIT their commissions
        - Update wallets accordingly
        
        Note: For CASH, driver already has the money.
        We only record what they OWE (debits).
        """
        trip_id = trip.trip_id
        driver_id = trip.driver_id
        tenant_id = trip.tenant_id
        
        # Platform Ledger - CREDIT
        if platform_commission > 0:
            LedgerService.create_platform_entry(
                db=db,
                trip_id=trip_id,
                amount=platform_commission,
                entry_type='CREDIT',
                reason=f"Commission from trip {trip_id} (CASH)",
                currency=currency
            )
        
        # Tenant Ledger - CREDIT
        if tenant_commission > 0 and tenant_id:
            LedgerService.create_tenant_entry(
                db=db,
                tenant_id=tenant_id,
                trip_id=trip_id,
                amount=tenant_commission,
                entry_type='CREDIT',
                reason=f"Commission from trip {trip_id} (CASH)",
                currency=currency
            )
        
        # Fleet Ledger - CREDIT
        if fleet_commission > 0 and fleet_id:
            LedgerService.create_fleet_entry(
                db=db,
                fleet_id=fleet_id,
                trip_id=trip_id,
                amount=fleet_commission,
                entry_type='CREDIT',
                reason=f"Commission from trip {trip_id} (CASH)",
                currency=currency
            )
        
        # Driver Ledger entries for CASH
        # Driver collected full cash, record debits (amounts owed)
        
        # DEBIT: Platform commission (driver owes platform)
        if platform_commission > 0:
            LedgerService.create_driver_entry(
                db=db,
                driver_id=driver_id,
                trip_id=trip_id,
                amount=platform_commission,
                entry_type='DEBIT',
                reason=f"Platform commission for trip {trip_id} (CASH)",
                currency=currency
            )
        
        # DEBIT: Tenant commission (driver owes tenant)
        if tenant_commission > 0:
            LedgerService.create_driver_entry(
                db=db,
                driver_id=driver_id,
                trip_id=trip_id,
                amount=tenant_commission,
                entry_type='DEBIT',
                reason=f"Tenant commission for trip {trip_id} (CASH)",
                currency=currency
            )
        
        # DEBIT: Fleet commission (driver owes fleet)
        if fleet_commission > 0 and fleet_id:
            LedgerService.create_driver_entry(
                db=db,
                driver_id=driver_id,
                trip_id=trip_id,
                amount=fleet_commission,
                entry_type='DEBIT',
                reason=f"Fleet commission for trip {trip_id} (CASH)",
                currency=currency
            )
        
        # Update driver wallet - DEBIT total commissions owed
        total_owed = platform_commission + tenant_commission + fleet_commission
        if total_owed > 0:
            WalletService.update_driver_wallet(
                db=db,
                driver_id=driver_id,
                amount=total_owed,
                operation='debit',
                currency=currency
            )
