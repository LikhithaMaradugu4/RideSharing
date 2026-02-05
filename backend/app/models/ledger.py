from sqlalchemy import Column, BigInteger, String, ForeignKey, Numeric, CHAR, Text, TIMESTAMP
from sqlalchemy.sql import func
from .base import Base
from .mixins import AuditMixin

class PlatformLedger(Base):
    __tablename__ = "platform_ledger"

    entry_id = Column(BigInteger, primary_key=True)
    trip_id = Column(BigInteger, ForeignKey("trip.trip_id"))

    currency = Column(CHAR(3), nullable=False)
    amount = Column(Numeric(12,2), nullable=False)
    entry_type = Column(Text, nullable=False)  # CREDIT / DEBIT
    reason = Column(Text)

    created_on = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())


class TenantLedger(Base):
    __tablename__ = "tenant_ledger"

    entry_id = Column(BigInteger, primary_key=True)
    tenant_id = Column(BigInteger, ForeignKey("tenant.tenant_id"), nullable=False)
    trip_id = Column(BigInteger, ForeignKey("trip.trip_id"))

    currency = Column(CHAR(3), nullable=False)
    amount = Column(Numeric(12,2), nullable=False)
    entry_type = Column(Text, nullable=False)
    reason = Column(Text)

    created_on = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())


class FleetLedger(Base):
    __tablename__ = "fleet_ledger"

    entry_id = Column(BigInteger, primary_key=True)
    fleet_id = Column(BigInteger, ForeignKey("fleet.fleet_id"), nullable=False)
    trip_id = Column(BigInteger, ForeignKey("trip.trip_id"))

    currency = Column(CHAR(3), nullable=False)
    amount = Column(Numeric(12,2), nullable=False)
    entry_type = Column(Text, nullable=False)
    reason = Column(Text)

    created_on = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
