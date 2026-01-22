from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps.jwt_auth import get_current_user
from app.core.database import SessionLocal
from app.models.fleet import DriverProfile, Fleet
from app.models.identity import AppUser


router = APIRouter(prefix="/me", tags=["Phase-2 Me"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("")
def get_my_profile(
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

    driver_profile = (
        db.query(DriverProfile)
        .filter(DriverProfile.driver_id == user.user_id)
        .first()
    )
    driver_status = driver_profile.approval_status if driver_profile else "NOT_APPLIED"

    fleet = (
        db.query(Fleet)
        .filter(Fleet.owner_user_id == user.user_id)
        .first()
    )
    fleet_owner_status = fleet.approval_status if fleet else "NOT_APPLIED"

    return {
        "user": {
            "user_id": user.user_id,
            "name": user.full_name,
            "phone": user.phone,
        },
        "driver_status": driver_status,
        "fleet_owner_status": fleet_owner_status,
    }
