from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime


# ============================================
# ADMIN AUTHENTICATION SCHEMAS
# ============================================

class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str


class AdminLoginResponse(BaseModel):
    message: str
    admin_type: str  # PLATFORM or TENANT
    full_name: str
    email: str
    tenant_id: Optional[int] = None


class AdminMeResponse(BaseModel):
    user_id: int
    full_name: str
    email: str
    admin_type: str  # PLATFORM or TENANT
    tenant_id: Optional[int] = None


# ============================================
# TENANT MANAGEMENT SCHEMAS
# ============================================

class TenantCreateRequest(BaseModel):
    tenant_name: str
    default_currency: str
    default_timezone: str


class TenantResponse(BaseModel):
    tenant_id: int
    tenant_code: str
    name: str
    status: str
    default_currency: str
    default_timezone: str
    created_on: datetime

    class Config:
        from_attributes = True


class TenantListResponse(BaseModel):
    tenant_id: int
    name: str
    tenant_code: str
    status: str
    default_currency: str
    default_timezone: str
    created_on: datetime

    class Config:
        from_attributes = True


class TenantAdminResponse(BaseModel):
    tenant_admin_id: int
    user_id: int
    email: str
    full_name: str
    is_primary: bool
    created_on: datetime


class TenantDetailResponse(BaseModel):
    tenant_id: int
    tenant_code: str
    name: str
    status: str
    default_currency: str
    default_timezone: str
    created_on: datetime
    primary_admin: Optional[TenantAdminResponse] = None
    document_count: int = 0

    class Config:
        from_attributes = True


# ============================================
# TENANT ADMIN MANAGEMENT SCHEMAS
# ============================================

class TenantAdminCreateRequest(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


# ============================================
# TENANT DOCUMENT SCHEMAS
# ============================================

class TenantDocumentResponse(BaseModel):
    tenant_document_id: int
    document_type: str
    file_name: str
    file_url: str
    created_on: datetime

    class Config:
        from_attributes = True


class TenantDocumentUploadResponse(BaseModel):
    tenant_document_id: int
    message: str


# ============================================
# TENANT ADMIN - DRIVER/FLEET SCHEMAS (EXISTING)
# ============================================

class PendingDriverResponse(BaseModel):
    driver_id: int
    full_name: Optional[str] = None
    phone: Optional[str] = None
    application_date: datetime
    driver_type: str


class DriverListResponse(BaseModel):
    driver_id: int
    full_name: Optional[str] = None
    phone: Optional[str] = None
    approval_status: str
    allowed_vehicle_categories: Optional[List[str]] = None
    driver_type: Optional[str] = None

    class Config:
        from_attributes = True


class DriverApproveRequest(BaseModel):
    allowed_vehicle_categories: List[str]


class DriverRejectRequest(BaseModel):
    reason: Optional[str] = None


class FleetApprovalResponse(BaseModel):
    fleet_id: int
    approval_status: str


class FleetPendingDocument(BaseModel):
    document_id: int
    document_type: str
    file_url: str
    verification_status: str

    class Config:
        from_attributes = True


class PendingFleetResponse(BaseModel):
    fleet_id: int
    fleet_name: str
    fleet_type: str
    approval_status: str
    status: str
    documents: List[FleetPendingDocument]


class FleetListResponse(BaseModel):
    fleet_id: int
    fleet_name: str
    fleet_type: str
    approval_status: str
    status: str

    class Config:
        from_attributes = True


class DriverDocumentResponse(BaseModel):
    document_id: int
    document_type: str
    document_number: str
    file_url: Optional[str]
    verification_status: str

    class Config:
        from_attributes = True


class VehicleDocumentAdminResponse(BaseModel):
    document_id: int
    document_type: str
    file_url: str
    verification_status: str

    class Config:
        from_attributes = True


# ============================================
# VEHICLE APPROVAL SCHEMAS
# ============================================

class VehiclePendingApprovalResponse(BaseModel):
    vehicle_id: int
    fleet_id: Optional[int]
    category: str
    registration_no: str
    status: str
    approval_status: str
    created_on: datetime

    class Config:
        from_attributes = True


class VehicleApprovalRequest(BaseModel):
    approval_status: str  # APPROVED or REJECTED
    rejection_reason: Optional[str] = None


class VehicleRejectionRequest(BaseModel):
    rejection_reason: str  # Required for rejection
