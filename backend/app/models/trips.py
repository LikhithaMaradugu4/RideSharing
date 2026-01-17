from sqlalchemy import Column, BigInteger, String, ForeignKey, Numeric, TIMESTAMP,DECIMAL,TEXT
from .base import Base
from .mixins import AuditMixin
from sqlalchemy.sql import func


class RideRequest(Base):
    __tablename__ = "ride_request"

    request_id = Column(BigInteger, primary_key=True, index=True)

    rider_id = Column(
        BigInteger,
        ForeignKey("app_user.user_id", ondelete="CASCADE"),
        nullable=False
    )

    city_id = Column(
        BigInteger,
        ForeignKey("city.city_id"),
        nullable=False
    )

    pickup_lat = Column(DECIMAL(9, 6), nullable=False)
    pickup_lng = Column(DECIMAL(9, 6), nullable=False)

    drop_lat = Column(DECIMAL(9, 6), nullable=False)
    drop_lng = Column(DECIMAL(9, 6), nullable=False)

    status = Column(TEXT, nullable=False)  # REQUESTED, CONFIRMED, EXPIRED

    created_on = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )





class Trip(Base, AuditMixin):
    __tablename__ = "trip"

    trip_id = Column(BigInteger, primary_key=True)
    tenant_id = Column(BigInteger, ForeignKey("tenant.tenant_id"), nullable=False)

    rider_id = Column(BigInteger, ForeignKey("app_user.user_id"), nullable=False)
    driver_id = Column(BigInteger, ForeignKey("app_user.user_id"))
    vehicle_id = Column(BigInteger, ForeignKey("vehicle.vehicle_id"))

    city_id = Column(BigInteger, ForeignKey("city.city_id"), nullable=False)
    zone_id = Column(BigInteger, ForeignKey("zone.zone_id"))

    pickup_lat = Column(Numeric(9,6), nullable=False)
    pickup_lng = Column(Numeric(9,6), nullable=False)
    drop_lat = Column(Numeric(9,6))
    drop_lng = Column(Numeric(9,6))

    status = Column(String, ForeignKey("lu_trip_status.status_code"), nullable=False)

    requested_at = Column(TIMESTAMP(timezone=True), nullable=False)
    assigned_at = Column(TIMESTAMP(timezone=True))
    picked_up_at = Column(TIMESTAMP(timezone=True))
    completed_at = Column(TIMESTAMP(timezone=True))
    cancelled_at = Column(TIMESTAMP(timezone=True))

    fare_amount = Column(Numeric(10,2))
    driver_earning = Column(Numeric(10,2))
    platform_fee = Column(Numeric(10,2))

    payment_status = Column(String, ForeignKey("lu_payment_status.status_code"))
