from sqlalchemy import Column, BigInteger, String, ForeignKey, Numeric, TIMESTAMP
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


class DriverWallet(Base, AuditMixin):
    __tablename__ = "driver_wallet"

    driver_id = Column(BigInteger, ForeignKey("app_user.user_id"), primary_key=True)
    balance = Column(Numeric(12,2), nullable=False, default=0)


class PlatformWallet(Base, AuditMixin):
    __tablename__ = "platform_wallet"

    id = Column(BigInteger, primary_key=True)
    balance = Column(Numeric(14,2), nullable=False, default=0)


class TenantWallet(Base, AuditMixin):
    __tablename__ = "tenant_wallet"

    tenant_id = Column(BigInteger, ForeignKey("tenant.tenant_id"), primary_key=True)
    balance = Column(Numeric(12,2), nullable=False, default=0)


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
