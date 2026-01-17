from pydantic import BaseModel


class PricingEstimateRequest(BaseModel):
    ride_request_id: int


class PricingEstimateResponse(BaseModel):
    tenant_id: int
    tenant_name: str
    vehicle_category: str
    estimated_fare: float
