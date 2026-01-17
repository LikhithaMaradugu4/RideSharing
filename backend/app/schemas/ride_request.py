from pydantic import BaseModel, field_validator


class RideRequestCreate(BaseModel):
    pickup_lat: float
    pickup_lng: float
    drop_lat: float
    drop_lng: float
    city_id: int

    @field_validator("pickup_lat", "drop_lat")
    def validate_lat(cls, v):
        if not -90 <= v <= 90:
            raise ValueError("Invalid latitude")
        return v

    @field_validator("pickup_lng", "drop_lng")
    def validate_lng(cls, v):
        if not -180 <= v <= 180:
            raise ValueError("Invalid longitude")
        return v


class RideRequestResponse(BaseModel):
    request_id: int
    status: str

    class Config:
        from_attributes = True

from pydantic import BaseModel


class RideRequestConfirm(BaseModel):
    tenant_id: int
    vehicle_category: str
