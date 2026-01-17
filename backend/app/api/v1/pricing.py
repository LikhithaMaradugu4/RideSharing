from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.schemas.pricing import (
    PricingEstimateRequest,
    PricingEstimateResponse
)
from app.services.pricing_service import PricingService

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter(prefix="/pricing", tags=["Pricing"])

@router.post(
    "/estimate",
    response_model=list[PricingEstimateResponse]
)
def estimate_pricing(
    data: PricingEstimateRequest,
    db: Session = Depends(get_db)
):
    return PricingService.estimate_prices(
        db=db,
        ride_request_id=data.ride_request_id
    )

