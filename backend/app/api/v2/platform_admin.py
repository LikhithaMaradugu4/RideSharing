from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

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
    TenantDocumentListResponse
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
