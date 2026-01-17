from sqlalchemy import Column, BigInteger, String, ForeignKey, TIMESTAMP, Numeric
from .base import Base
from .mixins import AuditMixin, GeoMixin

class DriverShift(Base, AuditMixin):
    __tablename__ = "driver_shift"

    shift_id = Column(BigInteger, primary_key=True)
    driver_id = Column(BigInteger, ForeignKey("app_user.user_id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(BigInteger, ForeignKey("tenant.tenant_id"), nullable=False)

    status = Column(String, nullable=False)

    started_at = Column(TIMESTAMP(timezone=True), nullable=False)
    ended_at = Column(TIMESTAMP(timezone=True))

    last_latitude = Column(Numeric(9,6))
    last_longitude = Column(Numeric(9,6))


class DriverLocation(Base, GeoMixin):
    __tablename__ = "driver_location"

    driver_id = Column(BigInteger, ForeignKey("app_user.user_id", ondelete="CASCADE"), primary_key=True)
    last_updated = Column(TIMESTAMP(timezone=True), nullable=False)


class DriverLocationHistory(Base, GeoMixin):
    __tablename__ = "driver_location_history"

    id = Column(BigInteger, primary_key=True)
    driver_id = Column(BigInteger, ForeignKey("app_user.user_id", ondelete="CASCADE"), nullable=False)
    recorded_at = Column(TIMESTAMP(timezone=True), nullable=False)
