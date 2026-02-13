from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import SessionLocal
from app.api.admin.auth import get_admin_session
from app.services.tenant_admin_service import TenantAdminService
from app.schemas.admin import (
    TenantCountryAddRequest,
    TenantCityAddRequest,
    TenantCountryResponse,
    TenantCityResponse,
    TenantCountryListResponse,
    TenantCityListResponse,
    AllCountriesResponse,
    AllCitiesResponse,
    CountryResponse,
    CityResponse
)

router = APIRouter(prefix="/operating-regions", tags=["Tenant Admin - Operating Regions"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==================== All Available Countries/Cities ====================

@router.get("/countries/all", response_model=AllCountriesResponse)
def get_all_countries(
    db: Session = Depends(get_db),
    admin_data: dict = Depends(get_admin_session)
):
    """Get all available countries."""
    countries = TenantAdminService.get_all_countries(db)
    return AllCountriesResponse(
        countries=[
            CountryResponse(
                country_code=c.country_code,
                name=c.name,
                phone_code=getattr(c, 'phone_code', None)
            )
            for c in countries
        ],
        total=len(countries)
    )


@router.get("/cities/all", response_model=AllCitiesResponse)
def get_all_cities(
    country_code: Optional[str] = None,
    db: Session = Depends(get_db),
    admin_data: dict = Depends(get_admin_session)
):
    """Get all available cities, optionally filtered by country."""
    cities = TenantAdminService.get_all_cities(db, country_code)
    return AllCitiesResponse(
        cities=[
            CityResponse(
                city_id=c.city_id,
                name=c.name,
                country_code=c.country_code,
                is_active=c.is_active
            )
            for c in cities
        ],
        total=len(cities)
    )


# ==================== Tenant Operating Countries ====================

@router.get("/countries", response_model=TenantCountryListResponse)
def get_tenant_countries(
    db: Session = Depends(get_db),
    admin_data: dict = Depends(get_admin_session)
):
    """Get countries where tenant operates."""
    current_user = admin_data["user"]
    countries = TenantAdminService.get_tenant_countries(db, current_user)
    
    return TenantCountryListResponse(
        countries=[
            TenantCountryResponse(
                tenant_id=tc.tenant_id,
                country_code=tc.country_code,
                country_name=c.name
            )
            for tc, c in countries
        ],
        total=len(countries)
    )


@router.post("/countries", response_model=TenantCountryResponse)
def add_tenant_country(
    request: TenantCountryAddRequest,
    db: Session = Depends(get_db),
    admin_data: dict = Depends(get_admin_session)
):
    """Add a country to tenant's operating regions."""
    current_user = admin_data["user"]
    tc, country = TenantAdminService.add_tenant_country(db, current_user, request.country_code)
    
    return TenantCountryResponse(
        tenant_id=tc.tenant_id,
        country_code=tc.country_code,
        country_name=country.name
    )


@router.delete("/countries/{country_code}")
def remove_tenant_country(
    country_code: str,
    db: Session = Depends(get_db),
    admin_data: dict = Depends(get_admin_session)
):
    """Remove a country from tenant's operating regions."""
    current_user = admin_data["user"]
    return TenantAdminService.remove_tenant_country(db, current_user, country_code)


# ==================== Tenant Operating Cities ====================

@router.get("/cities", response_model=TenantCityListResponse)
def get_tenant_cities(
    db: Session = Depends(get_db),
    admin_data: dict = Depends(get_admin_session)
):
    """Get cities where tenant operates."""
    current_user = admin_data["user"]
    cities = TenantAdminService.get_tenant_cities(db, current_user)
    
    return TenantCityListResponse(
        cities=[
            TenantCityResponse(
                tenant_id=tc.tenant_id,
                city_id=tc.city_id,
                city_name=c.name,
                country_code=c.country_code
            )
            for tc, c in cities
        ],
        total=len(cities)
    )


@router.post("/cities", response_model=TenantCityResponse)
def add_tenant_city(
    request: TenantCityAddRequest,
    db: Session = Depends(get_db),
    admin_data: dict = Depends(get_admin_session)
):
    """Add a city to tenant's operating regions."""
    current_user = admin_data["user"]
    tc, city = TenantAdminService.add_tenant_city(db, current_user, request.city_id)
    
    return TenantCityResponse(
        tenant_id=tc.tenant_id,
        city_id=tc.city_id,
        city_name=city.name,
        country_code=city.country_code
    )


@router.delete("/cities/{city_id}")
def remove_tenant_city(
    city_id: int,
    db: Session = Depends(get_db),
    admin_data: dict = Depends(get_admin_session)
):
    """Remove a city from tenant's operating regions."""
    current_user = admin_data["user"]
    return TenantAdminService.remove_tenant_city(db, current_user, city_id)
