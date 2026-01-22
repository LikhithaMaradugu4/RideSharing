from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps.jwt_auth import get_current_user
from app.core.database import SessionLocal
from app.models.identity import AppUser
from app.schemas.user import ProfileResponse, ProfileUpdateRequest


router = APIRouter(prefix="/profile", tags=["Phase-2 Profile"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=ProfileResponse)
def get_profile(
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

    return ProfileResponse(
        user_id=user.user_id,
        full_name=user.full_name,
        phone=user.phone,
        gender=user.gender,
        city_id=user.city_id,
        country_code=user.country_code
    )


@router.put("", response_model=ProfileResponse)
def update_profile(
    data: ProfileUpdateRequest,
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

    # Update only provided fields
    if data.full_name is not None:
        user.full_name = data.full_name
    if data.gender is not None:
        user.gender = data.gender
    if data.city_id is not None:
        user.city_id = data.city_id

    db.commit()
    db.refresh(user)

    return ProfileResponse(
        user_id=user.user_id,
        full_name=user.full_name,
        phone=user.phone,
        gender=user.gender,
        city_id=user.city_id,
        country_code=user.country_code
    )
