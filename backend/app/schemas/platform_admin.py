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


# ==================== COUNTRY MANAGEMENT ====================

class CountryCreateRequest(BaseModel):
    country_code: str = Field(..., min_length=2, max_length=2, description="ISO 3166-1 alpha-2")
    name: str = Field(..., min_length=1, max_length=100)
    phone_code: str = Field(..., min_length=1, max_length=5)
    default_timezone: str = Field(..., min_length=1, max_length=50)
    default_currency: str = Field(..., min_length=3, max_length=3, description="ISO 4217 currency code")


class CountryUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone_code: Optional[str] = Field(None, min_length=1, max_length=5)
    default_timezone: Optional[str] = Field(None, min_length=1, max_length=50)
    default_currency: Optional[str] = Field(None, min_length=3, max_length=3)


class CountryResponse(BaseModel):
    country_code: str
    name: str
    phone_code: str
    default_timezone: str
    default_currency: str

    class Config:
        from_attributes = True


# ==================== CITY MANAGEMENT ====================

class CityCreateRequest(BaseModel):
    country_code: str = Field(..., min_length=2, max_length=2)
    name: str = Field(..., min_length=1, max_length=120)
    timezone: str = Field(..., min_length=1, max_length=50)
    currency: str = Field(..., min_length=3, max_length=3)
    boundary_geojson: str = Field(default="{}")


class CityUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=120)
    timezone: Optional[str] = Field(None, min_length=1, max_length=50)
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    boundary_geojson: Optional[str] = None
    is_active: Optional[bool] = None


class CityResponse(BaseModel):
    city_id: int
    country_code: str
    name: str
    timezone: str
    currency: str
    boundary_geojson: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True


# ==================== FARE CONFIG MANAGEMENT ====================

class FareConfigCreateRequest(BaseModel):
    city_id: int
    vehicle_category: str = Field(..., min_length=1)
    currency: str = Field(..., min_length=3, max_length=3)
    base_fare: float
    per_km_rate: float
    per_min_rate: float
    minimum_fare: Optional[float] = None
    booking_fee: Optional[float] = None
    surge_allowed: bool = True
    night_charge_pct: Optional[float] = None
    effective_from: datetime
    effective_to: Optional[datetime] = None


class FareConfigUpdateRequest(BaseModel):
    base_fare: Optional[float] = None
    per_km_rate: Optional[float] = None
    per_min_rate: Optional[float] = None
    minimum_fare: Optional[float] = None
    booking_fee: Optional[float] = None
    surge_allowed: Optional[bool] = None
    night_charge_pct: Optional[float] = None
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None


class FareConfigResponse(BaseModel):
    fare_config_id: int
    city_id: int
    vehicle_category: str
    currency: str
    base_fare: float
    per_km_rate: float
    per_min_rate: float
    minimum_fare: Optional[float] = None
    booking_fee: Optional[float] = None
    surge_allowed: bool
    night_charge_pct: Optional[float] = None
    effective_from: datetime
    effective_to: Optional[datetime] = None
    created_by: Optional[int] = None
    created_on: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==================== COMMISSION CONFIG MANAGEMENT ====================

class CommissionConfigCreateRequest(BaseModel):
    city_id: int
    vehicle_category: str = Field(..., min_length=1)
    commission_type: str = Field(..., description="FIXED or PERCENTAGE")
    fixed_amount: Optional[float] = None
    percentage: Optional[float] = None
    currency: str = Field(..., min_length=3, max_length=3)
    effective_from: datetime
    effective_to: Optional[datetime] = None


class CommissionConfigUpdateRequest(BaseModel):
    commission_type: Optional[str] = None
    fixed_amount: Optional[float] = None
    percentage: Optional[float] = None
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None


class CommissionConfigResponse(BaseModel):
    id: int
    commission_type: str
    tenant_id: Optional[int] = None
    city_id: Optional[int] = None
    vehicle_category: Optional[str] = None
    fixed_amount: Optional[float] = None
    percentage: Optional[float] = None
    currency: str
    is_active: bool
    effective_from: datetime
    effective_to: Optional[datetime] = None
    created_by: Optional[int] = None
    created_on: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==================== ERROR RESPONSES ====================

class ErrorResponse(BaseModel):
    detail: str
    status_code: int
