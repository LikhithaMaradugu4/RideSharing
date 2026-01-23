from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, timezone

from app.core.database import SessionLocal
from app.models.core import Tenant
from app.models.identity import AppUser, UserAuth
from app.models.tenant import TenantAdmin, TenantDocument
from app.schemas.admin import (
    TenantCreateRequest,
    TenantResponse,
    TenantListResponse,
    TenantDetailResponse,
    TenantAdminCreateRequest,
    TenantAdminResponse,
    TenantDocumentResponse
)
from app.utils.security import hash_password
from app.api.admin.auth import get_admin_session

router = APIRouter(prefix="/tenants", tags=["Platform Admin - Tenants"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def require_platform_admin(admin_data: dict = Depends(get_admin_session)):
    """Ensure user is a platform admin"""
    user = admin_data["user"]
    if user.role != "PLATFORM_ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Only platform admins can perform this action"
        )
    return admin_data


@router.get("", response_model=List[TenantListResponse])
def list_tenants(
    db: Session = Depends(get_db),
    admin_data: dict = Depends(require_platform_admin)
):
    """Get list of all tenants - Platform Admin only"""
    
    tenants = db.query(Tenant).order_by(Tenant.created_on.desc()).all()
    
    return [
        TenantListResponse(
            tenant_id=t.tenant_id,
            name=t.name,
            tenant_code=t.tenant_code,
            status=t.status,
            default_currency=t.default_currency,
            default_timezone=t.default_timezone,
            created_on=t.created_on
        )
        for t in tenants
    ]


@router.post("", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
def create_tenant(
    data: TenantCreateRequest,
    db: Session = Depends(get_db),
    admin_data: dict = Depends(require_platform_admin)
):
    """Create a new tenant - Platform Admin only"""
    
    # Check if tenant name already exists
    existing = db.query(Tenant).filter(Tenant.name == data.tenant_name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tenant name already exists")
    
    # Generate tenant code from name
    tenant_code = data.tenant_name.upper().replace(" ", "_")[:50]
    
    # Ensure tenant code is unique
    base_code = tenant_code
    counter = 1
    while db.query(Tenant).filter(Tenant.tenant_code == tenant_code).first():
        tenant_code = f"{base_code}_{counter}"
        counter += 1
    
    # Create tenant
    tenant = Tenant(
        tenant_code=tenant_code,
        name=data.tenant_name,
        default_currency=data.default_currency,
        default_timezone=data.default_timezone,
        status="ACTIVE",
        created_on=datetime.now(timezone.utc),
        updated_on=datetime.now(timezone.utc)
    )
    
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    
    return TenantResponse(
        tenant_id=tenant.tenant_id,
        tenant_code=tenant.tenant_code,
        name=tenant.name,
        status=tenant.status,
        default_currency=tenant.default_currency,
        default_timezone=tenant.default_timezone,
        created_on=tenant.created_on
    )


@router.get("/{tenant_id}", response_model=TenantDetailResponse)
def get_tenant_details(
    tenant_id: int,
    db: Session = Depends(get_db),
    admin_data: dict = Depends(require_platform_admin)
):
    """Get detailed tenant information - Platform Admin only"""
    
    tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    # Get primary tenant admin if exists
    tenant_admin = db.query(TenantAdmin, AppUser).join(
        AppUser, TenantAdmin.user_id == AppUser.user_id
    ).filter(
        TenantAdmin.tenant_id == tenant_id,
        TenantAdmin.is_primary == True
    ).first()
    
    primary_admin = None
    if tenant_admin:
        admin_record, admin_user = tenant_admin
        primary_admin = TenantAdminResponse(
            tenant_admin_id=admin_record.tenant_admin_id,
            user_id=admin_user.user_id,
            email=admin_user.email,
            full_name=admin_user.full_name,
            is_primary=admin_record.is_primary,
            created_on=admin_record.created_on
        )
    
    # Count documents
    document_count = db.query(func.count(TenantDocument.tenant_document_id)).filter(
        TenantDocument.tenant_id == tenant_id,
        TenantDocument.is_active == True
    ).scalar() or 0
    
    return TenantDetailResponse(
        tenant_id=tenant.tenant_id,
        tenant_code=tenant.tenant_code,
        name=tenant.name,
        status=tenant.status,
        default_currency=tenant.default_currency,
        default_timezone=tenant.default_timezone,
        created_on=tenant.created_on,
        primary_admin=primary_admin,
        document_count=document_count
    )


@router.delete("/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tenant(
    tenant_id: int,
    db: Session = Depends(get_db),
    admin_data: dict = Depends(require_platform_admin)
):
    """Delete a tenant - Platform Admin only"""
    
    tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    # TODO: Add checks for dependent data (drivers, fleets, etc.)
    # For now, simple delete
    db.delete(tenant)
    db.commit()
    
    return None


@router.post("/{tenant_id}/admins", response_model=TenantAdminResponse, status_code=status.HTTP_201_CREATED)
def create_tenant_admin(
    tenant_id: int,
    data: TenantAdminCreateRequest,
    db: Session = Depends(get_db),
    admin_data: dict = Depends(require_platform_admin)
):
    """Create primary tenant admin - Platform Admin only"""
    
    # Check tenant exists
    tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    # Check if primary admin already exists
    existing_admin = db.query(TenantAdmin).filter(
        TenantAdmin.tenant_id == tenant_id,
        TenantAdmin.is_primary == True
    ).first()
    
    if existing_admin:
        raise HTTPException(
            status_code=400,
            detail="Primary tenant admin already exists"
        )
    
    # Check if email already exists
    existing_user = db.query(AppUser).filter(AppUser.email == data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already in use")
    
    # Create AppUser
    user = AppUser(
        full_name=data.full_name or data.email,
        email=data.email,
        role="TENANT_ADMIN",
        status="ACTIVE",
        country_code=tenant.default_currency[:2] if len(tenant.default_currency) >= 2 else "US",  # Default
        created_on=datetime.now(timezone.utc),
        updated_on=datetime.now(timezone.utc)
    )
    
    db.add(user)
    db.flush()
    
    # Create default password (email without domain)
    default_password = data.email.split("@")[0] + "123"
    
    # Create UserAuth
    user_auth = UserAuth(
        user_id=user.user_id,
        password_hash=hash_password(default_password),
        is_locked=False,
        created_on=datetime.now(timezone.utc),
        updated_on=datetime.now(timezone.utc)
    )
    
    db.add(user_auth)
    
    # Create TenantAdmin
    tenant_admin = TenantAdmin(
        tenant_id=tenant_id,
        user_id=user.user_id,
        is_primary=True,
        created_on=datetime.now(timezone.utc),
        updated_on=datetime.now(timezone.utc)
    )
    
    db.add(tenant_admin)
    db.commit()
    db.refresh(tenant_admin)
    
    return TenantAdminResponse(
        tenant_admin_id=tenant_admin.tenant_admin_id,
        user_id=user.user_id,
        email=user.email,
        full_name=user.full_name,
        is_primary=tenant_admin.is_primary,
        created_on=tenant_admin.created_on
    )


@router.get("/{tenant_id}/admins", response_model=TenantAdminResponse)
def get_tenant_admin(
    tenant_id: int,
    db: Session = Depends(get_db),
    admin_data: dict = Depends(require_platform_admin)
):
    """Get primary tenant admin - Platform Admin only"""
    
    # Check tenant exists
    tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    # Get primary tenant admin
    result = db.query(TenantAdmin, AppUser).join(
        AppUser, TenantAdmin.user_id == AppUser.user_id
    ).filter(
        TenantAdmin.tenant_id == tenant_id,
        TenantAdmin.is_primary == True
    ).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Primary admin not found")
    
    admin_record, admin_user = result
    
    return TenantAdminResponse(
        tenant_admin_id=admin_record.tenant_admin_id,
        user_id=admin_user.user_id,
        email=admin_user.email,
        full_name=admin_user.full_name,
        is_primary=admin_record.is_primary,
        created_on=admin_record.created_on
    )
