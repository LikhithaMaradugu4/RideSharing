from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.api.deps.auth import get_current_user
from app.schemas.ride_request import RideRequestCreate, RideRequestResponse
from app.services.ride_request_service import RideRequestService
from app.schemas.ride_request import RideRequestConfirm

from app.models.identity import AppUser

router = APIRouter(prefix="/ride-requests", tags=["Ride Requests"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("", response_model=RideRequestResponse)
def create_ride_request(
    data: RideRequestCreate,
    db: Session = Depends(get_db),
    current_user: AppUser = Depends(get_current_user)
):
    return RideRequestService.create_request(db, current_user, data)


@router.post("/{request_id}/confirm")
def confirm_ride_request(
    request_id: int,
    data: RideRequestConfirm,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    trip = RideRequestService.confirm_request(
        db=db,
        user=current_user,
        request_id=request_id,
        data=data
    )

    return {
        "trip_id": trip.trip_id,
        "status": trip.status
    }






