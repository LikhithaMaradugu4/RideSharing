from sqlalchemy import Column, BigInteger, String, ForeignKey, Numeric, TIMESTAMP
from .base import Base
from .mixins import AuditMixin

class FareConfig(Base, AuditMixin):
    __tablename__ = "fare_config"

    fare_id = Column(BigInteger, primary_key=True)
    tenant_id = Column(BigInteger, ForeignKey("tenant.tenant_id"), nullable=False)
    city_id = Column(BigInteger, ForeignKey("city.city_id"), nullable=False)
    vehicle_category = Column(String, ForeignKey("lu_vehicle_category.category_code"), nullable=False)

    base_fare = Column(Numeric(10,2), nullable=False)
    per_km = Column(Numeric(10,2), nullable=False)
    per_minute = Column(Numeric(10,2), nullable=False)
    minimum_fare = Column(Numeric(10,2), nullable=False)


class PricingTimeRule(Base, AuditMixin):
    __tablename__ = "pricing_time_rule"

    rule_id = Column(BigInteger, primary_key=True)
    tenant_id = Column(BigInteger, ForeignKey("tenant.tenant_id"), nullable=False)
    city_id = Column(BigInteger, ForeignKey("city.city_id"), nullable=False)

    rule_type = Column(String(50), nullable=False)
    start_time = Column(TIMESTAMP, nullable=False)
    end_time = Column(TIMESTAMP, nullable=False)
    multiplier = Column(Numeric(5,2), nullable=False)


class SurgeZone(Base, AuditMixin):
    __tablename__ = "surge_zone"

    surge_zone_id = Column(BigInteger, primary_key=True)
    zone_id = Column(BigInteger, ForeignKey("zone.zone_id"), nullable=False)


class SurgeEvent(Base, AuditMixin):
    __tablename__ = "surge_event"

    surge_id = Column(BigInteger, primary_key=True)
    tenant_id = Column(BigInteger, ForeignKey("tenant.tenant_id"), nullable=False)
    surge_zone_id = Column(BigInteger, ForeignKey("surge_zone.surge_zone_id"), nullable=False)

    multiplier = Column(Numeric(5,2), nullable=False)
    demand_index = Column(BigInteger)
    supply_index = Column(BigInteger)

    started_at = Column(TIMESTAMP(timezone=True), nullable=False)
    ended_at = Column(TIMESTAMP(timezone=True))
