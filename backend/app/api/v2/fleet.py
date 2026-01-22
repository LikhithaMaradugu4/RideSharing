from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps.jwt_auth import get_current_user
from app.core.database import SessionLocal
from app.models.identity import AppUser
from app.schemas.fleet import FleetApplyRequest, FleetApplyResponse, FleetResponse
from app.services.fleet_service import FleetService


router = APIRouter(prefix="/fleet", tags=["Phase-2 Fleet"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/apply", response_model=FleetApplyResponse)
def apply_fleet(
    data: FleetApplyRequest,
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

    fleet = FleetService.apply_fleet(db=db, user=user, data=data)

    return FleetApplyResponse(
        fleet_id=fleet.fleet_id,
        approval_status=fleet.approval_status
    )


@router.get("/my", response_model=FleetResponse)
def get_my_fleet(
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

    fleet = FleetService.get_my_fleet(db=db, user=user)

    return FleetResponse(
        fleet_id=fleet.fleet_id,
        fleet_name=fleet.fleet_name,
        tenant_id=fleet.tenant_id,
        approval_status=fleet.approval_status,
        status=fleet.status
    )
