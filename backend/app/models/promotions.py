from sqlalchemy import Column, BigInteger, String, ForeignKey, Numeric, TIMESTAMP, Boolean
from .base import Base
from .mixins import AuditMixin

class Coupon(Base, AuditMixin):
    __tablename__ = "coupon"

    coupon_id = Column(BigInteger, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    coupon_type = Column(String, ForeignKey("lu_coupon_type.type_code"), nullable=False)

    value = Column(Numeric(10,2), nullable=False)
    start_date = Column(TIMESTAMP(timezone=True), nullable=False)
    end_date = Column(TIMESTAMP(timezone=True), nullable=False)

    max_uses = Column(BigInteger)
    per_user_limit = Column(BigInteger)


class CouponTenant(Base, AuditMixin):
    __tablename__ = "coupon_tenant"

    coupon_id = Column(BigInteger, ForeignKey("coupon.coupon_id"), primary_key=True)
    tenant_id = Column(BigInteger, ForeignKey("tenant.tenant_id"), primary_key=True)


class CouponRedemption(Base):
    __tablename__ = "coupon_redemption"

    redemption_id = Column(BigInteger, primary_key=True)
    coupon_id = Column(BigInteger, ForeignKey("coupon.coupon_id"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("app_user.user_id"), nullable=False)
    trip_id = Column(BigInteger, ForeignKey("trip.trip_id"))

    redeemed_at = Column(TIMESTAMP(timezone=True), nullable=False)
    created_on = Column(TIMESTAMP(timezone=True), nullable=False)


class DriverIncentiveScheme(Base, AuditMixin):
    __tablename__ = "driver_incentive_scheme"

    scheme_id = Column(BigInteger, primary_key=True)
    tenant_id = Column(BigInteger, ForeignKey("tenant.tenant_id"), nullable=False)

    name = Column(String(150), nullable=False)
    description = Column(String)

    start_date = Column(TIMESTAMP(timezone=True), nullable=False)
    end_date = Column(TIMESTAMP(timezone=True), nullable=False)

    criteria = Column(String, nullable=False)
    reward_amount = Column(Numeric(10,2), nullable=False)


class DriverIncentiveProgress(Base):
    __tablename__ = "driver_incentive_progress"

    id = Column(BigInteger, primary_key=True)
    scheme_id = Column(BigInteger, ForeignKey("driver_incentive_scheme.scheme_id"), nullable=False)
    driver_id = Column(BigInteger, ForeignKey("app_user.user_id"), nullable=False)

    progress_value = Column(BigInteger, nullable=False)
    achieved = Column(Boolean, default=False)
    updated_on = Column(TIMESTAMP(timezone=True), nullable=False)


class DriverIncentiveReward(Base):
    __tablename__ = "driver_incentive_reward"

    reward_id = Column(BigInteger, primary_key=True)
    scheme_id = Column(BigInteger, ForeignKey("driver_incentive_scheme.scheme_id"), nullable=False)
    driver_id = Column(BigInteger, ForeignKey("app_user.user_id"), nullable=False)

    amount = Column(Numeric(10,2), nullable=False)
    paid = Column(Boolean, default=False)
    created_on = Column(TIMESTAMP(timezone=True), nullable=False)
