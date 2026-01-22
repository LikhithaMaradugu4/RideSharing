from pydantic import BaseModel
from typing import Optional, List


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
