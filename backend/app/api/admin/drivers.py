from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import SessionLocal
from app.api.deps.auth import get_current_user
from app.services.tenant_admin_service import TenantAdminService
from app.models.identity import AppUser
from app.schemas.admin import (
    PendingDriverResponse,
    DriverApproveRequest,
    DriverRejectRequest,
    DriverDocumentResponse
)


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
    current_user: AppUser = Depends(get_current_user)
):
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
    current_user: AppUser = Depends(get_current_user)
):
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
    current_user: AppUser = Depends(get_current_user)
):
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
    current_user: AppUser = Depends(get_current_user)
):
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
