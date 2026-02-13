from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.api.deps.jwt_auth import get_current_user
from app.core.database import SessionLocal
from app.models.identity import AppUser
from app.schemas.fleet import (
    FleetDiscoveryListResponse,
    FleetDiscoveryItemResponse,
    DriverFleetInviteListResponse,
    DriverFleetInviteResponse,
    DriverCurrentFleetResponse
)
from app.services.driver_fleet_service import DriverFleetService

router = APIRouter(tags=["Driver Fleet"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------- Current Fleet ----------------------

@router.get("/driver/current-fleet", response_model=DriverCurrentFleetResponse)
def get_current_fleet(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get the driver's currently active fleet association."""
    user_id = current_user.get("user_id")
    user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    fleet_data = DriverFleetService.get_current_fleet(db=db, user=user)
    if not fleet_data:
        raise HTTPException(status_code=404, detail="No active fleet association found")

    return DriverCurrentFleetResponse(**fleet_data)


# ---------------------- Fleet Discovery ----------------------

@router.get("/fleets/discover", response_model=FleetDiscoveryListResponse)
def discover_fleets(
    city_id: Optional[int] = None,
    tenant_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get("user_id")
    user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    rows = DriverFleetService.discover_fleets(
        db=db,
        user=user,
        city_id=city_id,
        tenant_id=tenant_id
    )

    fleets = [
        FleetDiscoveryItemResponse(
            fleet_id=f.fleet_id,
            fleet_name=f.fleet_name,
            city_id=city.city_id,
            city_name=city.name,
            address=None,
            contact_phone=None
        )
        for f, _, city in rows
    ]

    return FleetDiscoveryListResponse(fleets=fleets, total=len(fleets))


# ---------------------- Invitations ----------------------

@router.get("/driver/fleet-invites", response_model=DriverFleetInviteListResponse)
def list_fleet_invites(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all pending fleet invites for the driver."""
    user_id = current_user.get("user_id")
    user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    rows = DriverFleetService.list_invites(db=db, user=user)

    invites = []
    seen = set()
    for invite, fleet, _, city in rows:
        if fleet.fleet_id in seen:
            continue
        seen.add(fleet.fleet_id)
        invites.append(
            DriverFleetInviteResponse(
                fleet_id=fleet.fleet_id,
                fleet_name=fleet.fleet_name,
                city_id=city.city_id,
                city_name=city.name,
                invited_at=invite.invited_at,
                contact_phone=None,
                address=None
            )
        )

    return DriverFleetInviteListResponse(invites=invites, total=len(invites))


@router.post("/driver/fleet-invites/{fleet_id}/accept")
def accept_fleet_invite(
    fleet_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get("user_id")
    user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    DriverFleetService.accept_invite(db=db, user=user, fleet_id=fleet_id)
    return {"message": "Fleet invite accepted"}


@router.post("/driver/fleet-invites/{fleet_id}/reject")
def reject_fleet_invite(
    fleet_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get("user_id")
    user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    DriverFleetService.reject_invite(db=db, user=user, fleet_id=fleet_id)
    return {"message": "Fleet invite rejected"}


# NOTE: Work Availability endpoints have been removed.
# This functionality is no longer supported.