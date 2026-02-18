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


@router.get("/application")
def get_my_application(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get driver's application status with all documents.
    
    Returns:
    - Application status
    - All uploaded documents with their status
    - For each document: status, rejection_reason, can_reupload
    - can_resubmit: true if app is PARTIALLY_REJECTED and no docs are REJECTED
    """
    from app.models.fleet import DriverProfile
    
    user_id = current_user.get("user_id")
    user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Get driver profile
    profile = db.query(DriverProfile).filter(DriverProfile.driver_id == user_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No driver application found"
        )

    # Get all KYC documents for this user
    all_documents = db.query(UserKYC).filter(UserKYC.user_id == user_id).all()
    
    # Only use the latest document per type (re-uploads create new records)
    doc_by_type = {}
    for doc in all_documents:
        if doc.document_type not in doc_by_type or doc.kyc_id > doc_by_type[doc.document_type].kyc_id:
            doc_by_type[doc.document_type] = doc
    
    # Build document list with can_reupload flag
    doc_list = []
    has_rejected_docs = False
    
    for doc in doc_by_type.values():
        can_reupload = (
            doc.verification_status == "REJECTED" and 
            profile.approval_status in ["PARTIALLY_REJECTED", "REJECTED"]
        )
        if doc.verification_status == "REJECTED":
            has_rejected_docs = True
            
        doc_list.append({
            "document_id": doc.kyc_id,
            "document_type": doc.document_type,
            "document_number": doc.document_number,
            "file_url": doc.file_url,
            "verification_status": doc.verification_status,
            "rejection_reason": doc.rejection_reason,
            "can_reupload": can_reupload,
            "verified_by": doc.verified_by,
            "verified_on": doc.verified_on.isoformat() if doc.verified_on else None
        })
    
    # Can resubmit if PARTIALLY_REJECTED and no documents are currently REJECTED
    can_resubmit = (
        profile.approval_status == "PARTIALLY_REJECTED" and 
        not has_rejected_docs and
        len(doc_list) > 0
    )
    
    return {
        "driver_id": profile.driver_id,
        "tenant_id": profile.tenant_id,
        "driver_type": profile.driver_type,
        "approval_status": profile.approval_status,
        "documents": doc_list,
        "can_resubmit": can_resubmit
    }


@router.post("/documents/{document_type}/reupload")
async def reupload_document(
    document_type: str,
    document_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Re-upload a rejected document.
    
    Validation:
    - Application must be PARTIALLY_REJECTED or REJECTED
    - The document must have been REJECTED
    - Cannot reupload if application is APPROVED
    
    Behavior:
    - Creates new document entry (preserves history)
    - New document status = PENDING
    - Clears rejection_reason
    """
    from app.models.fleet import DriverProfile
    
    user_id = current_user.get("user_id")
    
    # Get driver profile
    profile = db.query(DriverProfile).filter(DriverProfile.driver_id == user_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No driver application found"
        )
    
    # Check application status
    if profile.approval_status == "APPROVED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot reupload documents for approved application"
        )
    
    if profile.approval_status not in ["PARTIALLY_REJECTED", "REJECTED"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only reupload documents when application is rejected"
        )
    
    # Find the latest document of this type
    existing_doc = (
        db.query(UserKYC)
        .filter(
            UserKYC.user_id == user_id,
            UserKYC.document_type == document_type.upper()
        )
        .order_by(UserKYC.kyc_id.desc())
        .first()
    )
    
    if not existing_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existing {document_type} document found"
        )
    
    if existing_doc.verification_status != "REJECTED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Document {document_type} is not rejected. Current status: {existing_doc.verification_status}"
        )
    
    # Save the new file
    user_dir = UPLOAD_DIR / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_ext = os.path.splitext(document_file.filename)[1]
    filename = f"{document_type.lower()}_{timestamp}{file_ext}"
    file_path = user_dir / filename
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(document_file.file, buffer)
    
    relative_path = f"uploads/driver_documents/{user_id}/{filename}"
    
    # Create new KYC record (keep old one for history)
    new_doc = UserKYC(
        user_id=user_id,
        document_type=document_type.upper(),
        document_number="PENDING_VERIFICATION",
        file_url=relative_path,
        verification_status="PENDING",
        rejection_reason=None
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    
    return {
        "message": f"Document {document_type} re-uploaded successfully",
        "document_id": new_doc.kyc_id,
        "verification_status": new_doc.verification_status
    }


@router.post("/resubmit")
def resubmit_application(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Manually resubmit application after fixing all rejected documents.
    
    Validation:
    - Application must be PARTIALLY_REJECTED
    - No document should currently have REJECTED status
    
    Behavior:
    - Updates application.status → PENDING
    - Updates updated_at timestamp
    """
    from app.models.fleet import DriverProfile
    
    user_id = current_user.get("user_id")
    
    # Get driver profile
    profile = db.query(DriverProfile).filter(DriverProfile.driver_id == user_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No driver application found"
        )
    
    # Check application status
    if profile.approval_status != "PARTIALLY_REJECTED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Application status must be PARTIALLY_REJECTED to resubmit. Current: {profile.approval_status}"
        )
    
    # Check if latest documents per type still have REJECTED status
    all_docs = db.query(UserKYC).filter(UserKYC.user_id == user_id).all()
    if not all_docs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No documents found for application"
        )
    
    # Get latest document per type
    doc_by_type = {}
    for doc in all_docs:
        if doc.document_type not in doc_by_type or doc.kyc_id > doc_by_type[doc.document_type].kyc_id:
            doc_by_type[doc.document_type] = doc
    
    rejected_latest = [d for d in doc_by_type.values() if d.verification_status == "REJECTED"]
    if rejected_latest:
        rejected_types = [doc.document_type for doc in rejected_latest]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot resubmit. These documents are still rejected: {', '.join(rejected_types)}"
        )
    
    # Update application status to PENDING for review
    profile.approval_status = "PENDING"
    db.commit()
    
    return {
        "message": "Application resubmitted successfully",
        "driver_id": profile.driver_id,
        "approval_status": profile.approval_status
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
