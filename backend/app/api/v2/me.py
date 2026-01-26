from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps.jwt_auth import get_current_user
from app.core.database import SessionLocal
from app.models.fleet import DriverProfile, Fleet
from app.models.identity import AppUser


router = APIRouter(prefix="/me", tags=["Phase-2 Me"])


# ============================================================================
# CONSTANTS
# ============================================================================

NORMAL_USER_ROLES = ["RIDER", "DRIVER","FLEET_OWNER"]
ADMIN_ROLES = ["TENANT_ADMIN", "PLATFORM_ADMIN"]


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


@router.get("/capabilities")
def get_capabilities(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get the CURRENT capabilities of the logged-in user.
    
    NORMAL USERS ONLY: Admin tokens are rejected.
    Capabilities are NOT roles and must not be inferred from JWT.
    
    Returns:
    {
        "user_id": int,
        "rider": true,
        "driver": {
            "exists": bool,
            "approval_status": "APPROVED" | "PENDING" | "REJECTED" | null
        },
        "fleet_owner": {
            "exists": bool,
            "approval_status": "APPROVED" | "PENDING" | "REJECTED" | null
        }
    }
    """
    user_id = current_user.get("user_id")
    user_role = current_user.get("role", "").upper()
    
    # REJECT ADMIN TOKENS
    if user_role in ADMIN_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin users cannot access user capabilities endpoint"
        )
    
    # Fetch user record
    user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # ========== DRIVER CAPABILITY ==========
    driver_profile = (
        db.query(DriverProfile)
        .filter(DriverProfile.driver_id == user.user_id)
        .first()
    )
    
    driver_capability = {
        "exists": driver_profile is not None,
        "approval_status": driver_profile.approval_status if driver_profile else None
    }
    
    # ========== FLEET OWNER CAPABILITY ==========
    # Only BUSINESS fleets count as fleet_owner capability
    business_fleet = (
        db.query(Fleet)
        .filter(
            Fleet.owner_user_id == user.user_id,
            Fleet.fleet_type == "BUSINESS"
        )
        .first()
    )
    
    fleet_owner_capability = {
        "exists": business_fleet is not None,
        "approval_status": business_fleet.approval_status if business_fleet else None
    }
    
    return {
        "user_id": user.user_id,
        "rider": True,  # ALWAYS TRUE for normal users
        "driver": driver_capability,
        "fleet_owner": fleet_owner_capability
    }

