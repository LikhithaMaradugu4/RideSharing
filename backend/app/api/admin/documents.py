from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone
import os
import hashlib
import shutil

from app.core.database import SessionLocal
from app.models.core import Tenant
from app.models.tenant import TenantDocument
from app.schemas.admin import TenantDocumentResponse, TenantDocumentUploadResponse
from app.api.admin.auth import get_admin_session

router = APIRouter(prefix="/tenants/{tenant_id}/documents", tags=["Platform Admin - Tenant Documents"])

# Configure upload directory
UPLOAD_DIR = "/tmp/tenant_documents"  # Change this to your preferred directory
os.makedirs(UPLOAD_DIR, exist_ok=True)


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


@router.get("", response_model=List[TenantDocumentResponse])
def list_tenant_documents(
    tenant_id: int,
    db: Session = Depends(get_db),
    admin_data: dict = Depends(require_platform_admin)
):
    """Get all documents for a tenant - Platform Admin only"""
    
    # Check tenant exists
    tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    # Get documents
    documents = db.query(TenantDocument).filter(
        TenantDocument.tenant_id == tenant_id,
        TenantDocument.is_active == True
    ).order_by(TenantDocument.created_on.desc()).all()
    
    return [
        TenantDocumentResponse(
            tenant_document_id=doc.tenant_document_id,
            document_type=doc.document_type,
            file_name=doc.file_name,
            file_url=doc.file_url,
            created_on=doc.created_on
        )
        for doc in documents
    ]


@router.post("", response_model=TenantDocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_tenant_document(
    tenant_id: int,
    document_type: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin_data: dict = Depends(require_platform_admin)
):
    """Upload a document for a tenant - Platform Admin only"""
    
    # Check tenant exists
    tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Create tenant-specific directory
    tenant_dir = os.path.join(UPLOAD_DIR, str(tenant_id))
    os.makedirs(tenant_dir, exist_ok=True)
    
    # Generate unique filename
    file_ext = os.path.splitext(file.filename)[1]
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{document_type}_{timestamp}{file_ext}"
    file_path = os.path.join(tenant_dir, safe_filename)
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Calculate file hash
    file_hash = None
    try:
        with open(file_path, "rb") as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
    except Exception:
        pass
    
    # Create database record
    document = TenantDocument(
        tenant_id=tenant_id,
        document_type=document_type,
        file_name=file.filename,
        file_url=file_path,
        file_hash=file_hash,
        is_active=True,
        created_on=datetime.now(timezone.utc),
        updated_on=datetime.now(timezone.utc)
    )
    
    db.add(document)
    db.commit()
    db.refresh(document)
    
    return TenantDocumentUploadResponse(
        tenant_document_id=document.tenant_document_id,
        message="Document uploaded successfully"
    )


@router.get("/{document_id}/download")
async def download_tenant_document(
    tenant_id: int,
    document_id: int,
    db: Session = Depends(get_db),
    admin_data: dict = Depends(require_platform_admin)
):
    """Download a tenant document - Platform Admin only"""
    
    # Get document
    document = db.query(TenantDocument).filter(
        TenantDocument.tenant_document_id == document_id,
        TenantDocument.tenant_id == tenant_id,
        TenantDocument.is_active == True
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check if file exists
    if not os.path.exists(document.file_url):
        raise HTTPException(status_code=404, detail="File not found on server")
    
    return FileResponse(
        path=document.file_url,
        filename=document.file_name,
        media_type="application/octet-stream"
    )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tenant_document(
    tenant_id: int,
    document_id: int,
    db: Session = Depends(get_db),
    admin_data: dict = Depends(require_platform_admin)
):
    """Delete a tenant document (soft delete) - Platform Admin only"""
    
    # Get document
    document = db.query(TenantDocument).filter(
        TenantDocument.tenant_document_id == document_id,
        TenantDocument.tenant_id == tenant_id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Soft delete
    document.is_active = False
    document.updated_on = datetime.now(timezone.utc)
    db.commit()
    
    return None
