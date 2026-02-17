"""
Financial Schemas for Commission, Wallet, Ledger, and Payout operations.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime
from decimal import Decimal


# ============================================
# COMMISSION SCHEMAS
# ============================================

class CommissionRates(BaseModel):
    """Commission rates snapshot for a trip."""
    platform_percentage: Decimal
    tenant_percentage: Decimal
    fleet_percentage: Decimal
    
    class Config:
        from_attributes = True


class FareSplit(BaseModel):
    """Complete fare split breakdown."""
    total_fare: Decimal
    platform_commission: Decimal
    tenant_commission: Decimal
    fleet_commission: Decimal
    driver_earning: Decimal
    currency: str
    
    class Config:
        from_attributes = True


# ============================================
# WALLET SCHEMAS
# ============================================

class WalletBalance(BaseModel):
    """Single currency wallet balance."""
    currency: str
    balance: Decimal
    
    class Config:
        from_attributes = True


class DriverWalletResponse(BaseModel):
    """Driver wallet summary."""
    driver_id: int
    balances: List[WalletBalance]
    total_unsettled: List[WalletBalance]
    is_blocked: bool = False
    
    class Config:
        from_attributes = True


class TenantWalletResponse(BaseModel):
    """Tenant wallet summary."""
    tenant_id: int
    balances: List[WalletBalance]
    
    class Config:
        from_attributes = True


class FleetWalletResponse(BaseModel):
    """Fleet wallet summary."""
    fleet_id: int
    balances: List[WalletBalance]
    
    class Config:
        from_attributes = True


# ============================================
# LEDGER SCHEMAS
# ============================================

class LedgerEntry(BaseModel):
    """Single ledger entry."""
    entry_id: int
    trip_id: Optional[int]
    currency: str
    amount: Decimal
    entry_type: str  # CREDIT | DEBIT
    reason: Optional[str]
    settlement_status: str  # unsettled | settled
    created_on: datetime
    
    class Config:
        from_attributes = True


class DriverLedgerResponse(BaseModel):
    """Driver ledger response with pagination."""
    driver_id: int
    currency: str
    total: int
    page: int
    page_size: int
    entries: List[LedgerEntry]
    
    class Config:
        from_attributes = True


class LedgerListResponse(BaseModel):
    """Paginated ledger response."""
    entries: List[LedgerEntry]
    total: int
    page: int
    page_size: int
    
    class Config:
        from_attributes = True


class LedgerFilterParams(BaseModel):
    """Ledger query filters."""
    currency: Optional[str] = None
    settlement_status: Optional[str] = None  # unsettled | settled
    page: int = 1
    page_size: int = 20


# ============================================
# PAYOUT/SETTLEMENT SCHEMAS
# ============================================

class PayoutRequest(BaseModel):
    """Driver payout request."""
    type: Literal['single', 'batch', 'full']
    trip_ids: Optional[List[int]] = None
    currency: str = 'INR'


class PayoutRequestCreate(BaseModel):
    """Create payout/settlement request (trip-based)."""
    trip_ids: List[int]  # Trip IDs to settle
    currency: str = 'INR'


class PayoutRequestResponse(BaseModel):
    """Payout request response."""
    payout_request_id: int
    total_amount: float
    entries_settled: int
    message: str


class PayoutResponse(BaseModel):
    """Payout request response."""
    payout_id: int
    driver_id: int
    total_amount: Decimal
    currency: str
    payout_type: str
    status: str
    trips_settled: int
    ledger_entries_settled: int
    created_on: datetime
    
    class Config:
        from_attributes = True


class SettlementResult(BaseModel):
    """Settlement operation result."""
    success: bool
    payout_id: Optional[int]
    total_amount: Decimal
    currency: str
    trips_settled: int
    ledger_entries_settled: int
    new_wallet_balance: Decimal
    message: str
    
    class Config:
        from_attributes = True


# ============================================
# TRIP FINANCIAL SCHEMAS
# ============================================

class TripFinancialInfo(BaseModel):
    """Trip with financial details."""
    trip_id: int
    fare_amount: Decimal
    driver_earning: Decimal
    platform_fee: Decimal
    tenant_commission: Decimal
    fleet_commission: Decimal
    payment_mode: Optional[str]
    payment_status: Optional[str]
    settlement_status: str
    currency: str
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class DriverTripFinancialResponse(BaseModel):
    """Driver trips with financial details."""
    driver_id: int
    total: int
    page: int
    page_size: int
    trips: List[TripFinancialInfo]
    
    class Config:
        from_attributes = True


class TripListResponse(BaseModel):
    """Paginated trip response."""
    trips: List[TripFinancialInfo]
    total: int
    page: int
    page_size: int
    
    class Config:
        from_attributes = True


# ============================================
# FINANCIAL SUMMARY SCHEMAS
# ============================================

class DriverFinancialSummary(BaseModel):
    """Driver financial summary for admin view."""
    driver_id: int
    driver_name: str
    balances: List[WalletBalance]
    total_unsettled_per_currency: List[WalletBalance]
    is_blocked: bool
    
    class Config:
        from_attributes = True


class DriversFinancialListResponse(BaseModel):
    """List of driver financial summaries."""
    drivers: List[DriverFinancialSummary]
    total: int
    
    class Config:
        from_attributes = True


# ============================================
# PAYMENT CONFIRMATION SCHEMAS
# ============================================

class PaymentConfirmationRequest(BaseModel):
    """Payment confirmation request."""
    trip_id: int
    payment_mode: Literal['cash', 'online']
    amount: Decimal
    gateway_payment_id: Optional[str] = None  # For online payments


class PaymentConfirmationResponse(BaseModel):
    """Payment confirmation response."""
    trip_id: int
    status: str
    fare_split: FareSplit
    message: str
    
    class Config:
        from_attributes = True


# ============================================
# DISPUTE SCHEMAS
# ============================================

class DisputeCreateRequest(BaseModel):
    """Create payment dispute."""
    ride_id: int
    reason: str


class DisputeResponse(BaseModel):
    """Dispute response."""
    id: int
    ride_id: int
    driver_id: int
    raised_by: str
    reason: Optional[str]
    status: str
    resolved_by: Optional[int]
    resolved_on: Optional[datetime]
    created_on: datetime
    
    class Config:
        from_attributes = True
