from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date


class FleetDocumentInput(BaseModel):
    document_type: str
    file_url: str


class FleetApplyRequest(BaseModel):
    tenant_id: int
    fleet_name: str
    fleet_type: str = "BUSINESS"  # BUSINESS or INDIVIDUAL
    documents: List[FleetDocumentInput]
    
    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": 1,
                "fleet_name": "ABC Transport Services",
                "fleet_type": "BUSINESS",
                "documents": [
                    {
                        "document_type": "AADHAAR",
                        "file_url": "https://storage.example.com/fleet/aadhaar_123456.pdf"
                    },
                    {
                        "document_type": "PAN",
                        "file_url": "https://storage.example.com/fleet/pan_ABCDE1234F.pdf"
                    },
                    {
                        "document_type": "GST_CERTIFICATE",
                        "file_url": "https://storage.example.com/fleet/gst_certificate.pdf"
                    }
                ]
            }
        }


class FleetResponse(BaseModel):
    fleet_id: int
    fleet_name: str
    tenant_id: int
    approval_status: str
    status: str

    class Config:
        from_attributes = True


class FleetApplyResponse(BaseModel):
    fleet_id: int
    approval_status: str


# ==================== Fleet Owner Driver Management ====================

class FleetDriverInviteRequest(BaseModel):
    driver_id: int


class FleetDriverResponse(BaseModel):
    driver_id: int
    full_name: str
    phone: str
    start_date: datetime
    end_date: Optional[datetime]

    class Config:
        from_attributes = True


class FleetDriverListResponse(BaseModel):
    drivers: List[FleetDriverResponse]
    total: int


# ==================== Fleet Owner Assignment Management ====================

class FleetAssignmentCreateRequest(BaseModel):
    driver_id: int
    vehicle_id: int


class FleetAssignmentResponse(BaseModel):
    assignment_id: int
    driver_id: int
    vehicle_id: int
    start_time: datetime
    end_time: Optional[datetime]

    class Config:
        from_attributes = True


class FleetAssignmentListResponse(BaseModel):
    assignments: List[FleetAssignmentResponse]
    total: int


# ==================== Fleet Discovery (Driver side) ====================

class FleetDiscoveryItemResponse(BaseModel):
    fleet_id: int
    fleet_name: str
    city_id: int
    city_name: str
    address: str | None = None
    contact_phone: str | None = None


class FleetDiscoveryListResponse(BaseModel):
    fleets: List[FleetDiscoveryItemResponse]
    total: int


# ==================== Driver Invite Visibility ====================

class DriverFleetInviteResponse(BaseModel):
    fleet_id: int
    fleet_name: str
    city_id: int
    city_name: str
    invited_at: datetime
    contact_phone: str | None = None
    address: str | None = None


class DriverFleetInviteListResponse(BaseModel):
    invites: List[DriverFleetInviteResponse]
    total: int


# ==================== Fleet Cities (Fleet Owner) ====================

class FleetCityAddRequest(BaseModel):
    city_id: int


class FleetCityResponse(BaseModel):
    city_id: int
    city_name: str

    class Config:
        from_attributes = True


class FleetCityListResponse(BaseModel):
    cities: List[FleetCityResponse]
    total: int


# ==================== Driver Work Availability ====================

class DriverWorkAvailabilityRequest(BaseModel):
    date: date
    is_available: bool = True
    note: Optional[str] = None


class DriverWorkAvailabilityResponse(BaseModel):
    availability_id: int
    driver_id: int
    fleet_id: int
    date: date
    is_available: bool
    note: Optional[str]

    class Config:
        from_attributes = True


class DriverAvailabilityListResponse(BaseModel):
    availability_records: List[DriverWorkAvailabilityResponse]
    total: int


# ==================== Fleet Driver Availability View ====================

class FleetDriverAvailabilityItem(BaseModel):
    driver_id: int
    full_name: str
    phone: str
    date: date
    is_available: bool
    note: Optional[str]


class FleetDriverAvailabilityListResponse(BaseModel):
    records: List[FleetDriverAvailabilityItem]
    total: int
