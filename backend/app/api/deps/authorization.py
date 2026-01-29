"""
Authorization Helpers - Capability-based authorization checks.

These helpers check domain capability using database tables, not just app_user.role.
- Identity = app_user.role (RIDER, DRIVER, TENANT_ADMIN, PLATFORM_ADMIN)
- Capability = existence + status in domain tables (driver_profile, fleet, etc.)

Usage:
    from app.api.deps.authorization import require_approved_driver
    
    @router.post("/location")
    def update_location(
        db: Session = Depends(get_db),
        driver_profile: DriverProfile = Depends(require_approved_driver)
    ):
        # driver_profile is guaranteed to be APPROVED
        ...
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps.jwt_auth import get_current_user
from app.core.database import SessionLocal
from app.models.fleet import DriverProfile, Fleet
from app.models.identity import AppUser


def get_db():
    """Database session dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def require_approved_driver(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> DriverProfile:
    """
    Require the current user to be an APPROVED driver.
    
    Checks:
    - driver_profile exists for current_user.user_id
    - driver_profile.approval_status == "APPROVED"
    
    Returns:
        DriverProfile object if valid
    
    Raises:
        HTTPException 403 if not a valid approved driver
    """
    user_id = current_user.get("user_id")
    
    profile = (
        db.query(DriverProfile)
        .filter(DriverProfile.driver_id == user_id)
        .first()
    )
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Driver profile not found"
        )
    
    if profile.approval_status != "APPROVED":
        print("AUTH DEBUG → user_id:", user_id)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Driver is not approved"
        )

    return profile


def require_fleet_owner(
    fleet_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> Fleet:
    """
    Require the current user to be an APPROVED fleet owner.
    
    Checks:
    - fleet exists where owner_user_id == current_user.user_id
    - fleet.approval_status == "APPROVED"
    - Optionally: fleet.fleet_type matches required type
    
    Args:
        fleet_type: Optional fleet type filter ("BUSINESS" or "INDIVIDUAL")
    
    Returns:
        Fleet object if valid
    
    Raises:
        HTTPException 403 if not a valid approved fleet owner
    """
    user_id = current_user.get("user_id")
    
    query = db.query(Fleet).filter(Fleet.owner_user_id == user_id)
    
    if fleet_type:
        query = query.filter(Fleet.fleet_type == fleet_type)
    
    fleet = query.filter(Fleet.approval_status == "APPROVED").first()
    
    if not fleet:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Approved fleet not found for this user"
        )
    
    return fleet


def require_tenant_admin(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Require the current user to be a TENANT_ADMIN.
    
    This is a role-based check (not capability-based) since tenant admins
    are identified by their role, not by a separate domain table.
    
    Returns:
        current_user dict if valid
    
    Raises:
        HTTPException 403 if not a tenant admin
    """
    role = current_user.get("role")
    
    if role != "TENANT_ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant admin access required"
        )
    
    return current_user


def require_platform_admin(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Require the current user to be a PLATFORM_ADMIN.
    
    Returns:
        current_user dict if valid
    
    Raises:
        HTTPException 403 if not a platform admin
    """
    role = current_user.get("role")
    
    if role != "PLATFORM_ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Platform admin access required"
        )
    
    return current_user


# ---------------------- Convenience Functions ----------------------
# These can be called directly from service layer (not as dependencies)

def get_approved_driver_profile(db: Session, user_id: int) -> Optional[DriverProfile]:
    """
    Get approved driver profile for a user ID.
    
    Returns None if not found or not approved.
    """
    profile = (
        db.query(DriverProfile)
        .filter(
            DriverProfile.driver_id == user_id,
            DriverProfile.approval_status == "APPROVED"
        )
        .first()
    )
    return profile


def get_approved_fleet(db: Session, user_id: int, fleet_type: Optional[str] = None) -> Optional[Fleet]:
    """
    Get approved fleet for a user ID.
    
    Returns None if not found or not approved.
    """
    query = db.query(Fleet).filter(
        Fleet.owner_user_id == user_id,
        Fleet.approval_status == "APPROVED"
    )
    
    if fleet_type:
        query = query.filter(Fleet.fleet_type == fleet_type)
    
    return query.first()


def is_approved_driver(db: Session, user_id: int) -> bool:
    """Check if user is an approved driver."""
    return get_approved_driver_profile(db, user_id) is not None


def is_fleet_owner(db: Session, user_id: int) -> bool:
    """Check if user is an approved fleet owner."""
    return get_approved_fleet(db, user_id) is not None
