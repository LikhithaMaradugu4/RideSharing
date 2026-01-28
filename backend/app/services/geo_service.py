"""
Geo Service - City and surge zone detection using point-in-polygon.

Uses application-layer polygon checks (no PostGIS).
GeoJSON boundaries are stored as TEXT in the database.
"""

import json
from datetime import datetime, timezone
from typing import Optional, Tuple, List
from sqlalchemy.orm import Session

from app.models.core import City
from app.models.pricing import SurgeZone


def point_in_polygon(lat: float, lng: float, polygon_coords: List[List[float]]) -> bool:
    """
    Ray-casting algorithm for point-in-polygon check.
    
    Args:
        lat: Latitude of point
        lng: Longitude of point
        polygon_coords: List of [lng, lat] coordinates (GeoJSON format)
    
    Returns:
        True if point is inside polygon
    """
    n = len(polygon_coords)
    inside = False
    
    x, y = lng, lat
    
    j = n - 1
    for i in range(n):
        xi, yi = polygon_coords[i][0], polygon_coords[i][1]
        xj, yj = polygon_coords[j][0], polygon_coords[j][1]
        
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    
    return inside


def parse_geojson_polygon(geojson_text: str) -> Optional[List[List[float]]]:
    """
    Parse GeoJSON text and extract polygon coordinates.
    
    Supports:
    - Polygon type: {"type": "Polygon", "coordinates": [[[lng, lat], ...]]}
    - Simple coordinates: [[[lng, lat], ...]]
    
    Returns:
        List of [lng, lat] coordinates for the outer ring, or None if invalid
    """
    if not geojson_text or geojson_text == '{}':
        return None
    
    try:
        data = json.loads(geojson_text)
        
        # Handle GeoJSON Polygon type
        if isinstance(data, dict):
            if data.get("type") == "Polygon":
                coords = data.get("coordinates", [])
                if coords and len(coords) > 0:
                    return coords[0]  # Outer ring
            elif "coordinates" in data:
                coords = data["coordinates"]
                if coords and len(coords) > 0:
                    return coords[0]
        
        # Handle raw coordinates array
        elif isinstance(data, list) and len(data) > 0:
            if isinstance(data[0], list) and len(data[0]) > 0:
                if isinstance(data[0][0], list):
                    return data[0]  # [[[lng, lat], ...]]
                else:
                    return data  # [[lng, lat], ...]
        
        return None
    except (json.JSONDecodeError, TypeError, IndexError):
        return None


class GeoService:
    """Service for geographic operations."""
    
    @staticmethod
    def find_city_for_location(
        db: Session,
        lat: float,
        lng: float
    ) -> Optional[City]:
        """
        Find the city that contains the given location.
        
        Args:
            db: Database session
            lat: Latitude
            lng: Longitude
        
        Returns:
            City object if found, None otherwise
        """
        # Get all active cities
        cities = db.query(City).filter(City.is_active == True).all()
        
        for city in cities:
            polygon = parse_geojson_polygon(city.boundary_geojson)
            if polygon and point_in_polygon(lat, lng, polygon):
                return city
        
        return None
    
    @staticmethod
    def validate_location(
        db: Session,
        pickup_lat: float,
        pickup_lng: float,
        drop_lat: float,
        drop_lng: float
    ) -> Tuple[Optional[City], Optional[str]]:
        """
        Validate that pickup and drop locations are in a supported city.
        
        Args:
            db: Database session
            pickup_lat, pickup_lng: Pickup coordinates
            drop_lat, drop_lng: Drop coordinates
        
        Returns:
            Tuple of (City, None) if valid, or (None, error_message) if invalid
        """
        # Check pickup location
        pickup_city = GeoService.find_city_for_location(db, pickup_lat, pickup_lng)
        if not pickup_city:
            return None, "Pickup location is not within a supported city"
        
        # Check drop location
        drop_city = GeoService.find_city_for_location(db, drop_lat, drop_lng)
        if not drop_city:
            return None, "Drop location is not within a supported city"
        
        # Both must be in the same city
        if pickup_city.city_id != drop_city.city_id:
            return None, "Pickup and drop locations must be in the same city"
        
        return pickup_city, None
    
    @staticmethod
    def find_active_surge_zone(
        db: Session,
        lat: float,
        lng: float,
        city_id: int
    ) -> Optional[SurgeZone]:
        """
        Find an active surge zone at the given location.
        
        Surge zones are time-bounded and location-bounded.
        
        Args:
            db: Database session
            lat: Latitude (pickup location)
            lng: Longitude (pickup location)
            city_id: City ID to filter surge zones
        
        Returns:
            SurgeZone if point is in an active surge zone, None otherwise
        """
        now = datetime.now(timezone.utc)
        
        # Get active surge zones for the city that are currently valid
        surge_zones = (
            db.query(SurgeZone)
            .filter(
                SurgeZone.city_id == city_id,
                SurgeZone.is_active == True,
                SurgeZone.starts_at <= now,
                SurgeZone.ends_at >= now
            )
            .all()
        )
        
        for zone in surge_zones:
            polygon = parse_geojson_polygon(zone.boundary_geojson)
            if polygon and point_in_polygon(lat, lng, polygon):
                return zone
        
        return None
    
    @staticmethod
    def get_surge_info(
        db: Session,
        lat: float,
        lng: float,
        city_id: int
    ) -> Tuple[float, Optional[int]]:
        """
        Get surge multiplier and zone ID for a location.
        
        Args:
            db: Database session
            lat: Latitude
            lng: Longitude
            city_id: City ID
        
        Returns:
            Tuple of (multiplier, surge_zone_id). 
            Default multiplier is 1.0 if no surge.
        """
        surge_zone = GeoService.find_active_surge_zone(db, lat, lng, city_id)
        
        if surge_zone:
            return float(surge_zone.multiplier), surge_zone.surge_zone_id
        
        return 1.0, None
