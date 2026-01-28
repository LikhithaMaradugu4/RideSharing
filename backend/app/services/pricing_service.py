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
from fastapi import HTTPException

from app.models.pricing import FareConfig
from app.utils.haversine import haversine
from app.services.geo_service import GeoService


@dataclass
class FareBreakdown:
    """Detailed fare breakdown."""
    distance_km: float
    base_fare: float
    distance_fare: float
    time_fare: float  # Estimated based on distance
    subtotal: float
    surge_multiplier: float
    surge_zone_id: Optional[int]
    final_fare: float
    minimum_fare: float
    fare_applied: float  # max(final_fare, minimum_fare)


class PricingService:
    """Service for fare calculation."""

    # Estimated average speed for time estimation (km/h)
    AVERAGE_SPEED_KMH = 25
    
    @staticmethod
    def get_fare_config(
        db: Session,
        city_id: int,
        vehicle_category: str
    ) -> Optional[FareConfig]:
        """
        Get fare configuration for city and vehicle category.
        
        Args:
            db: Database session
            city_id: City ID
            vehicle_category: Vehicle category code
        
        Returns:
            FareConfig if found, None otherwise
        """
        return (
            db.query(FareConfig)
            .filter(
                FareConfig.city_id == city_id,
                FareConfig.vehicle_category == vehicle_category
            )
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
        fare_config = PricingService.get_fare_config(db, city_id, vehicle_category)
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
        distance_fare = float(fare_config.per_km) * distance_km
        time_fare = float(fare_config.per_minute) * estimated_minutes
        minimum_fare = float(fare_config.minimum_fare)
        
        # Subtotal before surge
        subtotal = base_fare + distance_fare + time_fare
        
        # Apply surge
        final_fare = subtotal * surge_multiplier
        
        # Apply minimum fare
        fare_applied = max(final_fare, minimum_fare)
        
        return FareBreakdown(
            distance_km=round(distance_km, 2),
            base_fare=round(base_fare, 2),
            distance_fare=round(distance_fare, 2),
            time_fare=round(time_fare, 2),
            subtotal=round(subtotal, 2),
            surge_multiplier=surge_multiplier,
            surge_zone_id=surge_zone_id,
            final_fare=round(final_fare, 2),
            minimum_fare=round(minimum_fare, 2),
            fare_applied=round(fare_applied, 2)
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
