from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class VehicleDocumentInput(BaseModel):
    document_type: str
    file_url: str

    
class Vehicle(BaseModel):
    vehicle_id: int
    tenant_id: int
    fleet_id: Optional[int]
    category: str
    registration_no: str
    status: str
    approval_status: str
    created_on: datetime  # ISO format date string

    model_config = {
        "from_attributes": True
    }

class VehicleCreateRequest(BaseModel):
    category: str
    registration_no: str
    documents: List['VehicleDocumentInput']
    
    class Config:
        json_schema_extra = {
            "example": {
                "category": "SEDAN",
                "registration_no": "KA01AB1234",
                "documents": [
                    {
                        "document_type": "RC",
                        "file_url": "https://storage.example.com/vehicle/rc_ka01ab1234.pdf"
                    },
                    {
                        "document_type": "INSURANCE",
                        "file_url": "https://storage.example.com/vehicle/insurance_valid.pdf"
                    },
                    {
                        "document_type": "VEHICLE_PHOTO",
                        "file_url": "https://storage.example.com/vehicle/photo_front.jpg"
                    },
                    {
                        "document_type": "PERMIT",
                        "file_url": "https://storage.example.com/vehicle/permit.pdf"
                    }
                ]
            }
        }


class VehicleResponse(BaseModel):
    vehicle_id: int
    tenant_id: int
    fleet_id: Optional[int]
    category: str
    registration_no: str
    status: str
    approval_status: str

    class Config:
        from_attributes = True


class VehicleSpecCreateRequest(BaseModel):
    manufacturer: str
    model_name: str
    manufacture_year: int
    fuel_type: str
    seating_capacity: int


class VehicleSpecResponse(BaseModel):
    vehicle_id: int
    manufacturer: str
    model_name: str
    manufacture_year: int
    fuel_type: str
    seating_capacity: int

    class Config:
        from_attributes = True


class VehicleDocumentCreateRequest(BaseModel):
    document_type: str
    file_url: str


class VehicleDocumentResponse(BaseModel):
    document_id: int
    vehicle_id: int
    document_type: str
    file_url: str
    verification_status: str

    class Config:
        from_attributes = True


class VehiclePhotoUploadRequest(BaseModel):
    photo_urls: List[str]


class DriverVehicleResponse(BaseModel):
    """Response for driver's approved vehicles with assignment status."""
    vehicle_id: int
    registration_no: str
    category: str
    approval_status: str
    is_currently_assigned: bool  # True if this vehicle has active assignment to this driver
    documents_complete: bool = False  # True if all required documents are approved
    missing_documents: List[str] = []  # List of document types that are not approved
    is_approved: bool = False  # True if vehicle approval_status is APPROVED

    class Config:
        from_attributes = True


class SelectVehicleRequest(BaseModel):
    """Request to select a vehicle for shift."""
    vehicle_id: int
    end_shift_if_active: bool = False  # If True, auto-end any active shift before switching
