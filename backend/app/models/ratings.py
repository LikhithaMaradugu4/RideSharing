from sqlalchemy import Column, BigInteger, String, ForeignKey, Integer, TIMESTAMP, Numeric
from .base import Base

class TripRating(Base):
    __tablename__ = "trip_rating"

    rating_id = Column(BigInteger, primary_key=True)
    trip_id = Column(BigInteger, ForeignKey("trip.trip_id"), nullable=False)

    rater_id = Column(BigInteger, ForeignKey("app_user.user_id"), nullable=False)
    ratee_id = Column(BigInteger, ForeignKey("app_user.user_id"), nullable=False)

    rating = Column(Integer)
    comment = Column(String)
    created_on = Column(TIMESTAMP(timezone=True), nullable=False)


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
