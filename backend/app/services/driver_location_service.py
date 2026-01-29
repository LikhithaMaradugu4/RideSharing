"""
Driver Location Service - Manage driver locations via Redis GEO and Postgres.

Redis GEO Commands Used:
- GEOADD: Add/update driver location
- GEORADIUS: Find drivers within radius
- GEOPOS: Get driver position
- ZREM: Remove driver from geo set
"""

from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timezone
import redis

from app.models.operations import DriverShift, DriverLocation, DriverLocationHistory
from app.core.redis.client import redis_client
from app.core.redis.keys import DRIVERS_GEO_KEY


class DriverLocationService:

    @staticmethod
    def update_location(
        db: Session,
        driver_id: int,
        latitude: float,
        longitude: float
    ) -> dict:
        """
        Update driver location in Redis GEO and Postgres.
        
        NOTE: Authorization (driver approval) should be checked at route level
        using require_approved_driver dependency. This service assumes the
        driver is already validated.
        
        Redis: GEOADD drivers:geo longitude latitude driver_id
        Postgres: UPDATE driver_location, INSERT driver_location_history
        
        Args:
            db: Database session
            driver_id: Validated driver's user ID
            latitude: Latitude coordinate
            longitude: Longitude coordinate
        
        Returns primitive dict (never ORM objects).
        """
        active_shift = (
            db.query(DriverShift)
            .filter(
                DriverShift.driver_id == driver_id,
                DriverShift.ended_at.is_(None)
            )
            .first()
        )

        if not active_shift:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Driver does not have an active shift"
            )

        now = datetime.now(timezone.utc)

        # 1. Update Redis GEO
        try:
            redis_client.geoadd(
                DRIVERS_GEO_KEY,
                (longitude, latitude, str(driver_id))
            )
        except redis.RedisError as e:
            # Log but don't fail - Postgres is primary source of truth
            print(f"Redis GEOADD error for driver {driver_id}: {e}")

        # 2. Upsert latest location in Postgres
        location = (
            db.query(DriverLocation)
            .filter(DriverLocation.driver_id == driver_id)
            .first()
        )

        if location:
            location.latitude = latitude
            location.longitude = longitude
            location.last_updated = now
        else:
            location = DriverLocation(
                driver_id=driver_id,
                latitude=latitude,
                longitude=longitude,
                last_updated=now
            )
            db.add(location)

        # 3. Insert history
        history = DriverLocationHistory(
            driver_id=driver_id,
            latitude=latitude,
            longitude=longitude,
            recorded_at=now
        )

        db.add(history)
        db.commit()

        return {
            "success": True,
            "driver_id": driver_id,
            "latitude": float(latitude),
            "longitude": float(longitude),
            "updated_at": now.isoformat()
        }

    @staticmethod
    def find_nearby_drivers(
        longitude: float,
        latitude: float,
        radius_km: float,
        count: Optional[int] = None
    ) -> List[Tuple[int, float]]:
        """
        Find drivers within radius using Redis GEORADIUS.
        
        Command: GEORADIUS drivers:geo longitude latitude radius km WITHDIST ASC
        
        Args:
            longitude: Center longitude
            latitude: Center latitude
            radius_km: Search radius in kilometers
            count: Optional limit on results
        
        Returns:
            List of (driver_id, distance_km) tuples, sorted by distance (nearest first)
        """
        try:
            # GEORADIUS returns: [(member, distance), ...]
            results = redis_client.georadius(
                DRIVERS_GEO_KEY,
                longitude,
                latitude,
                radius_km,
                unit='km',
                withdist=True,
                sort='ASC',
                count=count
            )
            
            # Convert to (driver_id, distance) tuples
            return [
                (int(member), float(distance))
                for member, distance in results
            ]
        
        except redis.RedisError as e:
            print(f"Redis GEORADIUS error: {e}")
            return []

    @staticmethod
    def get_driver_location(driver_id: int) -> Optional[Tuple[float, float]]:
        """
        Get driver's current location from Redis.
        
        Command: GEOPOS drivers:geo driver_id
        
        Args:
            driver_id: Driver's user ID
        
        Returns:
            (longitude, latitude) tuple or None if not found
        """
        try:
            positions = redis_client.geopos(DRIVERS_GEO_KEY, str(driver_id))
            if positions and positions[0]:
                return (float(positions[0][0]), float(positions[0][1]))
            return None
        except redis.RedisError:
            return None

    @staticmethod
    def remove_driver_from_geo(driver_id: int) -> bool:
        """
        Remove driver from the geo set (e.g., when going offline).
        
        Command: ZREM drivers:geo driver_id
        
        Args:
            driver_id: Driver's user ID
        
        Returns:
            True if removed, False otherwise
        """
        try:
            result = redis_client.zrem(DRIVERS_GEO_KEY, str(driver_id))
            return result > 0
        except redis.RedisError:
            return False



