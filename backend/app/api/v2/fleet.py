from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.api.deps.jwt_auth import get_current_user
from app.core.database import SessionLocal
from app.models.identity import AppUser
from app.models.core import City
from app.schemas.fleet import (
    FleetApplyRequest,
    FleetApplyResponse,
    FleetResponse,
    FleetDriverInviteRequest,
    FleetDriverResponse,
    FleetDriverListResponse,
    FleetAssignmentCreateRequest,
    FleetAssignmentResponse,
    FleetAssignmentListResponse,
    FleetCityAddRequest,
    FleetCityResponse,
    FleetCityListResponse,
    FleetDriverAvailabilityListResponse
)
from app.services.fleet_service import FleetService
from app.services.fleet_owner_service import FleetOwnerService
from app.services.driver_work_availability_service import DriverWorkAvailabilityService


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


# ==================== Fleet Owner Driver Management ====================

@router.post("/drivers/invite", response_model=FleetDriverResponse)
def invite_driver(
    data: FleetDriverInviteRequest,
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

    association = FleetOwnerService.invite_driver(db=db, user=user, driver_id=data.driver_id)

    driver_user = db.query(AppUser).filter(AppUser.user_id == data.driver_id).first()

    return FleetDriverResponse(
        driver_id=association.driver_id,
        full_name=driver_user.full_name if driver_user else "",
        phone=driver_user.phone if driver_user else "",
        start_date=association.start_date,
        end_date=association.end_date
    )


@router.get("/drivers", response_model=FleetDriverListResponse)
def list_fleet_drivers(
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

    rows = FleetOwnerService.list_drivers(db=db, user=user)

    drivers = [
        FleetDriverResponse(
            driver_id=user_row.user_id,
            full_name=user_row.full_name,
            phone=user_row.phone,
            start_date=assoc.start_date,
            end_date=assoc.end_date
        )
        for assoc, user_row in rows
    ]

    return FleetDriverListResponse(drivers=drivers, total=len(drivers))


@router.post("/drivers/{driver_id}/remove")
def remove_fleet_driver(
    driver_id: int,
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

    FleetOwnerService.remove_driver(db=db, user=user, driver_id=driver_id)

    return {"message": "Driver removed from fleet"}


# ==================== Fleet Owner Assignments ====================

@router.post("/assignments", response_model=FleetAssignmentResponse)
def create_assignment(
    data: FleetAssignmentCreateRequest,
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

    assignment = FleetOwnerService.create_assignment(
        db=db,
        user=user,
        driver_id=data.driver_id,
        vehicle_id=data.vehicle_id
    )

    return FleetAssignmentResponse(
        assignment_id=assignment.assignment_id,
        driver_id=assignment.driver_id,
        vehicle_id=assignment.vehicle_id,
        start_time=assignment.start_time,
        end_time=assignment.end_time
    )


@router.post("/assignments/{assignment_id}/end", response_model=FleetAssignmentResponse)
def end_assignment(
    assignment_id: int,
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

    assignment = FleetOwnerService.end_assignment(db=db, user=user, assignment_id=assignment_id)

    return FleetAssignmentResponse(
        assignment_id=assignment.assignment_id,
        driver_id=assignment.driver_id,
        vehicle_id=assignment.vehicle_id,
        start_time=assignment.start_time,
        end_time=assignment.end_time
    )


@router.get("/assignments/active", response_model=FleetAssignmentListResponse)
def list_active_assignments(
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

    assignments = FleetOwnerService.list_active_assignments(db=db, user=user)

    items = [
        FleetAssignmentResponse(
            assignment_id=a.assignment_id,
            driver_id=a.driver_id,
            vehicle_id=a.vehicle_id,
            start_time=a.start_time,
            end_time=a.end_time
        )
        for a in assignments
    ]

    return FleetAssignmentListResponse(assignments=items, total=len(items))


# ==================== Fleet Cities ====================

@router.post("/cities", response_model=FleetCityResponse)
def add_fleet_city(
    data: FleetCityAddRequest,
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

    record = FleetOwnerService.add_city(db=db, user=user, city_id=data.city_id)

    city = db.query(City).filter(City.city_id == record.city_id).first()
    return FleetCityResponse(city_id=record.city_id, city_name=city.name if city else "")


@router.get("/cities", response_model=FleetCityListResponse)
def list_fleet_cities(
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

    rows = FleetOwnerService.list_cities(db=db, user=user)
    cities = [
        FleetCityResponse(city_id=city.city_id, city_name=city.name)
        for _, city in rows
    ]
    return FleetCityListResponse(cities=cities, total=len(cities))


@router.delete("/cities/{city_id}")
def remove_fleet_city(
    city_id: int,
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

    FleetOwnerService.remove_city(db=db, user=user, city_id=city_id)
    return {"message": "City removed"}


# ---------------------- Driver Availability (Fleet Owner View) ----------------------

@router.get("/drivers/availability", response_model=FleetDriverAvailabilityListResponse)
def view_drivers_availability(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """View all drivers' work availability in fleet for date range."""
    user_id = current_user.get("user_id")
    user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    rows = DriverWorkAvailabilityService.list_fleet_driver_availability(
        db=db,
        user=user,
        start_date=start_date,
        end_date=end_date
    )

    from app.schemas.fleet import FleetDriverAvailabilityItem

    items = [
        FleetDriverAvailabilityItem(
            availability_id=avail.availability_id,
            driver_id=app_user.user_id,
            driver_phone=app_user.phone_number,
            date=avail.date,
            is_available=avail.is_available,
            note=avail.note
        )
        for avail, app_user in rows
    ]

    return FleetDriverAvailabilityListResponse(items=items, total=len(items))

