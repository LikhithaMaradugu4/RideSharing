from pydantic import BaseModel


class DriverLocationUpdateRequest(BaseModel):
    latitude: float
    longitude: float
