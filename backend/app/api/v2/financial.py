"""
Financial API Endpoints

Driver APIs:
- GET /driver/wallet - Get wallet summary
- GET /driver/ledger - Get ledger history with pagination
- GET /driver/trips - Get trips (for CASH rides: show pending_settlement)
- POST /driver/payout-request - Request settlement

Tenant Admin APIs:
- GET /tenant/drivers/financial-summary - Financial summary of all drivers

Fleet Owner APIs:
- GET /fleet/drivers/financial-summary - Financial summary of fleet drivers
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from app.core.database import SessionLocal
# JWT Auth for Driver and Fleet Owner endpoints
from app.api.deps.jwt_auth import get_current_user as get_jwt_user
# Session Auth for Tenant Admin endpoints
from app.api.deps.auth import get_current_user as get_session_user
from app.schemas.financial import (
    DriverWalletResponse,
    DriverLedgerResponse,
    DriverTripFinancialResponse,
    PayoutRequestCreate,
    PayoutRequestResponse,
    DriverFinancialSummary
)
from app.services.wallet_service import WalletService, MAX_NEGATIVE_LIMIT
from app.services.ledger_service import LedgerService
from app.services.payout_service import PayoutService
from app.services.financial_summary_service import FinancialSummaryService
from app.models.identity import AppUser
from app.models.fleet import DriverProfile, Fleet, FleetDriver
from app.models.trips import Trip
from app.models.ledger import DriverLedger
from decimal import Decimal


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================
# DRIVER ENDPOINTS
# ============================================

@router.get("/driver/wallet", response_model=DriverWalletResponse)
def get_driver_wallet(
    currency: str = Query(default='INR', description="Currency code"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_jwt_user)
):
    """
    Get driver's wallet summary.
    
    Auth: JWT Bearer Token
    
    Returns:
    - balance: Current wallet balance
    - currency: Currency code
    - unsettled_total: Total unsettled amount
    - is_blocked: Whether driver is blocked
    """
    driver_id = current_user.get("user_id")
    
    # Get wallet
    wallet = WalletService.get_driver_wallet(db, driver_id, currency)
    
    # Get unsettled total for this currency
    unsettled_totals = WalletService.get_driver_unsettled_totals(db, driver_id)
    unsettled = next(
        (u['balance'] for u in unsettled_totals if u['currency'] == currency),
        Decimal('0.00')
    )
    
    # Check if blocked
    is_blocked = Decimal(str(wallet.balance)) < MAX_NEGATIVE_LIMIT
    
    return {
        'balance': float(wallet.balance),
        'currency': wallet.currency,
        'unsettled_total': float(unsettled),
        'is_blocked': is_blocked
    }


@router.get("/driver/wallet/all")
def get_driver_all_wallets(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_jwt_user)
):
    """
    Get all wallet balances for driver (multi-currency).
    
    Auth: JWT Bearer Token
    """
    driver_id = current_user.get("user_id")
    balances = WalletService.get_driver_all_balances(db, driver_id)
    
    return {
        'driver_id': driver_id,
        'balances': [
            {'currency': b['currency'], 'balance': float(b['balance'])}
            for b in balances
        ]
    }


@router.get("/driver/earnings")
def get_driver_earnings(
    currency: str = Query(default='INR'),
    from_date: Optional[str] = Query(default=None, description="From date (YYYY-MM-DD)"),
    to_date: Optional[str] = Query(default=None, description="To date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_jwt_user)
):
    """
    Get driver's total earnings from completed trips.
    
    Auth: JWT Bearer Token
    
    Returns: SUM(trip.driver_earning) for completed trips
    Wallet balance is NOT used - it represents outstanding debt.
    """
    driver_id = current_user.get("user_id")
    
    # Query completed trips
    query = (
        db.query(Trip)
        .filter(
            Trip.driver_id == driver_id,
            Trip.status == 'COMPLETED',
            Trip.currency == currency
        )
    )
    
    # Optional date filtering
    if from_date:
        try:
            from datetime import datetime
            start_date = datetime.strptime(from_date, '%Y-%m-%d')
            query = query.filter(Trip.completed_at >= start_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid from_date format (use YYYY-MM-DD)")
    
    if to_date:
        try:
            from datetime import datetime
            end_date = datetime.strptime(to_date, '%Y-%m-%d')
            query = query.filter(Trip.completed_at <= end_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid to_date format (use YYYY-MM-DD)")
    
    trips = query.all()
    
    # Calculate totals
    total_earnings = Decimal('0.00')
    total_fare = Decimal('0.00')
    total_platform_fee = Decimal('0.00')
    total_tenant_commission = Decimal('0.00')
    total_fleet_commission = Decimal('0.00')
    trip_count = 0
    
    trip_details = []
    for trip in trips:
        trip_earning = Decimal(str(trip.driver_earning or 0))
        fare = Decimal(str(trip.fare_amount or 0))
        platform = Decimal(str(trip.platform_fee or 0))
        tenant = Decimal(str(trip.tenant_commission or 0))
        fleet = Decimal(str(trip.fleet_commission or 0))
        
        total_earnings += trip_earning
        total_fare += fare
        total_platform_fee += platform
        total_tenant_commission += tenant
        total_fleet_commission += fleet
        trip_count += 1
        
        trip_details.append({
            'trip_id': trip.trip_id,
            'fare_amount': float(fare),
            'driver_earning': float(trip_earning),
            'platform_fee': float(platform),
            'tenant_commission': float(tenant),
            'fleet_commission': float(fleet),
            'payment_status': trip.payment_status,
            'settlement_status': trip.settlement_status,
            'completed_at': trip.completed_at.isoformat() if trip.completed_at else None
        })
    
    # Get wallet balance (for reference - shows outstanding debt)
    wallet = WalletService.get_driver_wallet(db, driver_id, currency)
    
    return {
        'driver_id': driver_id,
        'currency': currency,
        'summary': {
            'total_earnings': float(total_earnings),
            'total_fare': float(total_fare),
            'total_platform_fee': float(total_platform_fee),
            'total_tenant_commission': float(total_tenant_commission),
            'total_fleet_commission': float(total_fleet_commission),
            'total_commission': float(total_platform_fee + total_tenant_commission + total_fleet_commission),
        },
        'trip_count': trip_count,
        'wallet_balance': float(wallet.balance) if wallet else 0.0,
        'wallet_note': 'Negative balance = driver owes platform. Zero = settled. Use settlement endpoint to pay back commission.',
        'from_date': from_date,
        'to_date': to_date,
        'trips': trip_details[:20]  # Limit to 20 most recent for response size
    }


@router.get("/driver/ledger")
def get_driver_ledger(
    currency: str = Query(default='INR'),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    settlement_status: Optional[str] = Query(default=None, description="Filter by settlement status: settled/unsettled"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_jwt_user)
):
    """
    Get driver's ledger history with pagination.
    
    Auth: JWT Bearer Token
    
    Returns paginated list of ledger entries.
    """
    driver_id = current_user.get("user_id")
    
    # Build query
    query = (
        db.query(DriverLedger)
        .filter(
            DriverLedger.driver_id == driver_id,
            DriverLedger.currency == currency
        )
    )
    
    if settlement_status:
        query = query.filter(DriverLedger.settlement_status == settlement_status)
    
    # Get total count
    total = query.count()
    
    # Paginate
    offset = (page - 1) * page_size
    entries = (
        query
        .order_by(DriverLedger.created_on.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )
    
    return {
        'driver_id': driver_id,
        'currency': currency,
        'total': total,
        'page': page,
        'page_size': page_size,
        'entries': [
            {
                'entry_id': e.entry_id,
                'trip_id': e.trip_id,
                'amount': float(e.amount),
                'entry_type': e.entry_type,
                'reason': e.reason,
                'settlement_status': e.settlement_status,
                'created_on': e.created_on
            }
            for e in entries
        ]
    }


@router.get("/driver/trips/financial")
def get_driver_trips_financial(
    payment_mode: Optional[str] = Query(default=None, description="Filter by payment mode: CASH/ONLINE"),
    settlement_status: Optional[str] = Query(default=None, description="Filter by settlement: SETTLED/PENDING"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_jwt_user)
):
    """
    Get driver's trips with financial details.
    
    Auth: JWT Bearer Token
    
    For CASH rides, shows pending_settlement amounts.
    """
    driver_id = current_user.get("user_id")
    
    query = (
        db.query(Trip)
        .filter(
            Trip.driver_id == driver_id,
            Trip.status == 'COMPLETED'
        )
    )
    
    if payment_mode:
        query = query.filter(Trip.payment_mode == payment_mode)
    
    if settlement_status:
        query = query.filter(Trip.settlement_status == settlement_status)
    
    # Get total
    total = query.count()
    
    # Paginate
    offset = (page - 1) * page_size
    trips = (
        query
        .order_by(Trip.completed_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )
    
    return {
        'driver_id': driver_id,
        'total': total,
        'page': page,
        'page_size': page_size,
        'trips': [
            {
                'trip_id': t.trip_id,
                'fare_amount': float(t.fare_amount) if t.fare_amount else None,
                'payment_mode': t.payment_mode,
                'settlement_status': t.settlement_status,
                'tenant_commission': float(t.tenant_commission) if t.tenant_commission else None,
                'fleet_commission': float(t.fleet_commission) if t.fleet_commission else None,
                'completed_at': t.completed_at,
                'currency': t.currency
            }
            for t in trips
        ]
    }


@router.get("/driver/unsettled-trips")
def get_driver_unsettled_trips(
    currency: str = Query(default='INR'),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_jwt_user)
):
    """
    Get driver's unsettled trips that can be settled.
    
    Auth: JWT Bearer Token
    
    Returns trips with:
    - payment_status = 'PAID' (cash collected from rider)
    - settlement_status = 'unsettled' (commission not paid back to platform)
    - Has unsettled DEBIT ledger entries
    """
    driver_id = current_user.get("user_id")
    
    # Query unsettled trips
    trips = (
        db.query(Trip)
        .filter(
            Trip.driver_id == driver_id,
            Trip.status == 'COMPLETED',
            Trip.payment_status == 'PAID',
            Trip.settlement_status == 'unsettled',
            Trip.currency == currency
        )
        .order_by(Trip.completed_at.desc())
        .all()
    )
    
    # Build response with trip details
    trip_list = []
    total_commission = Decimal('0.00')
    
    for trip in trips:
        # Calculate total commission for this trip
        platform_fee = Decimal(str(trip.platform_fee or 0))
        tenant_commission = Decimal(str(trip.tenant_commission or 0))
        fleet_commission = Decimal(str(trip.fleet_commission or 0))
        trip_commission = platform_fee + tenant_commission + fleet_commission
        
        total_commission += trip_commission
        
        trip_list.append({
            'trip_id': trip.trip_id,
            'fare_amount': float(trip.fare_amount or 0),
            'driver_earning': float(trip.driver_earning or 0),
            'platform_fee': float(platform_fee),
            'tenant_commission': float(tenant_commission),
            'fleet_commission': float(fleet_commission),
            'total_commission': float(trip_commission),
            'currency': trip.currency,
            'payment_mode': trip.payment_mode,
            'completed_at': trip.completed_at.isoformat() if trip.completed_at else None
        })
    
    return {
        'driver_id': driver_id,
        'currency': currency,
        'total_commission_due': float(total_commission),
        'trip_count': len(trip_list),
        'trips': trip_list
    }


@router.post("/driver/settlement-preview")
def get_settlement_preview(
    request_data: PayoutRequestCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_jwt_user)
):
    """
    Preview settlement before confirming.
    
    Auth: JWT Bearer Token
    
    Returns breakdown of commissions for the selected trips
    WITHOUT actually performing the settlement.
    """
    driver_id = current_user.get("user_id")
    
    if not request_data.trip_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="trip_ids cannot be empty"
        )
    
    # Fetch trips and calculate totals
    trips = (
        db.query(Trip)
        .filter(
            Trip.trip_id.in_(request_data.trip_ids),
            Trip.driver_id == driver_id,
            Trip.status == 'COMPLETED',
            Trip.settlement_status == 'unsettled',
            Trip.currency == request_data.currency
        )
        .all()
    )
    
    if not trips:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No eligible unsettled trips found for the given IDs"
        )
    
    total_fare = Decimal('0.00')
    total_platform_fee = Decimal('0.00')
    total_tenant_commission = Decimal('0.00')
    total_fleet_commission = Decimal('0.00')
    total_driver_earning = Decimal('0.00')
    total_commission = Decimal('0.00')
    
    trip_details = []
    for trip in trips:
        fare = Decimal(str(trip.fare_amount or 0))
        platform = Decimal(str(trip.platform_fee or 0))
        tenant = Decimal(str(trip.tenant_commission or 0))
        fleet = Decimal(str(trip.fleet_commission or 0))
        earning = Decimal(str(trip.driver_earning or 0))
        commission = platform + tenant + fleet
        
        total_fare += fare
        total_platform_fee += platform
        total_tenant_commission += tenant
        total_fleet_commission += fleet
        total_driver_earning += earning
        total_commission += commission
        
        trip_details.append({
            'trip_id': trip.trip_id,
            'fare_amount': float(fare),
            'platform_fee': float(platform),
            'tenant_commission': float(tenant),
            'fleet_commission': float(fleet),
            'driver_earning': float(earning),
            'total_commission': float(commission),
            'completed_at': trip.completed_at.isoformat() if trip.completed_at else None
        })
    
    return {
        'trip_count': len(trips),
        'currency': request_data.currency,
        'summary': {
            'total_fare': float(total_fare),
            'total_platform_fee': float(total_platform_fee),
            'total_tenant_commission': float(total_tenant_commission),
            'total_fleet_commission': float(total_fleet_commission),
            'total_commission': float(total_commission),
            'net_driver_earning': float(total_driver_earning)
        },
        'trips': trip_details
    }


@router.post("/driver/payout-request")
def create_payout_request(
    request_data: PayoutRequestCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_jwt_user)
):
    """
    Request a payout/settlement (trip-based).
    
    Auth: JWT Bearer Token
    
    Settles all unsettled DEBIT entries for the specified trips.
    Settlement is IMMEDIATE - no admin approval required.
    """
    driver_id = current_user.get("user_id")
    
    try:
        result = PayoutService.process_settlement(
            db=db,
            driver_id=driver_id,
            trip_ids=request_data.trip_ids,
            currency=request_data.currency
        )
        
        db.commit()
        
        return {
            'success': True,
            'payout_request_id': result['payout_request_id'],
            'settlement_amount': result['settlement_amount'],
            'entries_settled': result['entries_settled'],
            'trips_settled': result['trips_settled'],
            'old_balance': result['old_balance'],
            'new_balance': result['new_balance'],
            'is_blocked': result['is_blocked'],
            'message': result['message']
        }
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Settlement failed: {str(e)}"
        )


@router.get("/driver/payout-requests")
def get_driver_payout_requests(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_jwt_user)
):
    """
    Get driver's payout request history.
    
    Auth: JWT Bearer Token
    """
    from app.models.financial import PayoutRequest
    
    driver_id = current_user.get("user_id")
    
    query = (
        db.query(PayoutRequest)
        .filter(PayoutRequest.driver_id == driver_id)
    )
    
    total = query.count()
    
    offset = (page - 1) * page_size
    requests = (
        query
        .order_by(PayoutRequest.created_on.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )
    
    return {
        'driver_id': driver_id,
        'total': total,
        'page': page,
        'page_size': page_size,
        'requests': [
            {
                'request_id': r.id,
                'id': r.id,
                'total_amount': float(r.total_amount),
                'currency': r.currency,
                'payout_type': r.payout_type,
                'status': r.status,
                'created_on': r.created_on,
                'processed_on': r.processed_on
            }
            for r in requests
        ],
        'payouts': [
            {
                'request_id': r.id,
                'id': r.id,
                'total_amount': float(r.total_amount),
                'currency': r.currency,
                'payout_type': r.payout_type,
                'status': r.status,
                'created_on': r.created_on,
                'processed_on': r.processed_on
            }
            for r in requests
        ]
    }


# ============================================
# TENANT ADMIN ENDPOINTS
# ============================================

@router.get("/tenant/drivers/financial-summary")
def get_tenant_drivers_financial_summary(
    db: Session = Depends(get_db),
    current_user: AppUser = Depends(get_session_user)
):
    """
    Get financial summary of all drivers under tenant.
    
    Auth: Session (x_session_id header)
    
    For tenant admin use.
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
    # Verify user is tenant admin
    if current_user.role not in ['TENANT_ADMIN', 'SUPER_ADMIN']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only tenant admins can access this endpoint"
        )
    
    tenant_id = current_user.tenant_id
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No tenant associated with user"
        )
    
    summary = FinancialSummaryService.get_tenant_drivers_summary(db, tenant_id)
    
    # Convert Decimal to float for JSON
    for driver in summary:
        driver['balances'] = [
            {'currency': b['currency'], 'balance': float(b['balance'])}
            for b in driver['balances']
        ]
        driver['total_unsettled_per_currency'] = [
            {'currency': u['currency'], 'balance': float(u['balance'])}
            for u in driver['total_unsettled_per_currency']
        ]
    
    return {
        'tenant_id': tenant_id,
        'drivers': summary
    }


@router.get("/tenant/driver/{driver_id}/financial-details")
def get_tenant_driver_financial_details(
    driver_id: int,
    db: Session = Depends(get_db),
    current_user: AppUser = Depends(get_session_user)
):
    """
    Get detailed financial information for a specific driver.
    
    Auth: Session (x_session_id header)
    """
    # Verify user is tenant admin
    if current_user.role not in ['TENANT_ADMIN', 'SUPER_ADMIN']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only tenant admins can access this endpoint"
        )
    
    tenant_id = current_user.tenant_id
    
    # Verify driver belongs to tenant
    driver = (
        db.query(DriverProfile)
        .filter(
            DriverProfile.driver_id == driver_id,
            DriverProfile.tenant_id == tenant_id
        )
        .first()
    )
    
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found or not in your tenant"
        )
    
    details = FinancialSummaryService.get_driver_financial_details(db, driver_id)
    
    # Convert Decimal to float
    details['balances'] = [
        {'currency': b['currency'], 'balance': float(b['balance'])}
        for b in details['balances']
    ]
    details['total_unsettled_per_currency'] = [
        {'currency': u['currency'], 'balance': float(u['balance'])}
        for u in details['total_unsettled_per_currency']
    ]
    
    return details


# ============================================
# FLEET OWNER ENDPOINTS
# ============================================

@router.get("/fleet/drivers/financial-summary")
def get_fleet_drivers_financial_summary(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_jwt_user)
):
    """
    Get financial summary of all drivers under fleet.
    
    Auth: JWT Bearer Token
    
    For fleet owner use.
    """
    user_id = current_user.get("user_id")
    user_role = current_user.get("role", "").lower()
    
    # Verify user is fleet owner
    if user_role not in ['fleet_owner', 'super_admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only fleet owners can access this endpoint"
        )
    
    # Get fleet for this owner
    fleet = (
        db.query(Fleet)
        .filter(Fleet.owner_user_id == user_id)
        .first()
    )
    
    if not fleet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No fleet found for this user"
        )
    
    summary = FinancialSummaryService.get_fleet_drivers_summary(db, fleet.fleet_id)
    
    # Convert Decimal to float
    for driver in summary:
        driver['balances'] = [
            {'currency': b['currency'], 'balance': float(b['balance'])}
            for b in driver['balances']
        ]
        driver['total_unsettled_per_currency'] = [
            {'currency': u['currency'], 'balance': float(u['balance'])}
            for u in driver['total_unsettled_per_currency']
        ]
    
    return {
        'fleet_id': fleet.fleet_id,
        'drivers': summary
    }


@router.get("/fleet/driver/{driver_id}/financial-details")
def get_fleet_driver_financial_details(
    driver_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_jwt_user)
):
    """
    Get detailed financial information for a specific driver in fleet.
    
    Auth: JWT Bearer Token
    """
    user_id = current_user.get("user_id")
    user_role = current_user.get("role", "").lower()
    
    # Verify user is fleet owner
    if user_role not in ['fleet_owner', 'super_admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only fleet owners can access this endpoint"
        )
    
    # Get fleet for this owner
    fleet = (
        db.query(Fleet)
        .filter(Fleet.owner_user_id == user_id)
        .first()
    )
    
    if not fleet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No fleet found for this user"
        )
    
    # Verify driver belongs to fleet
    fleet_driver = (
        db.query(FleetDriver)
        .filter(
            FleetDriver.fleet_id == fleet.fleet_id,
            FleetDriver.driver_id == driver_id,
            FleetDriver.end_date.is_(None)
        )
        .first()
    )
    
    if not fleet_driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found or not in your fleet"
        )
    
    details = FinancialSummaryService.get_driver_financial_details(db, driver_id)
    
    # Convert Decimal to float
    details['balances'] = [
        {'currency': b['currency'], 'balance': float(b['balance'])}
        for b in details['balances']
    ]
    details['total_unsettled_per_currency'] = [
        {'currency': u['currency'], 'balance': float(u['balance'])}
        for u in details['total_unsettled_per_currency']
    ]
    
    return details
