from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.api.admin.auth import get_admin_session
from app.services.tenant_admin_service import TenantAdminService
from app.schemas.vehicle import Vehicle
from app.schemas.admin import  (
    VehicleDocumentAdminResponse, 
    VehiclePendingApprovalResponse,
    VehicleApprovalRequest,
    VehicleRejectionRequest,
    ApprovalStatusUpdateRequest
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
    admin_data: dict = Depends(get_admin_session)
):
    """Get all vehicles pending approval for admin's tenant."""
    current_user = admin_data["user"]
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


@router.get("", response_model=list[Vehicle])
def get_all_vehicles(
    db: Session = Depends(get_db),
    admin_data: dict = Depends(get_admin_session)
):
    """Get all vehicles for admin's tenant (both pending and approved)."""
    current_user = admin_data["user"]
    vehicles = TenantAdminService.get_all_vehicles(db, current_user)
    
    return [
        Vehicle(
            vehicle_id=v.vehicle_id,
            tenant_id=v.tenant_id,
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
    admin_data: dict = Depends(get_admin_session)
):
    """Approve or reject a vehicle."""
    current_user = admin_data["user"]
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
    admin_data: dict = Depends(get_admin_session)
):
    """Reject a vehicle with a mandatory rejection reason."""
    current_user = admin_data["user"]
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
    admin_data: dict = Depends(get_admin_session)
):
    current_user = admin_data["user"]
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


@router.get("/approved", response_model=list[Vehicle])
def get_approved_vehicles(
    db: Session = Depends(get_db),
    admin_data: dict = Depends(get_admin_session)
):
    """Get all approved vehicles for admin's tenant."""
    current_user = admin_data["user"]
    vehicles = TenantAdminService.get_approved_vehicles(db, current_user)
    
    return [
        Vehicle(
            vehicle_id=v.vehicle_id,
            tenant_id=v.tenant_id,
            fleet_id=v.fleet_id,
            category=v.category,
            registration_no=v.registration_no,
            status=v.status,
            approval_status=v.approval_status,
            created_on=v.created_on
        )
        for v in vehicles
    ]


@router.patch("/{vehicle_id}/status")
def update_vehicle_status(
    vehicle_id: int,
    request: ApprovalStatusUpdateRequest,
    db: Session = Depends(get_db),
    admin_data: dict = Depends(get_admin_session)
):
    """Update vehicle approval status."""
    current_user = admin_data["user"]
    vehicle = TenantAdminService.update_vehicle_approval_status(
        db, current_user, vehicle_id, request.approval_status
    )
    return {
        "message": f"Vehicle status updated to {request.approval_status}",
        "vehicle_id": vehicle_id,
        "approval_status": vehicle.approval_status
    }

