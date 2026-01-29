""" from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.api.deps.auth import get_current_user
from app.schemas.trip import TripResponse
from app.models.trips import Trip
from app.models.identity import AppUser

router = APIRouter(prefix="/trips", tags=["Trips"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/{trip_id}", response_model=TripResponse)
def get_trip_status(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: AppUser = Depends(get_current_user)
):
    trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    # Basic authorization: rider of the trip or assigned driver; admins can view all
    if current_user.role == "RIDER" and trip.rider_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not your trip")
    if current_user.role == "DRIVER" and trip.driver_id not in (None, current_user.user_id):
        # If driver_id is set and not this driver, forbid
        raise HTTPException(status_code=403, detail="Not your trip")

    return trip """ 
