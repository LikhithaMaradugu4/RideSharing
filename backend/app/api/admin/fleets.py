from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.core.database import SessionLocal
from app.api.admin.auth import get_admin_session
from app.services.tenant_admin_service import TenantAdminService
from app.schemas.admin import (
    FleetApprovalResponse, PendingFleetResponse, FleetPendingDocument,
    FleetListResponse, ApprovalStatusUpdateRequest,
    FleetDocumentReviewRequest, FleetDocumentDetailResponse
)


router = APIRouter(prefix="/fleets", tags=["Admin - Fleets"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/pending", response_model=list[PendingFleetResponse])
def get_pending_fleets(
    db: Session = Depends(get_db),
    admin_data: dict = Depends(get_admin_session)
):
    current_user = admin_data["user"]
    pending = TenantAdminService.get_pending_fleets_with_docs(db, current_user)

    response: list[PendingFleetResponse] = []
    for fleet, docs in pending:
        response.append(
            PendingFleetResponse(
                fleet_id=fleet.fleet_id,
                fleet_name=fleet.fleet_name,
                fleet_type=fleet.fleet_type,
                approval_status=fleet.approval_status,
                status=fleet.status,
                documents=[
                    FleetPendingDocument(
                        document_id=d.document_id,
                        document_type=d.document_type,
                        file_url=d.file_url,
                        verification_status=d.verification_status,
                    )
                    for d in docs
                ]
            )
        )

    return response


@router.post("/{fleet_id}/approve", response_model=FleetApprovalResponse)
def approve_fleet(
    fleet_id: int,
    db: Session = Depends(get_db),
    admin_data: dict = Depends(get_admin_session)
):
    current_user = admin_data["user"]
    TenantAdminService.approve_fleet(
        db=db,
        user=current_user,
        fleet_id=fleet_id
    )

    return FleetApprovalResponse(
        fleet_id=fleet_id,
        approval_status="APPROVED"
    )


@router.post("/{fleet_id}/reject", response_model=FleetApprovalResponse)
def reject_fleet(
    fleet_id: int,
    db: Session = Depends(get_db),
    admin_data: dict = Depends(get_admin_session)
):
    current_user = admin_data["user"]
    TenantAdminService.reject_fleet(
        db=db,
        user=current_user,
        fleet_id=fleet_id
    )

    return FleetApprovalResponse(
        fleet_id=fleet_id,
        approval_status="REJECTED"
    )


@router.get("", response_model=list[FleetListResponse])
def get_fleets(
    db: Session = Depends(get_db),
    admin_data: dict = Depends(get_admin_session)
):
    current_user = admin_data["user"]
    fleets = TenantAdminService.get_all_fleets(db, current_user)

    return [
        FleetListResponse(
          fleet_id=fleet.fleet_id,
          fleet_name=fleet.fleet_name,
          fleet_type=fleet.fleet_type,
          approval_status=fleet.approval_status,
          status=fleet.status
        )
        for fleet in fleets
    ]


@router.patch("/{fleet_id}/status")
def update_fleet_status(
    fleet_id: int,
    request: ApprovalStatusUpdateRequest,
    db: Session = Depends(get_db),
    admin_data: dict = Depends(get_admin_session)
):
    """Update fleet approval status."""
    current_user = admin_data["user"]
    fleet = TenantAdminService.update_fleet_approval_status(
        db, current_user, fleet_id, request.approval_status
    )
    return {
        "message": f"Fleet status updated to {request.approval_status}",
        "fleet_id": fleet_id,
        "approval_status": fleet.approval_status
    }


@router.get("/{fleet_id}/documents/detailed", response_model=list[FleetDocumentDetailResponse])
def get_fleet_documents_detailed(
    fleet_id: int,
    db: Session = Depends(get_db),
    admin_data: dict = Depends(get_admin_session)
):
    """
    Get detailed fleet documents with rejection info and review capability.
    """
    from app.models.fleet import Fleet, FleetDocument
    
    current_user = admin_data["user"]
    tenant_id = TenantAdminService._get_admin_tenant(db, current_user)
    
    fleet = (
        db.query(Fleet)
        .filter(
            Fleet.fleet_id == fleet_id,
            Fleet.tenant_id == tenant_id
        )
        .first()
    )
    
    if not fleet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fleet not found or not in your tenant"
        )
    
    all_documents = db.query(FleetDocument).filter(FleetDocument.fleet_id == fleet_id).all()
    
    # Only return the latest document per type (re-uploads create new records)
    doc_by_type = {}
    for doc in all_documents:
        if doc.document_type not in doc_by_type or doc.document_id > doc_by_type[doc.document_type].document_id:
            doc_by_type[doc.document_type] = doc
    
    return [
        FleetDocumentDetailResponse(
            document_id=doc.document_id,
            document_type=doc.document_type,
            file_url=doc.file_url,
            verification_status=doc.verification_status,
            rejection_reason=doc.rejection_reason,
            verified_by=doc.verified_by,
            verified_on=doc.verified_on,
            can_review=doc.verification_status != "APPROVED"
        )
        for doc in doc_by_type.values()
    ]


@router.post("/{fleet_id}/documents/{document_id}/review")
def review_fleet_document(
    fleet_id: int,
    document_id: int,
    request: FleetDocumentReviewRequest,
    db: Session = Depends(get_db),
    admin_data: dict = Depends(get_admin_session)
):
    """
    Review (approve/reject) an individual fleet document.
    
    Behavior:
    - If REJECTED: doc status = REJECTED, save rejection_reason, fleet → PARTIALLY_REJECTED
    - If APPROVED: doc status = APPROVED. If ALL latest docs APPROVED → fleet → APPROVED
    """
    from app.models.fleet import Fleet, FleetDocument
    
    current_user = admin_data["user"]
    admin_user_id = current_user.user_id
    tenant_id = TenantAdminService._get_admin_tenant(db, current_user)
    
    if request.status not in ["APPROVED", "REJECTED"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status must be APPROVED or REJECTED"
        )
    
    if request.status == "REJECTED" and not request.rejection_reason:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rejection reason is required when rejecting a document"
        )
    
    fleet = (
        db.query(Fleet)
        .filter(
            Fleet.fleet_id == fleet_id,
            Fleet.tenant_id == tenant_id
        )
        .first()
    )
    
    if not fleet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fleet not found or not in your tenant"
        )
    
    document = (
        db.query(FleetDocument)
        .filter(
            FleetDocument.document_id == document_id,
            FleetDocument.fleet_id == fleet_id
        )
        .first()
    )
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    if document.verification_status == "APPROVED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify already approved document"
        )
    
    document.verification_status = request.status
    document.verified_by = admin_user_id
    document.verified_on = datetime.now(timezone.utc)
    
    if request.status == "REJECTED":
        document.rejection_reason = request.rejection_reason
        fleet.approval_status = "PARTIALLY_REJECTED"
    else:
        document.rejection_reason = None
        
        # Check if ALL latest documents for this fleet are now APPROVED
        all_docs = db.query(FleetDocument).filter(FleetDocument.fleet_id == fleet_id).all()
        
        # Group by document type and get latest
        doc_by_type = {}
        for doc in all_docs:
            if doc.document_type not in doc_by_type or doc.document_id > doc_by_type[doc.document_type].document_id:
                doc_by_type[doc.document_type] = doc
        
        all_approved = all(d.verification_status == "APPROVED" for d in doc_by_type.values())
        
        if all_approved:
            fleet.approval_status = "APPROVED"
    
    db.commit()
    
    return {
        "message": f"Document {request.status.lower()}",
        "document_id": document_id,
        "document_type": document.document_type,
        "verification_status": document.verification_status,
        "fleet_approval_status": fleet.approval_status
    }
