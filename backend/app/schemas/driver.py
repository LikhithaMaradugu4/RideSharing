from pydantic import BaseModel
from typing import Optional
from app.schemas.common import LatLng


class UpdateDriverLocationRequest(LatLng):
    pass

class DriverAcceptResponse(BaseModel):
    trip_id: int
    status: str
    message: str


class DriverApplyRequest(BaseModel):
    tenant_id: int
    driver_type: str  # INDEPENDENT or FLEET


class DriverApplyWithDocumentsRequest(BaseModel):
    tenant_id: int
    driver_type: str
    driving_license_number: str
    driving_license_url: str
    aadhaar_number: Optional[str] = None
    aadhaar_url: Optional[str] = None
    pan_number: Optional[str] = None
    pan_url: Optional[str] = None
    passport_photo_url: Optional[str] = None
    alternate_phone_number: Optional[str] = None    
    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": 1,
                "driver_type": "FULL_TIME",
                "driving_license_number": "DL-1420110012345",
                "driving_license_url": "https://storage.example.com/driver/dl_12345.pdf",
                "aadhaar_number": "1234-5678-9012",
                "aadhaar_url": "https://storage.example.com/driver/aadhaar_masked.pdf",
                "pan_number": "ABCDE1234F",
                "pan_url": "https://storage.example.com/driver/pan_card.pdf",
                "passport_photo_url": "https://storage.example.com/driver/photo_selfie.jpg",
                "alternate_phone_number": "+919876543210"
            }
        }


class DriverProfileResponse(BaseModel):
    driver_id: int
    tenant_id: int
    driver_type: str
    approval_status: str
    rating: Optional[float]

    class Config:
        from_attributes = True

class DriverMeResponse(BaseModel):
    driver_id: int
    tenant_id: int
    driver_type: str
    approval_status: str
    rating: Optional[float]

    class Config:
        from_attributes = True


class TenantResponse(BaseModel):
    tenant_id: int
    name: str
    status: str

    class Config:
        from_attributes = True