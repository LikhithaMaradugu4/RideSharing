from sqlalchemy import Column, BigInteger, String, ForeignKey, Numeric
from .base import Base
from .mixins import AuditMixin

class PlatformLedger(Base, AuditMixin):
    __tablename__ = "platform_ledger"

    entry_id = Column(BigInteger, primary_key=True)
    trip_id = Column(BigInteger, ForeignKey("trip.trip_id"))

    amount = Column(Numeric(12,2), nullable=False)
    entry_type = Column(String, nullable=False)


class TenantLedger(Base, AuditMixin):
    __tablename__ = "tenant_ledger"

    entry_id = Column(BigInteger, primary_key=True)
    tenant_id = Column(BigInteger, ForeignKey("tenant.tenant_id"), nullable=False)
    trip_id = Column(BigInteger, ForeignKey("trip.trip_id"))

    amount = Column(Numeric(12,2), nullable=False)
    entry_type = Column(String, nullable=False)


class FleetLedger(Base, AuditMixin):
    __tablename__ = "fleet_ledger"

    entry_id = Column(BigInteger, primary_key=True)
    fleet_id = Column(BigInteger, ForeignKey("fleet.fleet_id"), nullable=False)
    trip_id = Column(BigInteger, ForeignKey("trip.trip_id"))

    amount = Column(Numeric(12,2), nullable=False)
    entry_type = Column(String, nullable=False)
