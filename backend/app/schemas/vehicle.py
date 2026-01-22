from pydantic import BaseModel
from typing import Optional, List


class VehicleDocumentInput(BaseModel):
    document_type: str
    file_url: str


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
