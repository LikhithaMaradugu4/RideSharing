from sqlalchemy import Column, BigInteger, String, ForeignKey, Numeric, TIMESTAMP, Text, Boolean, UniqueConstraint, CHAR
from sqlalchemy.sql import func
from .base import Base
from .mixins import AuditMixin

class FareConfig(Base):
    __tablename__ = "fare_config"
    __table_args__ = (
        UniqueConstraint('city_id', 'vehicle_category', 'effective_from', name='uq_fare_config_city_vehicle_effective'),
    )

    fare_config_id = Column(BigInteger, primary_key=True)
    city_id = Column(BigInteger, ForeignKey("city.city_id"), nullable=False)
    vehicle_category = Column(Text, nullable=False)  # BIKE / AUTO / CAB / XL
    currency = Column(CHAR(3), nullable=False)  # Frozen from city

    base_fare = Column(Numeric(10,2), nullable=False)
    per_km_rate = Column(Numeric(10,2), nullable=False)
    per_min_rate = Column(Numeric(10,2), nullable=False)

    minimum_fare = Column(Numeric(10,2))
    booking_fee = Column(Numeric(10,2))

    surge_allowed = Column(Boolean, nullable=False, default=True)
    night_charge_pct = Column(Numeric(5,2))

    effective_from = Column(TIMESTAMP(timezone=True), nullable=False)
    effective_to = Column(TIMESTAMP(timezone=True))

    created_by = Column(BigInteger, ForeignKey("app_user.user_id"))
    created_on = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())


class SurgeZone(Base, AuditMixin):
    __tablename__ = "surge_zone"

    surge_zone_id = Column(BigInteger, primary_key=True)
    city_id = Column(BigInteger, ForeignKey("city.city_id"), nullable=False)
    name = Column(String(120))

    boundary_geojson = Column(Text, nullable=False)
    multiplier = Column(Numeric(5,2), nullable=False)

    starts_at = Column(TIMESTAMP(timezone=True), nullable=False)
    ends_at = Column(TIMESTAMP(timezone=True), nullable=False)

    is_active = Column(Boolean, nullable=False, default=True)
