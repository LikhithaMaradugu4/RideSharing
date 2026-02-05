from sqlalchemy import Column, BigInteger, String, ForeignKey, Numeric, TIMESTAMP, CHAR, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from .base import Base
from .mixins import AuditMixin

class Payment(Base, AuditMixin):
    __tablename__ = "payment"

    payment_id = Column(BigInteger, primary_key=True)
    trip_id = Column(BigInteger, ForeignKey("trip.trip_id"), nullable=False)

    amount = Column(Numeric(10,2), nullable=False)
    currency = Column(String(3), nullable=False)
    payment_mode = Column(String, nullable=False)
    status = Column(String, ForeignKey("lu_payment_status.status_code"), nullable=False)

    # Payment gateway integration fields
    gateway_name = Column(Text)
    gateway_order_id = Column(Text)
    gateway_payment_id = Column(Text, unique=True)
    gateway_signature = Column(Text)
    gateway_payload = Column(JSONB)
    
    # Cash payment confirmation fields
    confirmed_by_driver_id = Column(BigInteger, ForeignKey("app_user.user_id"))
    confirmed_at = Column(TIMESTAMP(timezone=True))


class DriverWallet(Base):
    __tablename__ = "driver_wallet"
    __table_args__ = (
        {'extend_existing': True}
    )

    driver_id = Column(BigInteger, ForeignKey("app_user.user_id"), primary_key=True, nullable=False)
    currency = Column(CHAR(3), primary_key=True, nullable=False)
    balance = Column(Numeric(12,2), nullable=False, default=0)

    created_on = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_on = Column(TIMESTAMP(timezone=True))


class PlatformWallet(Base):
    __tablename__ = "platform_wallet"

    currency = Column(CHAR(3), primary_key=True)
    balance = Column(Numeric(14,2), nullable=False, default=0)

    created_on = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_on = Column(TIMESTAMP(timezone=True))


class TenantWallet(Base):
    __tablename__ = "tenant_wallet"
    __table_args__ = (
        {'extend_existing': True}
    )

    tenant_id = Column(BigInteger, ForeignKey("tenant.tenant_id"), primary_key=True, nullable=False)
    currency = Column(CHAR(3), primary_key=True, nullable=False)
    balance = Column(Numeric(12,2), nullable=False, default=0)

    created_on = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_on = Column(TIMESTAMP(timezone=True))


class TenantSettlement(Base, AuditMixin):
    __tablename__ = "tenant_settlement"

    settlement_id = Column(BigInteger, primary_key=True)
    tenant_id = Column(BigInteger, ForeignKey("tenant.tenant_id"), nullable=False)

    amount = Column(Numeric(12,2), nullable=False)
    status = Column(String, ForeignKey("lu_settlement_status.status_code"), nullable=False)

    requested_at = Column(TIMESTAMP(timezone=True), nullable=False)
    processed_at = Column(TIMESTAMP(timezone=True))


class Refund(Base, AuditMixin):
    __tablename__ = "refund"

    refund_id = Column(BigInteger, primary_key=True)
    payment_id = Column(BigInteger, ForeignKey("payment.payment_id"), nullable=False)

    amount = Column(Numeric(10,2), nullable=False)
    reason = Column(String)
