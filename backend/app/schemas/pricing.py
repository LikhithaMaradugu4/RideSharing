from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PricingEstimateRequest(BaseModel):
    ride_request_id: int


class PricingEstimateResponse(BaseModel):
    tenant_id: int
    tenant_name: str
    vehicle_category: str
    estimated_fare: float


# ============================================
# CITY SCHEMAS
# ============================================

class CityCreateRequest(BaseModel):
    country_code: str
    name: str
    timezone: str
    currency: str
    boundary_geojson: str
    is_active: bool = True


class CityUpdateRequest(BaseModel):
    name: Optional[str] = None
    timezone: Optional[str] = None
    currency: Optional[str] = None
    boundary_geojson: Optional[str] = None
    is_active: Optional[bool] = None


class CityResponse(BaseModel):
    city_id: int
    country_code: str
    name: str
    timezone: str
    currency: str
    boundary_geojson: str
    is_active: bool
    created_on: Optional[datetime] = None
    updated_on: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================
# FARE CONFIG SCHEMAS
# ============================================

class FareConfigCreateRequest(BaseModel):
    city_id: int
    vehicle_category: str  # BIKE / AUTO / CAB / XL
    currency: str  # 3-char currency code
    base_fare: float
    per_km_rate: float
    per_min_rate: float
    minimum_fare: Optional[float] = None
    booking_fee: Optional[float] = None
    surge_allowed: bool = True
    night_charge_pct: Optional[float] = None
    effective_from: datetime
    effective_to: Optional[datetime] = None


class FareConfigUpdateRequest(BaseModel):
    base_fare: Optional[float] = None
    per_km_rate: Optional[float] = None
    per_min_rate: Optional[float] = None
    minimum_fare: Optional[float] = None
    booking_fee: Optional[float] = None
    surge_allowed: Optional[bool] = None
    night_charge_pct: Optional[float] = None
    effective_to: Optional[datetime] = None


class FareConfigResponse(BaseModel):
    fare_config_id: int
    city_id: int
    vehicle_category: str
    currency: str
    base_fare: float
    per_km_rate: float
    per_min_rate: float
    minimum_fare: Optional[float] = None
    booking_fee: Optional[float] = None
    surge_allowed: bool
    night_charge_pct: Optional[float] = None
    effective_from: datetime
    effective_to: Optional[datetime] = None
    created_by: Optional[int] = None
    created_on: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================
# SURGE ZONE SCHEMAS
# ============================================

class SurgeZoneCreateRequest(BaseModel):
    city_id: int
    name: Optional[str] = None
    boundary_geojson: str
    multiplier: float
    starts_at: datetime
    ends_at: datetime
    is_active: bool = True


class SurgeZoneUpdateRequest(BaseModel):
    name: Optional[str] = None
    boundary_geojson: Optional[str] = None
    multiplier: Optional[float] = None
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None
    is_active: Optional[bool] = None


class SurgeZoneResponse(BaseModel):
    surge_zone_id: int
    city_id: int
    name: Optional[str] = None
    boundary_geojson: str
    multiplier: float
    starts_at: datetime
    ends_at: datetime
    is_active: bool
    created_on: Optional[datetime] = None
    updated_on: Optional[datetime] = None

    class Config:
        from_attributes = True
