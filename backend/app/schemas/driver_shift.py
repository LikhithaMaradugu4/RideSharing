from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List


class DriverShiftRequest(BaseModel):
    """Request to start shift (minimal data needed)."""
    pass  # No required parameters for start shift


class DriverShiftResponse(BaseModel):
    """Response for shift operations."""
    shift_id: Optional[int] = None
    driver_id: int
    tenant_id: Optional[int] = None
    vehicle_id: Optional[int] = None
    status: str  # ONLINE | BUSY | OFFLINE
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    created_by: Optional[int] = None
    created_on: Optional[datetime] = None
    updated_by: Optional[int] = None
    updated_on: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ShiftStatusResponse(BaseModel):
    """Current shift and assignment status."""
    is_online: bool
    shift_id: Optional[int]
    shift_status: Optional[str]  # ONLINE | BUSY | OFFLINE
    vehicle_id: Optional[int]
    vehicle_registration: Optional[str]
    fleet_name: Optional[str]
    assignment_start: Optional[datetime]
    started_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class EndShiftRequest(BaseModel):
    """Request to end shift."""
    pass  # No additional parameters needed


class EndAssignmentRequest(BaseModel):
    """Request to end vehicle assignment."""
    pass  # No additional parameters needed


class EndAssignmentResponse(BaseModel):
    """Response after ending assignment."""
    assignment_id: int
    driver_id: int
    vehicle_id: int
    start_time: datetime
    end_time: datetime
    message: str = "Assignment ended successfully"

    model_config = ConfigDict(from_attributes=True)
