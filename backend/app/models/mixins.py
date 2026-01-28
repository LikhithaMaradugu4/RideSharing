from sqlalchemy import Column, TIMESTAMP,Numeric, BigInteger,String, func


class AuditMixin:
    created_by = Column(BigInteger)
    created_on = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    updated_by = Column(BigInteger)
    updated_on = Column(TIMESTAMP(timezone=True), onupdate=func.now())


class StatusMixin:
    status = Column(String, nullable=False)


class GeoMixin:
    latitude = Column(Numeric(9, 6))
    longitude = Column(Numeric(9, 6))


