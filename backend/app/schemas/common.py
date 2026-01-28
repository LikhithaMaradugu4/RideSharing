from pydantic import BaseModel

class LatLng(BaseModel):
    latitude: float
    longitude: float
