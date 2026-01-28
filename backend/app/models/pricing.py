from sqlalchemy import Column, BigInteger, String, ForeignKey, Numeric, TIMESTAMP, Text, Boolean, UniqueConstraint
from .base import Base
from .mixins import AuditMixin

class FareConfig(Base, AuditMixin):
    __tablename__ = "fare_config"
    __table_args__ = (
        UniqueConstraint('city_id', 'vehicle_category', name='uq_fare_config_city_vehicle'),
    )

    fare_id = Column(BigInteger, primary_key=True)
    city_id = Column(BigInteger, ForeignKey("city.city_id"), nullable=False)
    vehicle_category = Column(String, ForeignKey("lu_vehicle_category.category_code"), nullable=False)

    base_fare = Column(Numeric(10,2), nullable=False)
    per_km = Column(Numeric(10,2), nullable=False)
    per_minute = Column(Numeric(10,2), nullable=False)
    minimum_fare = Column(Numeric(10,2), nullable=False)


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
