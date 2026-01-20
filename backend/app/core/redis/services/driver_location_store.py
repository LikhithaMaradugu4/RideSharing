"""
Driver Location Redis Store - Handles real-time driver location tracking
"""

import json
from app.core.redis.client import redis_client
from app.core.redis.keys import (
    DRIVER_LOCATION_KEY,
    DRIVERS_IN_CITY_KEY,
    format_key
)


class DriverLocationStore:
    """
    Manages driver location data in Redis
    
    Responsibilities:
    - Store driver location
    - Fetch driver location
    - List drivers in city
    - Remove driver location
    """

    LOCATION_TTL = 300  # 5 minutes - locations expire if not updated

    @staticmethod
    def store_location(driver_id: int, city_id: int, latitude: float, longitude: float, ttl: int = LOCATION_TTL) -> bool:
        """
        Store driver location in Redis
        
        Args:
            driver_id: Driver ID
            city_id: City ID
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            ttl: Time to live in seconds
            
        Returns:
            bool: True if stored successfully
        """
        try:
            location_data = {
                "driver_id": driver_id,
                "city_id": city_id,
                "latitude": latitude,
                "longitude": longitude
            }
            
            # Store driver location
            key = format_key(DRIVER_LOCATION_KEY, driver_id=driver_id)
            redis_client.setex(key, ttl, json.dumps(location_data))
            
            # Add to city drivers set
            city_key = format_key(DRIVERS_IN_CITY_KEY, city_id=city_id)
            redis_client.sadd(city_key, driver_id)
            redis_client.expire(city_key, ttl)
            
            return True
        except Exception as e:
            print(f"Error storing driver location: {e}")
            return False

    @staticmethod
    def get_location(driver_id: int) -> dict | None:
        """
        Fetch driver location from Redis
        
        Args:
            driver_id: Driver ID
            
        Returns:
            dict: Location data if exists, None otherwise
        """
        try:
            key = format_key(DRIVER_LOCATION_KEY, driver_id=driver_id)
            location_json = redis_client.get(key)
            if location_json:
                return json.loads(location_json)
            return None
        except Exception as e:
            print(f"Error fetching driver location: {e}")
            return None

    @staticmethod
    def get_drivers_in_city(city_id: int) -> list[int]:
        """
        Get all driver IDs in a city
        
        Args:
            city_id: City ID
            
        Returns:
            list: List of driver IDs
        """
        try:
            city_key = format_key(DRIVERS_IN_CITY_KEY, city_id=city_id)
            driver_ids = redis_client.smembers(city_key)
            return [int(did) for did in driver_ids]
        except Exception as e:
            print(f"Error fetching drivers in city: {e}")
            return []

    @staticmethod
    def remove_location(driver_id: int) -> bool:
        """
        Remove driver location from Redis (when driver goes offline)
        
        Args:
            driver_id: Driver ID
            
        Returns:
            bool: True if removed
        """
        try:
            key = format_key(DRIVER_LOCATION_KEY, driver_id=driver_id)
            redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Error removing driver location: {e}")
            return False


