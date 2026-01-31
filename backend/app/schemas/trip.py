from pydantic import BaseModel
from typing import Optional

class ValidateLocationRequest(BaseModel):
    pickup_lat: float
    pickup_lng: float
    drop_lat: float
    drop_lng: float


class ValidateLocationResponse(BaseModel):
    city_id: int
    city_name: str


from typing import Optional

class FareEstimateRequest(BaseModel):
    pickup_lat: float
    pickup_lng: float
    drop_lat: float
    drop_lng: float
    vehicle_category: str


class FareEstimateResponse(BaseModel):
    distance_km: float
    base_fare: float
    surge_multiplier: float
    final_fare: float
    surge_zone_id: Optional[int]

class CreateTripRequest(BaseModel):
    pickup_lat: float
    pickup_lng: float
    drop_lat: float
    drop_lng: float
    vehicle_category: str


class CreateTripResponse(BaseModel):
    trip_id: int
    status: str
    fare_amount: float


class LocationInfo(BaseModel):
    lat: float
    lng: float


class DriverInfo(BaseModel):
    driver_id: int
    full_name: Optional[str] = None
    phone_number: Optional[str] = None


class VehicleInfo(BaseModel):
    vehicle_id: int
    vehicle_category: Optional[str] = None
    registration_number: Optional[str] = None


class TripStatusResponse(BaseModel):
    trip_id: int
    status: str
    driver_id: Optional[int] = None
    fare_amount: float
    estimated_fare: Optional[float] = None
    distance_km: Optional[float] = None
    vehicle_category: Optional[str] = None
    pickup_location: Optional[LocationInfo] = None
    drop_location: Optional[LocationInfo] = None
    driver: Optional[DriverInfo] = None
    vehicle: Optional[VehicleInfo] = None
    pickup_otp: Optional[str] = None

class CancelTripResponse(BaseModel):
    trip_id: int
    status: str


# ----- Pickup OTP Schemas -----

class GeneratePickupOTPResponse(BaseModel):
    """Response after generating pickup OTP."""
    trip_id: int
    otp: str  # The 6-digit OTP to show to rider
    expires_at: str  # ISO timestamp when OTP expires

    model_config = {"from_attributes": True}


class VerifyPickupOTPRequest(BaseModel):
    """Request to verify pickup OTP."""
    otp: str  # The 6-digit OTP entered by driver


class VerifyPickupOTPResponse(BaseModel):
    """Response after verifying pickup OTP."""
    trip_id: int
    verified: bool
    message: str

    model_config = {"from_attributes": True}
