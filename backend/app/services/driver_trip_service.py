from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.trips import Trip
from app.models.dispatch import DispatchAttempt
from app.models.fleet import DriverProfile
from datetime import timezone,datetime
from sqlalchemy import and_
class DriverTripService:

    @staticmethod
    def get_trip_offers(db: Session, driver_id: int):
        # Check if driver is approved
        profile = (
            db.query(DriverProfile)
            .filter(DriverProfile.driver_id == driver_id)
            .first()
        )

        if not profile:
            raise HTTPException(
                status_code=404,
                detail="Driver profile not found"
            )

        if profile.approval_status != "APPROVED":
            raise HTTPException(
                status_code=403,
                detail="Driver is not approved to accept trips"
            )

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
        # Check if driver is approved
        profile = (
            db.query(DriverProfile)
            .filter(DriverProfile.driver_id == driver_id)
            .first()
        )

        if not profile:
            raise HTTPException(
                status_code=404,
                detail="Driver profile not found"
            )

        if profile.approval_status != "APPROVED":
            raise HTTPException(
                status_code=403,
                detail="Driver is not approved to accept trips"
            )

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
        """
        Complete a trip and calculate final fare.
        
        Sets status to COMPLETED and calculates final_fare using:
        - fare_config (from fare_snapshot or current config)
        - Actual distance traveled
        - Time taken
        - Currency and country_code already stored at trip creation
        """
        from app.services.pricing_service import PricingService
        import json
        
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

        # Calculate final fare using pricing service
        try:
            fare_breakdown = PricingService.calculate_fare(
                db=db,
                city_id=trip.city_id,
                vehicle_category=trip.fare_snapshot.get("vehicle_category") if trip.fare_snapshot else "STANDARD",
                pickup_lat=float(trip.pickup_lat),
                pickup_lng=float(trip.pickup_lng),
                drop_lat=float(trip.drop_lat),
                drop_lng=float(trip.drop_lng)
            )
            
            # Store final fare
            trip.fare_amount = fare_breakdown.fare_applied
            
            # Update fare_snapshot with actual values
            if trip.fare_snapshot:
                snapshot = dict(trip.fare_snapshot)
                snapshot.update({
                    "actual_distance_km": fare_breakdown.distance_km,
                    "actual_minutes": fare_breakdown.estimated_minutes,
                    "final_fare": fare_breakdown.fare_applied,
                    "completed_at": datetime.now(timezone.utc).isoformat()
                })
                trip.fare_snapshot = snapshot
        except Exception as e:
            # If fare calculation fails, , use fare_amount from trip creation (estimated fare)
            pass

        trip.status = "COMPLETED"
        trip.completed_at = datetime.now(timezone.utc)

        # Auto-create cash payment record
        from app.services.payment_service import PaymentService
        try:
            PaymentService.auto_create_cash_payment(db, trip)
        except Exception as e:
            # Log but don't fail trip completion if payment creation fails
            print(f"Warning: Could not auto-create payment record: {e}")

        db.commit()
        db.refresh(trip)
        
        return {
            "message": "Trip completed",
            "trip_id": trip.trip_id,
            "final_fare": float(trip.fare_amount),
            "currency": trip.currency
        }
    
    
