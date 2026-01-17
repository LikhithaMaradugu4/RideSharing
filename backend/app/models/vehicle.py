from sqlalchemy import Column, BigInteger, String, ForeignKey, TIMESTAMP
from .base import Base
from .mixins import AuditMixin, StatusMixin

class Vehicle(Base, AuditMixin, StatusMixin):
    __tablename__ = "vehicle"

    vehicle_id = Column(BigInteger, primary_key=True)
    tenant_id = Column(BigInteger, ForeignKey("tenant.tenant_id"), nullable=False)
    fleet_id = Column(BigInteger, ForeignKey("fleet.fleet_id"), nullable=False)

    category = Column(String, ForeignKey("lu_vehicle_category.category_code"), nullable=False)
    registration_no = Column(String(50), unique=True, nullable=False)


class VehicleDocument(Base, AuditMixin):
    __tablename__ = "vehicle_document"

    document_id = Column(BigInteger, primary_key=True)
    vehicle_id = Column(BigInteger, ForeignKey("vehicle.vehicle_id", ondelete="CASCADE"), nullable=False)

    document_type = Column(String(50), nullable=False)
    file_url = Column(String, nullable=False)
    verification_status = Column(String, ForeignKey("lu_approval_status.status_code"), nullable=False)

    verified_by = Column(BigInteger)
    verified_on = Column(TIMESTAMP(timezone=True))


class DriverVehicleAssignment(Base, AuditMixin):
    __tablename__ = "driver_vehicle_assignment"

    assignment_id = Column(BigInteger, primary_key=True)
    driver_id = Column(BigInteger, ForeignKey("app_user.user_id"), nullable=False)
    vehicle_id = Column(BigInteger, ForeignKey("vehicle.vehicle_id"), nullable=False)

    start_time = Column(TIMESTAMP(timezone=True), nullable=False)
    end_time = Column(TIMESTAMP(timezone=True))
