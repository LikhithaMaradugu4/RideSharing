from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ==================== TENANT MANAGEMENT ====================

class TenantCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    tenant_code: str = Field(..., min_length=1, max_length=50, description="Unique tenant identifier")
    default_currency: str = Field(..., min_length=3, max_length=3, description="ISO 4217 currency code")
    default_timezone: str = Field(..., min_length=1, max_length=50)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Uber India",
                "tenant_code": "UBER_IND",
                "default_currency": "INR",
                "default_timezone": "Asia/Kolkata"
            }
        }


class TenantUpdateStatusRequest(BaseModel):
    status: str = Field(..., description="ACTIVE or SUSPENDED")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "ACTIVE"
            }
        }


class TenantResponse(BaseModel):
    tenant_id: int
    name: str
    tenant_code: str
    status: str
    default_currency: str
    default_timezone: str
    created_on: datetime
    
    class Config:
        from_attributes = True
        populate_by_name = True


class TenantListResponse(BaseModel):
    tenants: List[TenantResponse]
    total: int


class TenantDetailResponse(BaseModel):
    tenant_id: int
    name: str
    tenant_code: str
    status: str
    default_currency: str
    default_timezone: str
    created_on: datetime
    created_by: Optional[int]
    
    class Config:
        from_attributes = True
        populate_by_name = True


# ==================== TENANT ADMIN ASSIGNMENT ====================

class TenantAdminAssignRequest(BaseModel):
    user_id: int
    is_primary: bool = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 123,
                "is_primary": True
            }
        }

class TenantAdminResponse(BaseModel):
    tenant_admin_id: int
    tenant_id: int
    user_id: int
    is_primary: bool
    
    class Config:
        from_attributes = True
        populate_by_name = True
        from_attributes = True


# ==================== TENANT DOCUMENT MANAGEMENT ====================

class TenantDocumentUploadRequest(BaseModel):
    document_type: str = Field(..., description="Document type (e.g., GST_CERTIFICATE, CONTRACT, etc.)")
    file_name: str = Field(..., description="Original filename")
    file_url: str = Field(..., description="Private storage URL path")
    file_hash: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "document_type": "GST_CERTIFICATE",
                "file_name": "gst_cert_UBER_IND.pdf",
                "file_url": "s3://private-storage/tenants/1/gst_cert.pdf",
                "file_hash": "sha256:abcd1234..."
            }
        }

class TenantDocumentResponse(BaseModel):
    tenant_document_id: int
    tenant_id: int
    document_type: str
    file_name: str
    file_hash: Optional[str]
    signed_url: Optional[str] = None  # Dynamically generated
    created_on: datetime
    
    class Config:
        from_attributes = True
        populate_by_name = True
        from_attributes = True


class TenantDocumentListResponse(BaseModel):
    documents: List[TenantDocumentResponse]
    total: int


# ==================== ERROR RESPONSES ====================

class ErrorResponse(BaseModel):
    detail: str
    status_code: int
