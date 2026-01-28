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



class TripStatusResponse(BaseModel):
    trip_id: int
    status: str
    driver_id: Optional[int]
    fare_amount: float

class CancelTripResponse(BaseModel):
    trip_id: int
    status: str
