"""
Pricing Service - Fare calculation with Haversine distance and surge.

Pricing is based on:
- Haversine distance between pickup and drop
- fare_config (city + vehicle_category)
- surge multiplier (pickup location only)

Price is LOCKED at trip request time.
"""

from typing import Optional
from dataclasses import dataclass
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException
from datetime import datetime, timezone

from app.models.pricing import FareConfig
from app.utils.haversine import haversine
from app.services.geo_service import GeoService


@dataclass
class FareBreakdown:
    """Detailed fare breakdown."""
    distance_km: float
    estimated_minutes: float
    base_fare: float
    distance_fare: float
    time_fare: float
    booking_fee: float
    subtotal: float
    surge_multiplier: float
    surge_zone_id: Optional[int]
    final_fare: float
    minimum_fare: float
    fare_applied: float  # max(final_fare, minimum_fare)
    fare_config: FareConfig  # Include fare config for snapshot


class PricingService:
    """Service for fare calculation."""

    # Estimated average speed for time estimation (km/h)
    AVERAGE_SPEED_KMH = 25
    
    @staticmethod
    def get_fare_config(
        db: Session,
        city_id: int,
        vehicle_category: str,
        effective_time: Optional[datetime] = None
    ) -> Optional[FareConfig]:
        """
        Get fare configuration for city and vehicle category at a specific time.
        
        Args:
            db: Database session
            city_id: City ID
            vehicle_category: Vehicle category code (BIKE/AUTO/CAB/XL)
            effective_time: Time to check (defaults to now)
        
        Returns:
            FareConfig if found, None otherwise
        """
        if effective_time is None:
            effective_time = datetime.now(timezone.utc)
        
        return (
            db.query(FareConfig)
            .filter(
                FareConfig.city_id == city_id,
                FareConfig.vehicle_category == vehicle_category,
                FareConfig.effective_from <= effective_time,
                or_(
                    FareConfig.effective_to.is_(None),
                    FareConfig.effective_to > effective_time
                )
            )
            .order_by(FareConfig.effective_from.desc())
            .first()
        )
    
    @staticmethod
    def calculate_fare(
        db: Session,
        city_id: int,
        vehicle_category: str,
        pickup_lat: float,
        pickup_lng: float,
        drop_lat: float,
        drop_lng: float
    ) -> FareBreakdown:
        """
        Calculate fare for a trip.
        
        Pricing formula:
        1. distance_km = haversine(pickup, drop)
        2. estimated_minutes = distance_km / average_speed * 60
        3. base_total = base_fare + (per_km * distance) + (per_minute * minutes)
        4. surge_fare = base_total * surge_multiplier
        5. final = max(surge_fare, minimum_fare)
        
        Args:
            db: Database session
            city_id: City ID
            vehicle_category: Vehicle category code
            pickup_lat, pickup_lng: Pickup coordinates
            drop_lat, drop_lng: Drop coordinates
        
        Returns:
            FareBreakdown with all pricing details
        
        Raises:
            HTTPException if fare config not found
        """
        # Get fare config
        fare_config =PricingService.get_fare_config(db, city_id, vehicle_category)
        if not fare_config:
            raise HTTPException(
                status_code=400,
                detail=f"No fare configuration for vehicle category '{vehicle_category}' in this city"
            )
        
        # Calculate distance
        distance_km = haversine(pickup_lat, pickup_lng, drop_lat, drop_lng)
        
        # Estimate time (minutes)
        estimated_minutes = (distance_km / PricingService.AVERAGE_SPEED_KMH) * 60
        
        # Get surge info (based on pickup location only)
        surge_multiplier, surge_zone_id = GeoService.get_surge_info(
            db, pickup_lat, pickup_lng, city_id
        )
        
        # Calculate fare components
        base_fare = float(fare_config.base_fare)
        distance_fare = float(fare_config.per_km_rate) * distance_km
        time_fare = float(fare_config.per_min_rate) * estimated_minutes
        booking_fee = float(fare_config.booking_fee) if fare_config.booking_fee else 0.0
        minimum_fare = float(fare_config.minimum_fare) if fare_config.minimum_fare else 0.0
        
        # Subtotal before surge
        subtotal = base_fare + distance_fare + time_fare + booking_fee
        
        # Apply surge (only if allowed for this fare config)
        if fare_config.surge_allowed:
            final_fare = subtotal * surge_multiplier
        else:
            final_fare = subtotal
            surge_multiplier = 1.0
            surge_zone_id = None
        
        # Apply minimum fare
        fare_applied = max(final_fare, minimum_fare)
        
        return FareBreakdown(
            distance_km=round(distance_km, 2),
            estimated_minutes=round(estimated_minutes, 2),
            base_fare=round(base_fare, 2),
            distance_fare=round(distance_fare, 2),
            time_fare=round(time_fare, 2),
            booking_fee=round(booking_fee, 2),
            subtotal=round(subtotal, 2),
            surge_multiplier=surge_multiplier,
            surge_zone_id=surge_zone_id,
            final_fare=round(final_fare, 2),
            minimum_fare=round(minimum_fare, 2),
            fare_applied=round(fare_applied, 2),
            fare_config=fare_config
        )
    
    @staticmethod
    def estimate_fare(
        db: Session,
        pickup_lat: float,
        pickup_lng: float,
        drop_lat: float,
        drop_lng: float,
        vehicle_category: str
    ) -> dict:
        """
        Estimate fare for a potential trip (before trip creation).
        
        Validates locations and returns fare estimate.
        
        Args:
            db: Database session
            pickup_lat, pickup_lng: Pickup coordinates
            drop_lat, drop_lng: Drop coordinates
            vehicle_category: Vehicle category code
        
        Returns:
            Dict with fare details
        
        Raises:
            HTTPException if location invalid or fare config not found
        """
        # Validate location
        city, error = GeoService.validate_location(
            db, pickup_lat, pickup_lng, drop_lat, drop_lng
        )
        
        if error:
            raise HTTPException(status_code=400, detail=error)
        
        # Calculate fare
        breakdown = PricingService.calculate_fare(
            db=db,
            city_id=city.city_id,
            vehicle_category=vehicle_category,
            pickup_lat=pickup_lat,
            pickup_lng=pickup_lng,
            drop_lat=drop_lat,
            drop_lng=drop_lng
        )
        
        return {
            "city_id": city.city_id,
            "city_name": city.name,
            "distance_km": breakdown.distance_km,
            "base_fare": breakdown.base_fare,
            "surge_multiplier": breakdown.surge_multiplier,
            "surge_zone_id": breakdown.surge_zone_id,
            "final_fare": breakdown.fare_applied
        }
