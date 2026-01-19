from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.api.deps.auth import get_current_user
from app.services.tenant_admin_service import TenantAdminService
from app.models.identity import AppUser

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter(
    prefix="/tenant-admin",
    tags=["Tenant Admin"]
)

@router.post("/drivers/{driver_id}/approve")
def approve_driver(
    driver_id: int,
    db: Session = Depends(get_db),
    current_user: AppUser = Depends(get_current_user)
):
    TenantAdminService.approve_driver(db, current_user, driver_id)
    return {"message": "Driver approved successfully"}

@router.post("/drivers/{driver_id}/reject")
def reject_driver(
    driver_id: int,
    db: Session = Depends(get_db),
    current_user: AppUser = Depends(get_current_user)
):
    TenantAdminService.reject_driver(db, current_user, driver_id)
    return {"message": "Driver rejected successfully"}
