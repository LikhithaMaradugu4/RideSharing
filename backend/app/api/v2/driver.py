from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
import os
import shutil
from pathlib import Path
from datetime import datetime

from app.api.deps.jwt_auth import get_current_user
from app.core.database import SessionLocal
from app.models.identity import AppUser, UserKYC
from app.models.core import Tenant
from app.schemas.driver import DriverApplyWithDocumentsRequest
from app.schemas.platform_admin import TenantResponse
from app.services.driver_service import DriverService

router = APIRouter(prefix="/driver", tags=["Phase-2 Driver"])

# Local storage directory for uploaded documents
UPLOAD_DIR = Path("uploads/driver_documents")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/tenants")
def get_available_tenants(
    db: Session = Depends(get_db)
):
    """
    Get all available (ACTIVE) tenants for driver/fleet owner application.
    No authentication required - used during pre-login tenant selection.
    """
    tenants = db.query(Tenant).filter(Tenant.status == "ACTIVE").all()
    return {
        "tenants": [
            TenantResponse.model_validate(t) for t in tenants
        ]
    }


@router.post("/apply-with-documents")
async def apply_driver_with_documents(
    tenant_id: int = Form(...),
    driving_license: UploadFile = File(...),
    driver_photo: UploadFile = File(...),
    aadhaar: UploadFile = File(None),
    pan: UploadFile = File(None),
    notes: str = Form(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Apply for driver with document uploads.
    Files are stored locally in uploads/driver_documents/{user_id}/
    
    Required:
    - driving_license (file)
    - driver_photo (file)
    
    At least one of:
    - aadhaar (file)
    - pan (file)
    
    Optional:
    - notes (text)
    """
    user_id = current_user.get("user_id")
    user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Validate at least one of aadhaar or pan is provided
    if not aadhaar and not pan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one of Aadhaar or PAN must be provided"
        )

    # Create user-specific directory
    user_dir = UPLOAD_DIR / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)

    # Helper function to save file locally
    async def save_file(upload_file: UploadFile, doc_type: str) -> str:
        """Save uploaded file and return relative path"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_ext = os.path.splitext(upload_file.filename)[1]
        filename = f"{doc_type}_{timestamp}{file_ext}"
        file_path = user_dir / filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        
        # Return relative path for database storage
        return f"uploads/driver_documents/{user_id}/{filename}"

    # Save all uploaded files
    driving_license_path = await save_file(driving_license, "driving_license")
    driver_photo_path = await save_file(driver_photo, "driver_photo")
    aadhaar_path = await save_file(aadhaar, "aadhaar") if aadhaar else None
    pan_path = await save_file(pan, "pan") if pan else None

    # Create application data with file paths
    data = DriverApplyWithDocumentsRequest(
        tenant_id=tenant_id,
        driver_type="INDEPENDENT",
        driving_license_number="PENDING_VERIFICATION",
        driving_license_url=driving_license_path,
        aadhaar_number="PENDING_VERIFICATION" if aadhaar else None,
        aadhaar_url=aadhaar_path,
        pan_number="PENDING_VERIFICATION" if pan else None,
        pan_url=pan_path,
        passport_photo_url=driver_photo_path,
    )

    profile = DriverService.apply_with_documents(db=db, user=user, data=data)

    # Create UserKYC records for each uploaded document
    # First, delete any existing KYC records for this user to avoid duplicates
    db.query(UserKYC).filter(UserKYC.user_id == user_id).delete()
    
    documents_created = 0
    
    # Driving License KYC
    kyc_license = UserKYC(
        user_id=user_id,
        document_type="DRIVING_LICENSE",
        document_number="PENDING_VERIFICATION",
        file_url=driving_license_path,
        verification_status="PENDING"
    )
    db.add(kyc_license)
    documents_created += 1
    
    # Driver Photo KYC
    kyc_photo = UserKYC(
        user_id=user_id,
        document_type="PROFILE_PHOTO",
        document_number="PENDING_VERIFICATION",
        file_url=driver_photo_path,
        verification_status="PENDING"
    )
    db.add(kyc_photo)
    documents_created += 1
    
    # Aadhaar KYC (if provided)
    if aadhaar_path:
        kyc_aadhaar = UserKYC(
            user_id=user_id,
            document_type="AADHAAR",
            document_number="PENDING_VERIFICATION",
            file_url=aadhaar_path,
            verification_status="PENDING"
        )
        db.add(kyc_aadhaar)
        documents_created += 1
    
    # PAN KYC (if provided)
    if pan_path:
        kyc_pan = UserKYC(
            user_id=user_id,
            document_type="PAN",
            document_number="PENDING_VERIFICATION",
            file_url=pan_path,
            verification_status="PENDING"
        )
        db.add(kyc_pan)
        documents_created += 1
    
    db.commit()

    return {
        "message": "Driver application submitted with documents",
        "status": profile.approval_status,
        "driver_id": profile.driver_id,
        "documents_created": documents_created
    }


@router.get("/me")
def get_my_driver_profile(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get("user_id")
    user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    profile = DriverService.get_my_profile(db=db, user=user)

    return {
        "driver_id": profile.driver_id,
        "tenant_id": profile.tenant_id,
        "driver_type": profile.driver_type,
        "approval_status": profile.approval_status,
        "rating": profile.rating
    }
