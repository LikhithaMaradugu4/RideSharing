from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.api.deps.auth import get_current_user
from app.services.tenant_admin_service import TenantAdminService
from app.models.identity import AppUser
from app.schemas.admin import VehicleDocumentAdminResponse

router = APIRouter(prefix="/vehicles", tags=["Admin - Vehicles"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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
