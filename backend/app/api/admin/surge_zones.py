"""
Admin API - Surge Zone Management

Only platform_admin can create, update, activate/deactivate, and delete surge zones.
All mutations sync Redis immediately so fare lookups use cached data.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import SessionLocal
from app.api.admin.auth import get_admin_session
from app.schemas.pricing import (
    SurgeZoneCreateRequest,
    SurgeZoneUpdateRequest,
    SurgeZoneResponse,
)
from app.services.surge_service import SurgeService

router = APIRouter(prefix="/surge-zones", tags=["Platform Admin - Surge Zones"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def require_platform_admin(admin_data: dict = Depends(get_admin_session)) -> dict:
    """Only PLATFORM_ADMIN may manage surge zones."""
    user = admin_data["user"]
    if user.role != "PLATFORM_ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only platform admins can manage surge zones",
        )
    return admin_data


# ------------------------------------------------------------------ #
#  LIST
# ------------------------------------------------------------------ #

@router.get("/", response_model=List[SurgeZoneResponse])
def list_surge_zones(
    city_id: Optional[int] = Query(None, description="Filter by city"),
    db: Session = Depends(get_db),
    admin_data: dict = Depends(require_platform_admin),
):
    """List all surge zones, optionally filtered by city."""
    zones = SurgeService.get_all(db, city_id=city_id)
    return zones


# ------------------------------------------------------------------ #
#  GET ONE
# ------------------------------------------------------------------ #

@router.get("/{surge_zone_id}", response_model=SurgeZoneResponse)
def get_surge_zone(
    surge_zone_id: int,
    db: Session = Depends(get_db),
    admin_data: dict = Depends(require_platform_admin),
):
    """Get a single surge zone by ID."""
    return SurgeService.get_by_id(db, surge_zone_id)


# ------------------------------------------------------------------ #
#  CREATE
# ------------------------------------------------------------------ #

@router.post("/", response_model=SurgeZoneResponse, status_code=status.HTTP_201_CREATED)
def create_surge_zone(
    body: SurgeZoneCreateRequest,
    db: Session = Depends(get_db),
    admin_data: dict = Depends(require_platform_admin),
):
    """
    Create a new surge zone.

    After creation, the active surge zones for the city are synced to Redis.
    """
    user = admin_data["user"]
    zone = SurgeService.create(
        db=db,
        city_id=body.city_id,
        name=body.name,
        boundary_geojson=body.boundary_geojson,
        multiplier=body.multiplier,
        starts_at=body.starts_at,
        ends_at=body.ends_at,
        is_active=body.is_active,
        created_by=user.user_id,
    )
    return zone


# ------------------------------------------------------------------ #
#  UPDATE
# ------------------------------------------------------------------ #

@router.put("/{surge_zone_id}", response_model=SurgeZoneResponse)
def update_surge_zone(
    surge_zone_id: int,
    body: SurgeZoneUpdateRequest,
    db: Session = Depends(get_db),
    admin_data: dict = Depends(require_platform_admin),
):
    """
    Update a surge zone (name, boundary, multiplier, time window, active flag).

    Redis cache is refreshed immediately after update.
    """
    user = admin_data["user"]
    update_data = body.model_dump(exclude_unset=True)
    zone = SurgeService.update(
        db=db,
        surge_zone_id=surge_zone_id,
        update_data=update_data,
        updated_by=user.user_id,
    )
    return zone


# ------------------------------------------------------------------ #
#  ACTIVATE / DEACTIVATE
# ------------------------------------------------------------------ #

@router.patch("/{surge_zone_id}/activate", response_model=SurgeZoneResponse)
def activate_surge_zone(
    surge_zone_id: int,
    activate: bool = Query(True, description="True to activate, False to deactivate"),
    db: Session = Depends(get_db),
    admin_data: dict = Depends(require_platform_admin),
):
    """
    Activate or deactivate a surge zone.

    Pass ?activate=true or ?activate=false.
    Redis cache is refreshed immediately.
    """
    user = admin_data["user"]
    zone = SurgeService.set_active(
        db=db,
        surge_zone_id=surge_zone_id,
        is_active=activate,
        updated_by=user.user_id,
    )
    return zone


# ------------------------------------------------------------------ #
#  DELETE
# ------------------------------------------------------------------ #

@router.delete("/{surge_zone_id}")
def delete_surge_zone(
    surge_zone_id: int,
    db: Session = Depends(get_db),
    admin_data: dict = Depends(require_platform_admin),
):
    """
    Delete a surge zone permanently.

    Redis cache is refreshed immediately after deletion.
    """
    return SurgeService.delete(db, surge_zone_id)
