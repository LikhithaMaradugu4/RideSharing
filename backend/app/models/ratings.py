from sqlalchemy import Column, BigInteger, String, ForeignKey, Integer, TIMESTAMP, Numeric, Text, UniqueConstraint
from sqlalchemy.sql import func
from .base import Base


class TripRating(Base):
    __tablename__ = "trip_ratings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trip_id = Column(Integer, ForeignKey("trip.trip_id"), nullable=False)

    rater_user_id = Column(Integer, ForeignKey("app_user.user_id"), nullable=False)
    rated_user_id = Column(Integer, ForeignKey("app_user.user_id"), nullable=False)

    rating = Column(Integer, nullable=False)
    feedback = Column(Text, nullable=True)
    role_type = Column(String(10), nullable=True)  # 'DRIVER' or 'RIDER'
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint('trip_id', 'rater_user_id', name='uq_trip_rater'),
    )


class DriverRatingSummary(Base):
    __tablename__ = "driver_rating_summary"

    driver_id = Column(BigInteger, ForeignKey("app_user.user_id"), primary_key=True)
    avg_rating = Column(Numeric(3,2))
    total_ratings = Column(Integer)
    updated_on = Column(TIMESTAMP(timezone=True))


class RiderRatingSummary(Base):
    __tablename__ = "rider_rating_summary"

    rider_id = Column(BigInteger, ForeignKey("app_user.user_id"), primary_key=True)
    avg_rating = Column(Numeric(3,2))
    total_ratings = Column(Integer)
    updated_on = Column(TIMESTAMP(timezone=True))


class TenantRatingSummary(Base):
    __tablename__ = "tenant_rating_summary"

    tenant_id = Column(BigInteger, ForeignKey("tenant.tenant_id"), primary_key=True)
    avg_rating = Column(Numeric(3,2))
    total_ratings = Column(Integer)
    updated_on = Column(TIMESTAMP(timezone=True))
