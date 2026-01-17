from sqlalchemy import Column, BigInteger, String, ForeignKey, TIMESTAMP
from .base import Base
from .mixins import AuditMixin

class DispatchAttempt(Base, AuditMixin):
    __tablename__ = "dispatch_attempt"

    attempt_id = Column(BigInteger, primary_key=True)
    trip_id = Column(BigInteger, ForeignKey("trip.trip_id", ondelete="CASCADE"), nullable=False)
    driver_id = Column(BigInteger, ForeignKey("app_user.user_id"), nullable=False)

    sent_at = Column(TIMESTAMP(timezone=True), nullable=False)
    responded_at = Column(TIMESTAMP(timezone=True))
    response = Column(String)


class DispatcherAssignment(Base, AuditMixin):
    __tablename__ = "dispatcher_assignment"

    assignment_id = Column(BigInteger, primary_key=True)
    dispatcher_id = Column(BigInteger, ForeignKey("app_user.user_id"), nullable=False)
    tenant_id = Column(BigInteger, ForeignKey("tenant.tenant_id"), nullable=False)
    city_id = Column(BigInteger, ForeignKey("city.city_id"))
    zone_id = Column(BigInteger, ForeignKey("zone.zone_id"))

    start_time = Column(TIMESTAMP(timezone=True), nullable=False)
    end_time = Column(TIMESTAMP(timezone=True))
