from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class PendingDriverResponse(BaseModel):
    driver_id: int
    full_name: Optional[str] = None
    phone: Optional[str] = None
    application_date: datetime
    driver_type: str


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
