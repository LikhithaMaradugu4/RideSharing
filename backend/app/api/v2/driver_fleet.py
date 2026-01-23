from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.api.deps.jwt_auth import get_current_user
from app.core.database import SessionLocal
from app.models.identity import AppUser
from app.schemas.fleet import (
    FleetDiscoveryListResponse,
    FleetDiscoveryItemResponse,
    DriverFleetInviteListResponse,
    DriverFleetInviteResponse,
    DriverWorkAvailabilityRequest,
    DriverWorkAvailabilityResponse,
    DriverAvailabilityListResponse
)
from app.services.driver_fleet_service import DriverFleetService
from app.services.driver_work_availability_service import DriverWorkAvailabilityService

router = APIRouter(tags=["Driver Fleet"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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
    user_id = current_user.get("user_id")
    user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    rows = DriverFleetService.list_invites(db=db, user=user)

    invites = []
    seen = set()
    for assoc, fleet, _, city in rows:
        if fleet.fleet_id in seen:
            continue
        seen.add(fleet.fleet_id)
        invites.append(
            DriverFleetInviteResponse(
                fleet_id=fleet.fleet_id,
                fleet_name=fleet.fleet_name,
                city_id=city.city_id,
                city_name=city.name,
                invited_at=assoc.start_date,
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


# ---------------------- Work Availability ----------------------

@router.post("/driver/work-availability", response_model=DriverWorkAvailabilityResponse)
def declare_work_availability(
    request: DriverWorkAvailabilityRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Declare or update driver's work availability for a date."""
    user_id = current_user.get("user_id")
    user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    record = DriverWorkAvailabilityService.declare_availability(
        db=db,
        user=user,
        data_date=request.date,
        is_available=request.is_available,
        note=request.note
    )

    return DriverWorkAvailabilityResponse.from_attributes(record)


@router.get("/driver/work-availability", response_model=DriverAvailabilityListResponse)
def list_work_availability(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List driver's work availability records."""
    user_id = current_user.get("user_id")
    user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    records = DriverWorkAvailabilityService.list_driver_availability(
        db=db,
        user=user,
        start_date=start_date,
        end_date=end_date
    )

    return DriverAvailabilityListResponse(
        records=[DriverWorkAvailabilityResponse.from_attributes(r) for r in records],
        total=len(records)
    )
