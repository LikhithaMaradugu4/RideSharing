from sqlalchemy import (
    Column, String, BigInteger, ForeignKey, Boolean, TIMESTAMP
)
from sqlalchemy.orm import relationship
from .base import Base
from .mixins import AuditMixin, StatusMixin

class AppUser(Base, AuditMixin, StatusMixin):
    __tablename__ = "app_user"

    user_id = Column(BigInteger, primary_key=True)

    full_name = Column(String(150), nullable=False)
    phone = Column(String(15), unique=True)
    email = Column(String(150), unique=True)

    country_code = Column(String(2), ForeignKey("country.country_code"), nullable=False)
    city_id = Column(BigInteger, ForeignKey("city.city_id"))

    gender = Column(String, ForeignKey("lu_gender.gender_code"))
    role = Column(String, ForeignKey("lu_tenant_role.role_code"), nullable=False)
    status = Column(String, ForeignKey("lu_account_status.status_code"), nullable=False)

    auth = relationship("UserAuth", back_populates="user", uselist=False)
    sessions = relationship("UserSession", back_populates="user")
    kyc_records = relationship("UserKYC", back_populates="user")


class UserAuth(Base, AuditMixin):
    __tablename__ = "user_auth"

    user_id = Column(BigInteger, ForeignKey("app_user.user_id", ondelete="CASCADE"), primary_key=True)
    password_hash = Column(String, nullable=False)
    is_locked = Column(Boolean, nullable=False, default=False)
    last_password_change = Column(TIMESTAMP(timezone=True))

    user = relationship("AppUser", back_populates="auth")


class UserSession(Base, AuditMixin):
    __tablename__ = "user_session"

    session_id = Column(String, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("app_user.user_id", ondelete="CASCADE"), nullable=False)

    login_at = Column(TIMESTAMP(timezone=True), nullable=False)
    logout_at = Column(TIMESTAMP(timezone=True))
    ip_address = Column(String)
    user_agent = Column(String)

    user = relationship("AppUser", back_populates="sessions")


class UserKYC(Base, AuditMixin):
    __tablename__ = "user_kyc"

    kyc_id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("app_user.user_id", ondelete="CASCADE"), nullable=False)

    document_type = Column(String(50), nullable=False)
    document_number = Column(String(100), nullable=False)
    file_url = Column(String, nullable=True)
    verification_status = Column(String, ForeignKey("lu_approval_status.status_code"), nullable=False)

    verified_by = Column(BigInteger)
    verified_on = Column(TIMESTAMP(timezone=True))

    user = relationship("AppUser", back_populates="kyc_records")
