from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List
from decimal import Decimal


class DispatchAttemptResponse(BaseModel):
    """Response for dispatch attempt."""
    attempt_id: int
    trip_id: int
    driver_id: int
    sent_at: datetime
    responded_at: Optional[datetime]
    response: str  # PENDING_WAVE_1 | ACCEPTED | REJECTED | CANCELLED | TIMEOUT
    wave_number: Optional[int] = None  # Dispatch wave (1, 2, 3, ...)

    model_config = ConfigDict(from_attributes=True)


class DriverDispatchNotification(BaseModel):
    """Notification sent to driver for incoming trip request."""
    attempt_id: int
    trip_id: int
    pickup_lat: Decimal
    pickup_lng: Decimal
    drop_lat: Optional[Decimal]
    drop_lng: Optional[Decimal]
    rider_name: Optional[str]
    estimated_distance_km: Optional[float]
    sent_at: datetime
    expires_in_seconds: int = 30

    model_config = ConfigDict(from_attributes=True)


class AcceptDispatchRequest(BaseModel):
    """Driver accepts trip request."""
    attempt_id: int


class RejectDispatchRequest(BaseModel):
    """Driver rejects trip request."""
    attempt_id: int
    reason: Optional[str] = None  # Optional rejection reason


class DispatchStatusResponse(BaseModel):
    """Current dispatch status for a trip."""
    trip_id: int
    status: str  # DISPATCHING | ASSIGNED | NO_DRIVER_AVAILABLE
    attempts_count: int
    latest_wave: Optional[int]
    assigned_driver_id: Optional[int]
    assigned_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class EligibleDriversResponse(BaseModel):
    """List of eligible drivers for debugging/admin."""
    total_count: int
    drivers: List[dict]  # List of {driver_id, distance_km, shift_status}

    model_config = ConfigDict(from_attributes=True)
