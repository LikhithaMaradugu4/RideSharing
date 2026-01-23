from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List


class DriverShiftRequest(BaseModel):
    """Request to start shift (minimal data needed)."""
    pass  # No required parameters for start shift


class DriverShiftResponse(BaseModel):
    """Response for shift operations."""
    shift_id: int
    driver_id: int
    tenant_id: int
    status: str  # ONLINE | BUSY | OFFLINE
    started_at: datetime
    ended_at: Optional[datetime]
    created_by: int
    created_on: datetime
    updated_by: Optional[int]
    updated_on: Optional[datetime]

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
