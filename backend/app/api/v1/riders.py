from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.api.deps.auth import get_current_user
from app.schemas.trip import RiderRequestTrip, TripResponse
from app.services.trip_service import TripService
from app.models.identity import AppUser

router = APIRouter(prefix="/riders", tags=["Riders"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

