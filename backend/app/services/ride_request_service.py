from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timezone

from app.models.trips import RideRequest,Trip
from app.models.identity import AppUser
from app.schemas.ride_request import RideRequestCreate
from app.models.fleet import DriverProfile
from app.models.operations import DriverShift
from app.models.operations import DriverLocation,DriverLocationHistory
from app.models.dispatch import DispatchAttempt
from app.models.core import Tenant
from app.models.pricing import FareConfig
from app.utils.dispatch_attempt import haversine



class RideRequestService:

    @staticmethod
    def create_request(
        db: Session,
        user: AppUser,
        data: RideRequestCreate
    ):
        # 1️⃣ Validate user status
        if user.status != "ACTIVE":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is not active"
            )
        
        # Check if user already has a pending ride request
        existing_request = (
            db.query(RideRequest)
            .filter(
                RideRequest.rider_id == user.user_id,
                RideRequest.status == "REQUESTED"
            )
            .first()
        )
        
        if existing_request:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"You already have a pending ride request (Request ID: {existing_request.request_id})"
            )
        
        # Check if user already has an active trip
        existing_trip = (
            db.query(Trip)
            .filter(
                Trip.rider_id == user.user_id,
                Trip.status.in_(["REQUESTED", "ACCEPTED", "ARRIVED", "IN_PROGRESS"])
            )
            .first()
        )
        
        if existing_trip:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"You already have an active trip (Trip ID: {existing_trip.trip_id})"
            )

        request = RideRequest(
            rider_id=user.user_id,
            city_id=data.city_id,
            pickup_lat=data.pickup_lat,
            pickup_lng=data.pickup_lng,
            drop_lat=data.drop_lat,
            drop_lng=data.drop_lng,
            status="REQUESTED",
            created_on=datetime.now(timezone.utc)
        )

        db.add(request)
        db.commit()
        db.refresh(request)

        return request
    
    @staticmethod
    def confirm_request(
        db: Session,
        user,
        request_id: int,
        data
    ):
        # 0️⃣ Validate user status
        if user.status != "ACTIVE":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is not active"
            )
        
        # 1️⃣ Validate ride request
        ride_request = (
            db.query(RideRequest)
            .filter(
                RideRequest.request_id == request_id,
                RideRequest.status == "REQUESTED"
            )
            .first()
        )

        if not ride_request:
            raise HTTPException(
                status_code=404,
                detail="Ride request not found or already confirmed"
            )

        if ride_request.rider_id != user.user_id:
            raise HTTPException(status_code=403, detail="Not your ride request")

        # 2️⃣ Validate tenant
        tenant = (
            db.query(Tenant)
            .filter(
                Tenant.tenant_id == data.tenant_id,
                Tenant.status == "ACTIVE"
            )
            .first()
        )

        if not tenant:
            raise HTTPException(status_code=400, detail="Invalid tenant")

        # 3️⃣ Validate vehicle category for tenant
        fare = (
            db.query(FareConfig)
            .filter(
                FareConfig.tenant_id == data.tenant_id,
                FareConfig.city_id == ride_request.city_id,
                FareConfig.vehicle_category == data.vehicle_category
            )
            .first()
        )

        if not fare:
            raise HTTPException(
                status_code=400,
                detail="Vehicle category not supported by tenant"
            )

        # 4️⃣ Create trip (tenant-specific)
        trip = Trip(
            tenant_id=data.tenant_id,
            rider_id=user.user_id,
            city_id=ride_request.city_id,
            pickup_lat=ride_request.pickup_lat,
            pickup_lng=ride_request.pickup_lng,
            drop_lat=ride_request.drop_lat,
            drop_lng=ride_request.drop_lng,
            status="REQUESTED",
            requested_at=datetime.now(timezone.utc),
            created_by=user.user_id
        )

        db.add(trip)
        db.flush()  # get trip_id

        # 5️⃣ Mark ride request confirmed
        ride_request.status = "CONFIRMED"

        # 6️⃣ Dispatch (reuse your logic)
        drivers = (
            db.query(DriverProfile, DriverLocation)
            .join(DriverShift, DriverShift.driver_id == DriverProfile.driver_id)
            .join(DriverLocation, DriverLocation.driver_id == DriverProfile.driver_id)
            .filter(
                DriverProfile.tenant_id == data.tenant_id,
                DriverProfile.approval_status == "APPROVED",
                DriverShift.ended_at.is_(None)
            )
            .all()
        )

        if not drivers:
            raise HTTPException(
                status_code=404,
                detail="No drivers available for selected tenant"
            )

        driver_distances = []
        for profile, location in drivers:
            distance = haversine(
                ride_request.pickup_lat,
                ride_request.pickup_lng,
                location.latitude,
                location.longitude
            )
            driver_distances.append((profile, distance))

        driver_distances.sort(key=lambda x: x[1])
        selected_drivers = driver_distances[:3]

        now = datetime.now(timezone.utc)
        for profile, _ in selected_drivers:
            db.add(
                DispatchAttempt(
                    trip_id=trip.trip_id,
                    driver_id=profile.driver_id,
                    sent_at=now,
                    response="SENT",
                    created_by=user.user_id
                )
            )

        db.commit()
        db.refresh(trip)

        return trip

