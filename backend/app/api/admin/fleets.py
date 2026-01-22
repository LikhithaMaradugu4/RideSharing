from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.api.deps.auth import get_current_user
from app.services.tenant_admin_service import TenantAdminService
from app.models.identity import AppUser
from app.schemas.admin import FleetApprovalResponse, PendingFleetResponse, FleetPendingDocument


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
    current_user: AppUser = Depends(get_current_user)
):
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
    current_user: AppUser = Depends(get_current_user)
):
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
    current_user: AppUser = Depends(get_current_user)
):
    TenantAdminService.reject_fleet(
        db=db,
        user=current_user,
        fleet_id=fleet_id
    )

    return FleetApprovalResponse(
        fleet_id=fleet_id,
        approval_status="REJECTED"
    )
