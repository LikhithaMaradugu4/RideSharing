from sqlalchemy import Column, BigInteger, ForeignKey, Boolean, String, TIMESTAMP, Numeric
from .base import Base
from .mixins import AuditMixin

class TenantAdmin(Base, AuditMixin):
    __tablename__ = "tenant_admin"

    tenant_admin_id = Column(BigInteger, primary_key=True)
    tenant_id = Column(BigInteger, ForeignKey("tenant.tenant_id"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("app_user.user_id"), nullable=False)
    is_primary = Column(Boolean, default=False)


class TenantCountry(Base, AuditMixin):
    __tablename__ = "tenant_country"

    tenant_id = Column(BigInteger, ForeignKey("tenant.tenant_id"), primary_key=True)
    country_code = Column(String(2), ForeignKey("country.country_code"), primary_key=True)


class TenantCity(Base, AuditMixin):
    __tablename__ = "tenant_city"

    tenant_id = Column(BigInteger, ForeignKey("tenant.tenant_id"), primary_key=True)
    city_id = Column(BigInteger, ForeignKey("city.city_id"), primary_key=True)


class TenantTaxRule(Base):
    __tablename__ = "tenant_tax_rule"

    tax_id = Column(BigInteger, primary_key=True)
    tenant_id = Column(BigInteger, ForeignKey("tenant.tenant_id"), nullable=False)
    country_code = Column(String(2), ForeignKey("country.country_code"), nullable=False)

    tax_type = Column(String(50))
    rate = Column(Numeric(5,2), nullable=False)
    effective_from = Column(TIMESTAMP(timezone=True), nullable=False)
    effective_to = Column(TIMESTAMP(timezone=True))
