from sqlalchemy import Column, BigInteger, String, ForeignKey, Numeric, TIMESTAMP
from .base import Base
from .mixins import AuditMixin, StatusMixin

class DriverProfile(Base, AuditMixin):
    __tablename__ = "driver_profile"

    driver_id = Column(BigInteger, ForeignKey("app_user.user_id", ondelete="CASCADE"), primary_key=True)
    tenant_id = Column(BigInteger, ForeignKey("tenant.tenant_id"), nullable=False)

    driver_type = Column(String, ForeignKey("lu_driver_type.type_code"), nullable=False)
    approval_status = Column(String, ForeignKey("lu_approval_status.status_code"), nullable=False)
    rating = Column(Numeric(3,2), default=5.00)


class Fleet(Base, AuditMixin, StatusMixin):
    __tablename__ = "fleet"

    fleet_id = Column(BigInteger, primary_key=True)
    tenant_id = Column(BigInteger, ForeignKey("tenant.tenant_id"), nullable=False)
    owner_user_id = Column(BigInteger, ForeignKey("app_user.user_id"), nullable=False)

    fleet_name = Column(String(150), nullable=False)
    approval_status = Column(String, ForeignKey("lu_approval_status.status_code"), nullable=False)


class FleetDriver(Base, AuditMixin):
    __tablename__ = "fleet_driver"

    id = Column(BigInteger, primary_key=True)
    fleet_id = Column(BigInteger, ForeignKey("fleet.fleet_id", ondelete="CASCADE"), nullable=False)
    driver_id = Column(BigInteger, ForeignKey("app_user.user_id", ondelete="CASCADE"), nullable=False)

    start_date = Column(TIMESTAMP(timezone=True), nullable=False)
    end_date = Column(TIMESTAMP(timezone=True))
