from sqlalchemy import Column, BigInteger, String, ForeignKey, Numeric, TIMESTAMP, Text, ARRAY
from sqlalchemy.orm import relationship
from .base import Base
from .mixins import AuditMixin, StatusMixin

class DriverProfile(Base, AuditMixin):
    __tablename__ = "driver_profile"

    driver_id = Column(BigInteger, ForeignKey("app_user.user_id", ondelete="CASCADE"), primary_key=True)
    tenant_id = Column(BigInteger, ForeignKey("tenant.tenant_id"), nullable=False)

    driver_type = Column(String, ForeignKey("lu_driver_type.type_code"), nullable=False)
    approval_status = Column(String, ForeignKey("lu_approval_status.status_code"), nullable=False)
    rating = Column(Numeric(3,2), default=5.00)
    alternate_phone_number = Column(String(15), nullable=True)
    allowed_vehicle_categories = Column(ARRAY(String), nullable=True)


class Fleet(Base, AuditMixin, StatusMixin):
    __tablename__ = "fleet"

    fleet_id = Column(BigInteger, primary_key=True)
    tenant_id = Column(BigInteger, ForeignKey("tenant.tenant_id"), nullable=False)
    owner_user_id = Column(BigInteger, ForeignKey("app_user.user_id"), nullable=False)

    fleet_name = Column(String(150), nullable=False)
    fleet_type = Column(String, ForeignKey("lu_fleet_type.fleet_type_code"), nullable=False, default="BUSINESS")
    approval_status = Column(String, ForeignKey("lu_approval_status.status_code"), nullable=False)

    documents = relationship("FleetDocument", backref="fleet")


class FleetDriver(Base, AuditMixin):
    __tablename__ = "fleet_driver"

    id = Column(BigInteger, primary_key=True)
    fleet_id = Column(BigInteger, ForeignKey("fleet.fleet_id", ondelete="CASCADE"), nullable=False)
    driver_id = Column(BigInteger, ForeignKey("app_user.user_id", ondelete="CASCADE"), nullable=False)

    start_date = Column(TIMESTAMP(timezone=True), nullable=False)
    end_date = Column(TIMESTAMP(timezone=True))


class FleetDocument(Base, AuditMixin):
    __tablename__ = "fleet_document"

    document_id = Column(BigInteger, primary_key=True)
    fleet_id = Column(BigInteger, ForeignKey("fleet.fleet_id", ondelete="CASCADE"), nullable=False)
    document_type = Column(String(50), nullable=False)
    file_url = Column(Text, nullable=False)
    verification_status = Column(String, ForeignKey("lu_approval_status.status_code"), nullable=False)
    verified_by = Column(BigInteger, ForeignKey("app_user.user_id"), nullable=True)
    verified_on = Column(TIMESTAMP(timezone=True), nullable=True)


class FleetCity(Base, AuditMixin):
    __tablename__ = "fleet_city"

    fleet_id = Column(BigInteger, ForeignKey("fleet.fleet_id", ondelete="CASCADE"), primary_key=True)
    city_id = Column(BigInteger, ForeignKey("city.city_id"), primary_key=True)


class FleetDriverInvite(Base):
    __tablename__ = "fleet_driver_invite"

    invite_id = Column(BigInteger, primary_key=True)
    fleet_id = Column(BigInteger, ForeignKey("fleet.fleet_id", ondelete="CASCADE"), nullable=False)
    driver_id = Column(BigInteger, ForeignKey("app_user.user_id", ondelete="CASCADE"), nullable=False)

    status = Column(String, nullable=False, default="PENDING")  # PENDING, ACCEPTED, REJECTED, EXPIRED
    invited_at = Column(TIMESTAMP(timezone=True), nullable=False)
    responded_at = Column(TIMESTAMP(timezone=True))
