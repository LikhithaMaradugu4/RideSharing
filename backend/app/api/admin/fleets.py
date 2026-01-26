from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.api.admin.auth import get_admin_session
from app.services.tenant_admin_service import TenantAdminService
from app.schemas.admin import FleetApprovalResponse, PendingFleetResponse, FleetPendingDocument, FleetListResponse


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
