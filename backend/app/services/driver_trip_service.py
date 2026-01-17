from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.trips import Trip
from app.models.dispatch import DispatchAttempt
from datetime import timezone,datetime
from sqlalchemy import and_
class DriverTripService:

    @staticmethod
    def get_trip_offers(db: Session, driver_id: int):
        offers = (
            db.query(DispatchAttempt, Trip)
            .join(Trip, Trip.trip_id == DispatchAttempt.trip_id)
            .filter(
                DispatchAttempt.driver_id == driver_id,
                DispatchAttempt.response == "SENT",
                Trip.status == "REQUESTED"
            )
            .all()
        )

        return [
            {
                "trip_id": trip.trip_id,
                "pickup_lat": trip.pickup_lat,
                "pickup_lng": trip.pickup_lng,
                "drop_lat": trip.drop_lat,
                "drop_lng": trip.drop_lng
            }
            for _, trip in offers
        ]
    @staticmethod
    def accept_trip(db: Session, driver_id: int, trip_id: int):
        trip = (
            db.query(Trip)
            .filter(
                Trip.trip_id == trip_id,
                Trip.status == "REQUESTED"
            )
            .with_for_update()
            .first()
        )

        if not trip:
            raise HTTPException(400, "Trip already assigned")

        attempt = (
            db.query(DispatchAttempt)
            .filter(
                DispatchAttempt.trip_id == trip_id,
                DispatchAttempt.driver_id == driver_id
            )
            .first()
        )

        if not attempt:
            raise HTTPException(403, "No dispatch for this driver")

        # Assign trip
        trip.driver_id = driver_id
        trip.status = "ASSIGNED"
        trip.assigned_at = datetime.now(timezone.utc)

        # Update dispatch attempts
        attempt.response = "ACCEPTED"
        attempt.responded_at = datetime.now(timezone.utc)

        db.query(DispatchAttempt).filter(
            and_(
                DispatchAttempt.trip_id == trip_id,
                DispatchAttempt.driver_id != driver_id
            )
        ).update(
            {
                DispatchAttempt.response: "REJECTED",
                DispatchAttempt.responded_at: datetime.now(timezone.utc)
            }
        )

        db.commit()
        return {"message": "Trip accepted"}

    @staticmethod
    def start_trip(db: Session, driver_id: int, trip_id: int):
        trip = (
            db.query(Trip)
            .filter(
                Trip.trip_id == trip_id,
                Trip.driver_id == driver_id,
                Trip.status == "ASSIGNED"
            )
            .first()
        )

        if not trip:
            raise HTTPException(400, "Trip cannot be started")

        trip.status = "PICKED_UP"
        trip.picked_up_at = datetime.now(timezone.utc)

        db.commit()
        return {"message": "Trip started"}

    @staticmethod
    def complete_trip(db: Session, driver_id: int, trip_id: int):
        trip = (
            db.query(Trip)
            .filter(
                Trip.trip_id == trip_id,
                Trip.driver_id == driver_id,
                Trip.status == "PICKED_UP"
            )
            .first()
        )

        if not trip:
            raise HTTPException(400, "Trip cannot be completed")

        trip.status = "COMPLETED"
        trip.completed_at = datetime.now(timezone.utc)

        db.commit()
        return {"message": "Trip completed"}
    
    
