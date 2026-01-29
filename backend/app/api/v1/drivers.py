""" from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.api.deps.auth import get_current_user
from app.schemas.driver import DriverApplyRequest, DriverProfileResponse, DriverMeResponse, TenantResponse
from app.services.driver_service import DriverService
from app.services.tenant_service import TenantService
from app.models.identity import AppUser
from app.services.driver_shift_service import DriverShiftService
from app.schemas.driver_location import DriverLocationUpdateRequest
from app.services.driver_location_service import DriverLocationService



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter(prefix="/drivers", tags=["Drivers"])

@router.get("/tenants", response_model=list[TenantResponse])
def get_available_tenants(
    db: Session = Depends(get_db)
):
    #Get all available (ACTIVE) tenants for driver application
    return TenantService.get_active_tenants(db)

@router.post(
    "/apply",
    response_model=DriverProfileResponse,
    status_code=status.HTTP_201_CREATED
)
def apply_as_driver(
    data: DriverApplyRequest,
    db: Session = Depends(get_db),
    current_user: AppUser = Depends(get_current_user)
):
    return DriverService.apply_to_tenant(
        db=db,
        user=current_user,
        data=data
    )

@router.get(
    "/me",
    response_model=DriverMeResponse
)
def get_my_driver_profile(
    db: Session = Depends(get_db),
    current_user: AppUser = Depends(get_current_user)
):
    return DriverService.get_my_profile(
        db=db,
        user=current_user
    )


@router.post("/shift/start")
def start_driver_shift(
    db: Session = Depends(get_db),
    current_user: AppUser = Depends(get_current_user)
):
    DriverShiftService.start_shift(db, current_user)
    return {"message": "Driver shift started successfully"}

@router.post("/shift/end")
def end_driver_shift(
    db: Session = Depends(get_db),
    current_user: AppUser = Depends(get_current_user)
):
    DriverShiftService.end_shift(db, current_user)
    return {"message": "Driver shift ended successfully"}

@router.post("/location")
def update_driver_location(
    data: DriverLocationUpdateRequest,
    db: Session = Depends(get_db),
    current_user: AppUser = Depends(get_current_user)
):
    DriverLocationService.update_location(
        db=db,
        user=current_user,
        latitude=data.latitude,
        longitude=data.longitude
    )
    return {"message": "Location updated successfully"}
"""
