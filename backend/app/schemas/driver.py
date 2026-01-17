from pydantic import BaseModel
from typing import Optional


class DriverApplyRequest(BaseModel):
    tenant_id: int
    driver_type: str  # INDEPENDENT or FLEET


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