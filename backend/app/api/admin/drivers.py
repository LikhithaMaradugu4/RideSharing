from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone

from app.core.database import SessionLocal
from app.api.admin.auth import get_admin_session
from app.services.tenant_admin_service import TenantAdminService
from app.schemas.admin import (
    PendingDriverResponse,
    DriverApproveRequest,
    DriverRejectRequest,
    DriverDocumentResponse,
    DriverListResponse,
    ApprovalStatusUpdateRequest,
    DriverDetailResponse,
    DriverDocumentReviewRequest,
    DriverDocumentDetailResponse
)
from app.models.identity import UserKYC
from app.models.fleet import DriverProfile


router = APIRouter(prefix="/drivers", tags=[" Tenant Admin - Drivers"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/pending", response_model=List[PendingDriverResponse])
def get_pending_drivers(
    db: Session = Depends(get_db),
    admin_data: dict = Depends(get_admin_session)
):
    current_user = admin_data["user"]
    drivers = TenantAdminService.get_pending_drivers(db, current_user)

    return [
        PendingDriverResponse(
            driver_id=driver_profile.driver_id,
            full_name=user.full_name,
            phone=user.phone,
            application_date=driver_profile.created_on,
            driver_type=driver_profile.driver_type
        )
        for driver_profile, user in drivers
    ]


@router.post("/{driver_id}/approve")
def approve_driver(
    driver_id: int,
    data: DriverApproveRequest,
    db: Session = Depends(get_db),
    admin_data: dict = Depends(get_admin_session)
):
    current_user = admin_data["user"]
    TenantAdminService.approve_driver_with_fleet(
        db=db,
        user=current_user,
        driver_id=driver_id,
        allowed_vehicle_categories=data.allowed_vehicle_categories
    )

    return {
        "message": "Driver approved and INDIVIDUAL fleet created",
        "driver_id": driver_id
    }


@router.post("/{driver_id}/reject")
def reject_driver(
    driver_id: int,
    data: DriverRejectRequest,
    db: Session = Depends(get_db),
    admin_data: dict = Depends(get_admin_session)
):
    current_user = admin_data["user"]
    TenantAdminService.reject_driver_with_reason(
        db=db,
        user=current_user,
        driver_id=driver_id,
        reason=data.reason
    )

    return {
        "message": "Driver rejected",
        "driver_id": driver_id
    }


@router.get("/{driver_id}/documents", response_model=list[DriverDocumentResponse])
def get_driver_documents(
    driver_id: int,
    db: Session = Depends(get_db),
    admin_data: dict = Depends(get_admin_session)
):
    current_user = admin_data["user"]
    documents = TenantAdminService.get_driver_documents(db, current_user, driver_id)

    return [
        DriverDocumentResponse(
            document_id=doc.kyc_id,
            document_type=doc.document_type,
            document_number=doc.document_number,
            file_url=getattr(doc, "file_url", None),
            verification_status=doc.verification_status
        )
        for doc in documents
    ]


@router.get("", response_model=List[DriverListResponse])
def get_all_drivers(
    db: Session = Depends(get_db),
    admin_data: dict = Depends(get_admin_session)
):
    current_user = admin_data["user"]
    drivers = TenantAdminService.get_all_drivers(db, current_user)

    return [
        DriverListResponse(
            driver_id=driver.driver_id,
            full_name=user.full_name,
            phone=user.phone,
            approval_status=driver.approval_status,
            allowed_vehicle_categories=driver.allowed_vehicle_categories,
            driver_type=driver.driver_type
        )
        for driver, user in drivers
    ]


@router.patch("/{driver_id}/status")
def update_driver_status(
    driver_id: int,
    request: ApprovalStatusUpdateRequest,
    db: Session = Depends(get_db),
    admin_data: dict = Depends(get_admin_session)
):
    """Update driver approval status."""
    current_user = admin_data["user"]
    driver = TenantAdminService.update_driver_approval_status(
        db, current_user, driver_id, request.approval_status
    )
    return {
        "message": f"Driver status updated to {request.approval_status}",
        "driver_id": driver_id,
        "approval_status": driver.approval_status
    }


@router.get("/{driver_id}/details", response_model=DriverDetailResponse)
def get_driver_details(
    driver_id: int,
    db: Session = Depends(get_db),
    admin_data: dict = Depends(get_admin_session)
):
    """Get detailed driver info including fleet assignment."""
    current_user = admin_data["user"]
    details = TenantAdminService.get_driver_details(db, current_user, driver_id)
    return DriverDetailResponse(**details)


@router.get("/{driver_id}/documents/detailed", response_model=List[DriverDocumentDetailResponse])
def get_driver_documents_detailed(
    driver_id: int,
    db: Session = Depends(get_db),
    admin_data: dict = Depends(get_admin_session)
):
    """
    Get detailed driver documents with rejection info and review capability.
    
    Returns all documents with:
    - Current status
    - Rejection reason (if rejected)
    - can_review: True if document can be reviewed (not already APPROVED)
    """
    current_user = admin_data["user"]
    tenant_id = TenantAdminService._get_admin_tenant(db, current_user)
    
    # Verify driver belongs to admin's tenant
    driver = (
        db.query(DriverProfile)
        .filter(
            DriverProfile.driver_id == driver_id,
            DriverProfile.tenant_id == tenant_id
        )
        .first()
    )
    
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found or not in your tenant"
        )
    
    all_documents = db.query(UserKYC).filter(UserKYC.user_id == driver_id).all()
    
    # Only return the latest document per type (re-uploads create new records)
    doc_by_type = {}
    for doc in all_documents:
        if doc.document_type not in doc_by_type or doc.kyc_id > doc_by_type[doc.document_type].kyc_id:
            doc_by_type[doc.document_type] = doc
    
    return [
        DriverDocumentDetailResponse(
            document_id=doc.kyc_id,
            document_type=doc.document_type,
            document_number=doc.document_number,
            file_url=doc.file_url,
            verification_status=doc.verification_status,
            rejection_reason=doc.rejection_reason,
            verified_by=doc.verified_by,
            verified_on=doc.verified_on,
            can_review=doc.verification_status != "APPROVED"
        )
        for doc in doc_by_type.values()
    ]


@router.post("/{driver_id}/documents/{document_id}/review")
def review_driver_document(
    driver_id: int,
    document_id: int,
    request: DriverDocumentReviewRequest,
    db: Session = Depends(get_db),
    admin_data: dict = Depends(get_admin_session)
):
    """
    Review (approve/reject) an individual driver document.
    
    Request body:
    - status: "APPROVED" | "REJECTED"
    - rejection_reason: Required if status is REJECTED
    
    Behavior:
    - If REJECTED: document.status = REJECTED, save rejection_reason, 
      set application.status = PARTIALLY_REJECTED
    - If APPROVED: document.status = APPROVED
      If ALL documents APPROVED → application.status = APPROVED
    """
    current_user = admin_data["user"]
    admin_user_id = current_user.user_id
    tenant_id = TenantAdminService._get_admin_tenant(db, current_user)
    
    # Validate status value
    if request.status not in ["APPROVED", "REJECTED"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status must be APPROVED or REJECTED"
        )
    
    # If rejecting, require rejection reason
    if request.status == "REJECTED" and not request.rejection_reason:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rejection reason is required when rejecting a document"
        )
    
    # Verify driver belongs to admin's tenant
    driver = (
        db.query(DriverProfile)
        .filter(
            DriverProfile.driver_id == driver_id,
            DriverProfile.tenant_id == tenant_id
        )
        .first()
    )
    
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found or not in your tenant"
        )
    
    # Get the document
    document = (
        db.query(UserKYC)
        .filter(
            UserKYC.kyc_id == document_id,
            UserKYC.user_id == driver_id
        )
        .first()
    )
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Cannot review already approved document
    if document.verification_status == "APPROVED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify already approved document"
        )
    
    # Update document
    document.verification_status = request.status
    document.verified_by = admin_user_id
    document.verified_on = datetime.now(timezone.utc)
    
    if request.status == "REJECTED":
        document.rejection_reason = request.rejection_reason
        # Set driver application to PARTIALLY_REJECTED
        driver.approval_status = "PARTIALLY_REJECTED"
    else:
        document.rejection_reason = None
        
        # Check if ALL latest documents for this driver are now APPROVED
        # Get latest document for each type
        all_docs = db.query(UserKYC).filter(UserKYC.user_id == driver_id).all()
        
        # Group by document type and get latest
        doc_by_type = {}
        for doc in all_docs:
            if doc.document_type not in doc_by_type or doc.kyc_id > doc_by_type[doc.document_type].kyc_id:
                doc_by_type[doc.document_type] = doc
        
        # Check if all latest docs are approved
        all_approved = all(d.verification_status == "APPROVED" for d in doc_by_type.values())
        
        if all_approved:
            driver.approval_status = "APPROVED"
    
    db.commit()
    
    return {
        "message": f"Document {request.status.lower()}",
        "document_id": document_id,
        "document_type": document.document_type,
        "verification_status": document.verification_status,
        "driver_approval_status": driver.approval_status
    }