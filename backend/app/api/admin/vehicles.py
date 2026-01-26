from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.api.deps.auth import get_current_user
from app.services.tenant_admin_service import TenantAdminService
from app.models.identity import AppUser
from app.schemas.admin import (
    VehicleDocumentAdminResponse, 
    VehiclePendingApprovalResponse,
    VehicleApprovalRequest,
    VehicleRejectionRequest
)

router = APIRouter(prefix="/vehicles", tags=["Admin - Vehicles"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/pending-approval", response_model=list[VehiclePendingApprovalResponse])
def get_pending_vehicles(
    db: Session = Depends(get_db),
    current_user: AppUser = Depends(get_current_user)
):
    """Get all vehicles pending approval for admin's tenant."""
    vehicles = TenantAdminService.get_pending_vehicles(db, current_user)
    
    return [
        VehiclePendingApprovalResponse(
            vehicle_id=v.vehicle_id,
            fleet_id=v.fleet_id,
            category=v.category,
            registration_no=v.registration_no,
            status=v.status,
            approval_status=v.approval_status,
            created_on=v.created_on
        )
        for v in vehicles
    ]


@router.post("/{vehicle_id}/approve")
def approve_vehicle(
    vehicle_id: int,
    request: VehicleApprovalRequest,
    db: Session = Depends(get_db),
    current_user: AppUser = Depends(get_current_user)
):
    """Approve or reject a vehicle."""
    TenantAdminService.approve_vehicle(
        db, 
        current_user, 
        vehicle_id, 
        request.approval_status,
        request.rejection_reason
    )
    
    return {"message": f"Vehicle {request.approval_status.lower()} successfully"}


@router.post("/{vehicle_id}/reject")
def reject_vehicle(
    vehicle_id: int,
    request: VehicleRejectionRequest,
    db: Session = Depends(get_db),
    current_user: AppUser = Depends(get_current_user)
):
    """Reject a vehicle with a mandatory rejection reason."""
    TenantAdminService.approve_vehicle(
        db, 
        current_user, 
        vehicle_id, 
        "REJECTED",
        request.rejection_reason
    )
    
    return {"message": "Vehicle rejected successfully", "rejection_reason": request.rejection_reason}


@router.get("/{vehicle_id}/documents", response_model=list[VehicleDocumentAdminResponse])
def get_vehicle_documents(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: AppUser = Depends(get_current_user)
):
    documents = TenantAdminService.get_vehicle_documents(db, current_user, vehicle_id)

    return [
        VehicleDocumentAdminResponse(
            document_id=doc.document_id,
            document_type=doc.document_type,
            file_url=doc.file_url,
            verification_status=doc.verification_status
        )
        for doc in documents
    ]


