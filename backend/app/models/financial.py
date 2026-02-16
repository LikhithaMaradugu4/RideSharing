"""
Financial Models for Commission, Payout, and Dispute management.

Tables:
- commission_config: Commission rates for platform/tenant/fleet
- payout_request: Driver payout/settlement requests
- payout_request_item: Individual ledger entries in a payout request
- ride_payment_dispute: Payment disputes raised by riders/drivers
"""

from sqlalchemy import Column, BigInteger, String, ForeignKey, Numeric, TIMESTAMP, CHAR, Text, Boolean
from sqlalchemy.sql import func
from .base import Base


class CommissionConfig(Base):
    """
    Commission configuration table.
    
    commission_type: 'platform' | 'tenant' | 'fleet'
    
    All percentages are calculated from TOTAL FARE (F).
    percentage is stored as decimal (e.g., 0.20 = 20%)
    """
    __tablename__ = "commission_config"

    id = Column(BigInteger, primary_key=True)
    
    commission_type = Column(Text, nullable=False)  # platform | tenant | fleet
    
    tenant_id = Column(BigInteger, ForeignKey("tenant.tenant_id"), nullable=True)
    city_id = Column(BigInteger, ForeignKey("city.city_id"), nullable=True)
    vehicle_category = Column(Text, nullable=True)
    
    fixed_amount = Column(Numeric(10, 2), default=0)
    percentage = Column(Numeric(5, 4), default=0)  # 0.0000 to 1.0000
    
    currency = Column(CHAR(3), default='INR')
    
    is_active = Column(Boolean, default=True)
    
    effective_from = Column(TIMESTAMP(timezone=True), nullable=False)
    effective_to = Column(TIMESTAMP(timezone=True), nullable=True)
    
    created_on = Column(TIMESTAMP(timezone=True), server_default=func.now())
    created_by = Column(BigInteger, ForeignKey("app_user.user_id"), nullable=True)
    updated_on = Column(TIMESTAMP(timezone=True))
    updated_by = Column(BigInteger, ForeignKey("app_user.user_id"), nullable=True)


class PayoutRequest(Base):
    """
    Driver payout/settlement requests.
    
    payout_type: 'single' | 'batch' | 'full'
    status: 'requested' | 'approved' | 'rejected' | 'processing' | 'completed'
    
    For immediate settlement model, status goes directly to 'completed'.
    """
    __tablename__ = "payout_request"

    id = Column(BigInteger, primary_key=True)
    
    driver_id = Column(BigInteger, ForeignKey("app_user.user_id"), nullable=False)
    
    total_amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(CHAR(3), nullable=False, default='INR')
    
    payout_type = Column(Text, nullable=False)  # single | batch | full
    
    status = Column(Text, default='requested')
    # requested, approved, rejected, processing, completed
    
    payment_reference = Column(Text, nullable=True)  # bank/UPI txn id
    
    processed_by = Column(BigInteger, ForeignKey("app_user.user_id"), nullable=True)
    processed_on = Column(TIMESTAMP(timezone=True), nullable=True)
    
    created_on = Column(TIMESTAMP(timezone=True), server_default=func.now())


class PayoutRequestItem(Base):
    """
    Individual ledger entries included in a payout request.
    
    Links payout_request to driver_ledger entries.
    """
    __tablename__ = "payout_request_item"

    id = Column(BigInteger, primary_key=True)
    
    payout_request_id = Column(BigInteger, ForeignKey("payout_request.id"), nullable=False)
    ledger_id = Column(BigInteger, ForeignKey("driver_ledger.entry_id"), nullable=False)
    
    created_on = Column(TIMESTAMP(timezone=True), server_default=func.now())


class RidePaymentDispute(Base):
    """
    Payment disputes raised by riders or drivers.
    
    raised_by: 'rider' | 'driver'
    status: 'open' | 'under_review' | 'resolved' | 'rejected'
    """
    __tablename__ = "ride_payment_dispute"

    id = Column(BigInteger, primary_key=True)
    
    ride_id = Column(BigInteger, ForeignKey("trip.trip_id"), nullable=False)
    driver_id = Column(BigInteger, ForeignKey("app_user.user_id"), nullable=False)
    
    raised_by = Column(Text, nullable=False)  # rider | driver
    
    reason = Column(Text, nullable=True)
    
    status = Column(Text, default='open')
    # open, under_review, resolved, rejected
    
    resolved_by = Column(BigInteger, ForeignKey("app_user.user_id"), nullable=True)
    resolved_on = Column(TIMESTAMP(timezone=True), nullable=True)
    
    created_on = Column(TIMESTAMP(timezone=True), server_default=func.now())
