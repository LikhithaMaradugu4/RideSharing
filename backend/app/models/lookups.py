from sqlalchemy import Column, String
from .base import Base

class LuTenantRole(Base):
    __tablename__ = "lu_tenant_role"
    role_code = Column(String, primary_key=True)

class LuGender(Base):
    __tablename__ = "lu_gender"
    gender_code = Column(String, primary_key=True)

class LuApprovalStatus(Base):
    __tablename__ = "lu_approval_status"
    status_code = Column(String, primary_key=True)

class LuAccountStatus(Base):
    __tablename__ = "lu_account_status"
    status_code = Column(String, primary_key=True)

class LuDriverType(Base):
    __tablename__ = "lu_driver_type"
    type_code = Column(String, primary_key=True)

class LuVehicleCategory(Base):
    __tablename__ = "lu_vehicle_category"
    category_code = Column(String, primary_key=True)

class LuVehicleStatus(Base):
    __tablename__ = "lu_vehicle_status"
    status_code = Column(String, primary_key=True)

class LuTripStatus(Base):
    __tablename__ = "lu_trip_status"
    status_code = Column(String, primary_key=True)

class LuPaymentStatus(Base):
    __tablename__ = "lu_payment_status"
    status_code = Column(String, primary_key=True)

class LuSupportTicketStatus(Base):
    __tablename__ = "lu_support_ticket_status"
    status_code = Column(String, primary_key=True)

class LuSettlementStatus(Base):
    __tablename__ = "lu_settlement_status"
    status_code = Column(String, primary_key=True)

class LuCouponType(Base):
    __tablename__ = "lu_coupon_type"
    type_code = Column(String, primary_key=True)
