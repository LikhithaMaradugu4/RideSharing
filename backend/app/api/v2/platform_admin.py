from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.api.deps.auth import get_current_user
from app.core.database import SessionLocal
from app.models.identity import AppUser
from app.schemas.platform_admin import (
    TenantCreateRequest,
    TenantUpdateStatusRequest,
    TenantResponse,
    TenantListResponse,
    TenantDetailResponse,
    TenantAdminAssignRequest,
    TenantAdminResponse,
    TenantDocumentUploadRequest,
    TenantDocumentResponse,
    TenantDocumentListResponse,
    CountryCreateRequest,
    CountryUpdateRequest,
    CountryResponse,
    CityCreateRequest,
    CityUpdateRequest,
    CityResponse,
    FareConfigCreateRequest,
    FareConfigUpdateRequest,
    FareConfigResponse,
    CommissionConfigCreateRequest,
    CommissionConfigUpdateRequest,
    CommissionConfigResponse,
)
from app.services.platform_admin_service import PlatformAdminService


router = APIRouter(prefix="/platform-admin", tags=["Platform Admin"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==================== TENANT MANAGEMENT ====================

@router.post("/tenants", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
def create_tenant(
    data: TenantCreateRequest,
    db: Session = Depends(get_db),
    current_user: AppUser = Depends(get_current_user)
):
    tenant = PlatformAdminService.create_tenant(db=db, user=current_user, data=data)
    
    return TenantResponse.model_validate(tenant)


@router.get("/tenants", response_model=TenantListResponse)
def list_tenants(
    db: Session = Depends(get_db),
    current_user: AppUser = Depends(get_current_user)
):
    tenants = PlatformAdminService.list_tenants(db=db, user=current_user)
    
    return TenantListResponse(
        tenants=[TenantResponse.model_validate(t) for t in tenants],
        total=len(tenants)
    )


@router.get("/tenants/{tenant_id}", response_model=TenantDetailResponse)
def get_tenant(
    tenant_id: int,
    db: Session = Depends(get_db),
    current_user: AppUser = Depends(get_current_user)
):
   
    tenant = PlatformAdminService.get_tenant(db=db, user=current_user, tenant_id=tenant_id)
    
    return TenantDetailResponse.model_validate(tenant)


@router.patch("/tenants/{tenant_id}/status", response_model=TenantResponse)
def update_tenant_status(
    tenant_id: int,
    data: TenantUpdateStatusRequest,
    db: Session = Depends(get_db),
    current_user: AppUser = Depends(get_current_user)
):
    tenant = PlatformAdminService.update_tenant_status(
        db=db, user=current_user, tenant_id=tenant_id, data=data
    )
    
    return TenantResponse.model_validate(tenant)


# ==================== TENANT ADMIN ASSIGNMENT ====================

@router.post("/tenants/{tenant_id}/admins", response_model=TenantAdminResponse, status_code=status.HTTP_201_CREATED)
def assign_tenant_admin(
    tenant_id: int,
    data: TenantAdminAssignRequest,
    db: Session = Depends(get_db),
    current_user: AppUser = Depends(get_current_user)
):
    tenant_admin = PlatformAdminService.assign_tenant_admin(
        db=db, user=current_user, tenant_id=tenant_id, data=data
    )
    
    return TenantAdminResponse.model_validate(tenant_admin)


# ==================== TENANT DOCUMENT MANAGEMENT ====================

@router.post("/tenants/{tenant_id}/documents", response_model=TenantDocumentResponse, status_code=status.HTTP_201_CREATED)
def upload_tenant_document(
    tenant_id: int,
    data: TenantDocumentUploadRequest,
    db: Session = Depends(get_db),
    current_user: AppUser = Depends(get_current_user)
):
    document = PlatformAdminService.upload_tenant_document(
        db=db, user=current_user, tenant_id=tenant_id, data=data
    )
    
    return TenantDocumentResponse.model_validate(document)


@router.get("/tenants/{tenant_id}/documents", response_model=TenantDocumentListResponse)
def list_tenant_documents(
    tenant_id: int,
    db: Session = Depends(get_db),
    current_user: AppUser = Depends(get_current_user)
):
    documents = PlatformAdminService.list_tenant_documents(
        db=db, user=current_user, tenant_id=tenant_id
    )
    
    return TenantDocumentListResponse(
        documents=[TenantDocumentResponse.model_validate(d) for d in documents],
        total=len(documents)
    )


@router.get("/tenants/{tenant_id}/documents/{document_id}", response_model=TenantDocumentResponse)
def get_tenant_document(
    tenant_id: int,
    document_id: int,
    db: Session = Depends(get_db),
    current_user: AppUser = Depends(get_current_user)
):
    document = PlatformAdminService.get_tenant_document(
        db=db, user=current_user, tenant_id=tenant_id, document_id=document_id
    )
    
    return TenantDocumentResponse.model_validate(document)


# ==================== COUNTRY MANAGEMENT ====================

@router.post("/countries", response_model=CountryResponse, status_code=status.HTTP_201_CREATED)
def create_country(
    data: CountryCreateRequest,
    db: Session = Depends(get_db),
    current_user: AppUser = Depends(get_current_user)
):
    country = PlatformAdminService.create_country(db=db, user=current_user, data=data)
    return CountryResponse.model_validate(country)


@router.get("/countries", response_model=List[CountryResponse])
def list_countries(
    db: Session = Depends(get_db),
    current_user: AppUser = Depends(get_current_user)
):
    countries = PlatformAdminService.list_countries(db=db, user=current_user)
    return [CountryResponse.model_validate(c) for c in countries]


@router.put("/countries/{country_code}", response_model=CountryResponse)
def update_country(
    country_code: str,
    data: CountryUpdateRequest,
    db: Session = Depends(get_db),
    current_user: AppUser = Depends(get_current_user)
):
    country = PlatformAdminService.update_country(db=db, user=current_user, country_code=country_code, data=data)
    return CountryResponse.model_validate(country)


# ==================== CITY MANAGEMENT ====================

@router.post("/cities", response_model=CityResponse, status_code=status.HTTP_201_CREATED)
def create_city(
    data: CityCreateRequest,
    db: Session = Depends(get_db),
    current_user: AppUser = Depends(get_current_user)
):
    city = PlatformAdminService.create_city(db=db, user=current_user, data=data)
    return CityResponse.model_validate(city)


@router.get("/cities", response_model=List[CityResponse])
def list_cities(
    country_code: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: AppUser = Depends(get_current_user)
):
    cities = PlatformAdminService.list_cities(db=db, user=current_user, country_code=country_code)
    return [CityResponse.model_validate(c) for c in cities]


@router.put("/cities/{city_id}", response_model=CityResponse)
def update_city(
    city_id: int,
    data: CityUpdateRequest,
    db: Session = Depends(get_db),
    current_user: AppUser = Depends(get_current_user)
):
    city = PlatformAdminService.update_city(db=db, user=current_user, city_id=city_id, data=data)
    return CityResponse.model_validate(city)


# ==================== FARE CONFIG MANAGEMENT ====================

@router.post("/fare-config", response_model=FareConfigResponse, status_code=status.HTTP_201_CREATED)
def create_fare_config(
    data: FareConfigCreateRequest,
    db: Session = Depends(get_db),
    current_user: AppUser = Depends(get_current_user)
):
    fare = PlatformAdminService.create_fare_config(db=db, user=current_user, data=data)
    return FareConfigResponse.model_validate(fare)


@router.get("/fare-config", response_model=List[FareConfigResponse])
def list_fare_configs(
    city_id: Optional[int] = Query(None),
    vehicle_category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: AppUser = Depends(get_current_user)
):
    configs = PlatformAdminService.list_fare_configs(
        db=db, user=current_user, city_id=city_id, vehicle_category=vehicle_category
    )
    return [FareConfigResponse.model_validate(c) for c in configs]


@router.put("/fare-config/{fare_config_id}", response_model=FareConfigResponse)
def update_fare_config(
    fare_config_id: int,
    data: FareConfigUpdateRequest,
    db: Session = Depends(get_db),
    current_user: AppUser = Depends(get_current_user)
):
    fare = PlatformAdminService.update_fare_config(db=db, user=current_user, fare_config_id=fare_config_id, data=data)
    return FareConfigResponse.model_validate(fare)


@router.put("/fare-config/{fare_config_id}/deactivate", response_model=FareConfigResponse)
def deactivate_fare_config(
    fare_config_id: int,
    db: Session = Depends(get_db),
    current_user: AppUser = Depends(get_current_user)
):
    fare = PlatformAdminService.deactivate_fare_config(db=db, user=current_user, fare_config_id=fare_config_id)
    return FareConfigResponse.model_validate(fare)


# ==================== COMMISSION CONFIG MANAGEMENT ====================

@router.post("/commission-config", response_model=CommissionConfigResponse, status_code=status.HTTP_201_CREATED)
def create_commission_config(
    data: CommissionConfigCreateRequest,
    db: Session = Depends(get_db),
    current_user: AppUser = Depends(get_current_user)
):
    cc = PlatformAdminService.create_commission_config(db=db, user=current_user, data=data)
    return CommissionConfigResponse.model_validate(cc)


@router.get("/commission-config", response_model=List[CommissionConfigResponse])
def list_commission_configs(
    city_id: Optional[int] = Query(None),
    vehicle_category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: AppUser = Depends(get_current_user)
):
    configs = PlatformAdminService.list_commission_configs(
        db=db, user=current_user, city_id=city_id, vehicle_category=vehicle_category
    )
    return [CommissionConfigResponse.model_validate(c) for c in configs]


@router.put("/commission-config/{config_id}", response_model=CommissionConfigResponse)
def update_commission_config(
    config_id: int,
    data: CommissionConfigUpdateRequest,
    db: Session = Depends(get_db),
    current_user: AppUser = Depends(get_current_user)
):
    cc = PlatformAdminService.update_commission_config(db=db, user=current_user, config_id=config_id, data=data)
    return CommissionConfigResponse.model_validate(cc)


@router.put("/commission-config/{config_id}/deactivate", response_model=CommissionConfigResponse)
def deactivate_commission_config(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: AppUser = Depends(get_current_user)
):
    cc = PlatformAdminService.deactivate_commission_config(db=db, user=current_user, config_id=config_id)
    return CommissionConfigResponse.model_validate(cc)
