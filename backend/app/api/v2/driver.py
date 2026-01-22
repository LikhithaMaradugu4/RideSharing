from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps.jwt_auth import get_current_user
from app.core.database import SessionLocal
from app.models.identity import AppUser
from app.schemas.driver import DriverApplyWithDocumentsRequest
from app.services.driver_service import DriverService

router = APIRouter(prefix="/driver", tags=["Phase-2 Driver"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/apply-with-documents")
def apply_driver_with_documents(
    data: DriverApplyWithDocumentsRequest,
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

    profile = DriverService.apply_with_documents(db=db, user=user, data=data)

    return {
        "message": "Driver application submitted with documents",
        "status": profile.approval_status
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
