from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.trips import RideRequest
from app.models.core import Tenant
from app.models.pricing import FareConfig   

class PricingService:

    @staticmethod
    def estimate_prices(db: Session, ride_request_id: int):
        # 1️⃣ Fetch ride request
        ride_request = (
            db.query(RideRequest)
            .filter(RideRequest.request_id == ride_request_id)
            .first()
        )

        if not ride_request:
            raise HTTPException(status_code=404, detail="Ride request not found")

        # 2️⃣ Get active tenants
        tenants = (
            db.query(Tenant)
            .filter(Tenant.status == "ACTIVE")
            .all()
        )

        results = []

        # 3️⃣ Loop tenants → fare configs
        for tenant in tenants:
            fare_configs = (
                db.query(FareConfig)
                .filter(
                    FareConfig.tenant_id == tenant.tenant_id,
                    FareConfig.city_id == ride_request.city_id
                )
                .all()
            )

            for fare in fare_configs:
                # 🔹 Simple MVP pricing logic
                estimated_fare = (
                    float(fare.base_fare)
                    + float(fare.per_km) * 5
                    + float(fare.per_minute) * 10
                )

                results.append({
                    "tenant_id": tenant.tenant_id,
                    "tenant_name": tenant.name,
                    "vehicle_category": fare.vehicle_category,
                    "estimated_fare": round(estimated_fare, 2)
                })

        if not results:
            raise HTTPException(
                status_code=404,
                detail="No pricing available for this request"
            )

        return results
