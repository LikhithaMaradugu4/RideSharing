from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime

from app.models.core import Tenant
from app.models.tenant import TenantAdmin, TenantDocument
from app.models.identity import AppUser
from app.schemas.platform_admin import (
    TenantCreateRequest,
    TenantUpdateStatusRequest,
    TenantAdminAssignRequest,
    TenantDocumentUploadRequest
)


class PlatformAdminService:
    """Service for platform admin operations (tenant management only)"""

    # ==================== TENANT MANAGEMENT ====================

    @staticmethod
    def create_tenant(
        db: Session,
        user: AppUser,
        data: TenantCreateRequest
    ) -> Tenant:
        """Create a new tenant (ENTERPRISE onboarding offline)"""
        
        # 1. Verify user is PLATFORM_ADMIN
        if user.role != "PLATFORM_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only platform admins can create tenants"
            )
        
        # 2. Check tenant_code uniqueness
        existing_code = (
            db.query(Tenant)
            .filter(Tenant.tenant_code == data.tenant_code)
            .first()
        )
        
        if existing_code:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Tenant code '{data.tenant_code}' already exists"
            )
        
        # 3. Check tenant name uniqueness
        existing_name = (
            db.query(Tenant)
            .filter(Tenant.name == data.name)
            .first()
        )
        
        if existing_name:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Tenant name '{data.name}' already exists"
            )
        
        # 4. Create tenant with ACTIVE status
        tenant = Tenant(
            name=data.name,
            tenant_code=data.tenant_code,
            default_currency=data.default_currency,
            default_timezone=data.default_timezone,
            status="ACTIVE",
            created_by=user.user_id
        )
        
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
        
        return tenant
    
    @staticmethod
    def get_tenant(db: Session, user: AppUser, tenant_id: int) -> Tenant:
        """Fetch tenant details (platform admin only)"""
        
        if user.role != "PLATFORM_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only platform admins can access tenant details"
            )
        
        tenant = (
            db.query(Tenant)
            .filter(Tenant.tenant_id == tenant_id)
            .first()
        )
        
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        return tenant
    
    @staticmethod
    def list_tenants(db: Session, user: AppUser) -> list:
        """List all tenants (platform admin only)"""
        
        if user.role != "PLATFORM_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only platform admins can list tenants"
            )
        
        tenants = (
            db.query(Tenant)
            .all()
        )
        
        return tenants
    
    @staticmethod
    def update_tenant_status(
        db: Session,
        user: AppUser,
        tenant_id: int,
        data: TenantUpdateStatusRequest
    ) -> Tenant:
        """Update tenant status (ACTIVE or SUSPENDED)"""
        
        # 1. Verify user is PLATFORM_ADMIN
        if user.role != "PLATFORM_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only platform admins can update tenant status"
            )
        
        # 2. Validate status
        if data.status not in ["ACTIVE", "SUSPENDED"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Status must be ACTIVE or SUSPENDED"
            )
        
        # 3. Fetch tenant
        tenant = (
            db.query(Tenant)
            .filter(Tenant.tenant_id == tenant_id)
            .first()
        )
        
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        # 4. Update status
        tenant.status = data.status
        tenant.updated_by = user.user_id
        tenant.updated_on = datetime.utcnow()
        
        db.commit()
        db.refresh(tenant)
        
        return tenant

    # ==================== TENANT ADMIN ASSIGNMENT ====================

    @staticmethod
    def assign_tenant_admin(
        db: Session,
        user: AppUser,
        tenant_id: int,
        data: TenantAdminAssignRequest
    ) -> TenantAdmin:
        """Assign a tenant admin to a tenant"""
        
        # 1. Verify user is PLATFORM_ADMIN
        if user.role != "PLATFORM_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only platform admins can assign tenant admins"
            )
        
        # 2. Verify tenant exists and is ACTIVE
        tenant = (
            db.query(Tenant)
            .filter(Tenant.tenant_id == tenant_id)
            .first()
        )
        
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        if tenant.status != "ACTIVE":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tenant must be ACTIVE to assign admins"
            )
        
        # 3. Verify target user exists
        target_user = (
            db.query(AppUser)
            .filter(AppUser.user_id == data.user_id)
            .first()
        )
        
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target user not found"
            )
        
        # 4. Check if user is already tenant admin for another tenant
        existing_admin = (
            db.query(TenantAdmin)
            .filter(TenantAdmin.user_id == data.user_id)
            .first()
        )
        
        if existing_admin:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User is already a tenant admin for another tenant"
            )
        
        # 5. If primary = true, check for existing primary admin
        if data.is_primary:
            existing_primary = (
                db.query(TenantAdmin)
                .filter(
                    TenantAdmin.tenant_id == tenant_id,
                    TenantAdmin.is_primary == True
                )
                .first()
            )
            
            if existing_primary:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Tenant already has a primary admin"
                )
        
        # 6. Create tenant admin (TRANSACTION START)
        try:
            tenant_admin = TenantAdmin(
                tenant_id=tenant_id,
                user_id=data.user_id,
                is_primary=data.is_primary,
                created_by=user.user_id
            )
            
            db.add(tenant_admin)
            db.flush()
            
            # 7. Update app_user role and tenant_id
            target_user.role = "TENANT_ADMIN"
            target_user.tenant_id = tenant_id
            
            db.commit()
            db.refresh(tenant_admin)
            
            return tenant_admin
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to assign tenant admin: {str(e)}"
            )

    # ==================== TENANT DOCUMENT MANAGEMENT ====================

    @staticmethod
    def upload_tenant_document(
        db: Session,
        user: AppUser,
        tenant_id: int,
        data: TenantDocumentUploadRequest
    ) -> TenantDocument:
        """Upload a tenant document (offline onboarding docs)"""
        
        # 1. Verify user is PLATFORM_ADMIN
        if user.role != "PLATFORM_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only platform admins can upload tenant documents"
            )
        
        # 2. Verify tenant exists
        tenant = (
            db.query(Tenant)
            .filter(Tenant.tenant_id == tenant_id)
            .first()
        )
        
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        # 3. Store document metadata (file already in private storage)
        doc = TenantDocument(
            tenant_id=tenant_id,
            document_type=data.document_type,
            file_name=data.file_name,
            file_url=data.file_url,
            file_hash=data.file_hash,
            is_active=True,
            created_by=user.user_id
        )
        
        db.add(doc)
        db.commit()
        db.refresh(doc)
        
        return doc
    
    @staticmethod
    def list_tenant_documents(
        db: Session,
        user: AppUser,
        tenant_id: int
    ) -> list:
        """List active documents for a tenant (platform admin only)"""
        
        # 1. Verify user is PLATFORM_ADMIN
        if user.role != "PLATFORM_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only platform admins can view tenant documents"
            )
        
        # 2. Verify tenant exists
        tenant = (
            db.query(Tenant)
            .filter(Tenant.tenant_id == tenant_id)
            .first()
        )
        
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        # 3. Fetch active documents only
        documents = (
            db.query(TenantDocument)
            .filter(
                TenantDocument.tenant_id == tenant_id,
                TenantDocument.is_active == True
            )
            .all()
        )
        
        return documents
    
    @staticmethod
    def get_tenant_document(
        db: Session,
        user: AppUser,
        tenant_id: int,
        document_id: int
    ) -> TenantDocument:
        """Get a specific tenant document (platform admin only)"""
        
        # 1. Verify user is PLATFORM_ADMIN
        if user.role != "PLATFORM_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only platform admins can access tenant documents"
            )
        
        # 2. Fetch document
        document = (
            db.query(TenantDocument)
            .filter(
                TenantDocument.document_id == document_id,
                TenantDocument.tenant_id == tenant_id
            )
            .first()
        )
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        return document
