""" from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.api.deps.auth import get_current_user
from app.schemas.trip import RiderRequestTrip, TripResponse
from app.services.driver_trip_service import DriverTripService
from app.models.identity import AppUser

router = APIRouter(prefix="/drivers", tags=["DriverTrips"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/trips/offers")
def get_trip_offers(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return DriverTripService.get_trip_offers(
        db=db,
        driver_id=current_user.user_id
    )

@router.post("/trips/{trip_id}/accept")
def accept_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return DriverTripService.accept_trip(
        db=db,
        driver_id=current_user.user_id,
        trip_id=trip_id
    )



@router.post("/trips/{trip_id}/complete")
def complete_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return DriverTripService.complete_trip(
        db=db,
        driver_id=current_user.user_id,
        trip_id=trip_id
    )

@router.post("/trips/{trip_id}/start")
def start_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return DriverTripService.start_trip(
        db=db,
        driver_id=current_user.user_id,
        trip_id=trip_id
    )

@router.post("/trips/{trip_id}/complete")
def complete_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return DriverTripService.complete_trip(
        db=db,
        driver_id=current_user.user_id,
        trip_id=trip_id

    ) """