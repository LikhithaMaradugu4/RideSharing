from sqlalchemy import Column, String, BigInteger, ForeignKey, Numeric, Text, Boolean
from .base import Base
from .mixins import AuditMixin, StatusMixin

class Tenant(Base, AuditMixin, StatusMixin):
    __tablename__ = "tenant"

    tenant_id = Column(BigInteger, primary_key=True)
    tenant_code = Column(String(50), unique=True, nullable=False)
    name = Column(String(150), unique=True, nullable=False)
    default_currency = Column(String(3), nullable=False)
    default_timezone = Column(String(50), nullable=False)

    status = Column(String, ForeignKey("lu_account_status.status_code"), nullable=False)

class Country(Base, AuditMixin):
    __tablename__ = "country"

    country_code = Column(String(2), primary_key=True)
    name = Column(String(100), nullable=False)
    phone_code = Column(String(5), nullable=False)
    default_timezone = Column(String(50), nullable=False)
    default_currency = Column(String(3), nullable=False)

class City(Base, AuditMixin):
    __tablename__ = "city"

    city_id = Column(BigInteger, primary_key=True)
    country_code = Column(String(2), ForeignKey("country.country_code"), nullable=False)
    name = Column(String(120), nullable=False)
    timezone = Column(String(50), nullable=False)
    currency = Column(String(3), nullable=False)
    boundary_geojson = Column(Text, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
