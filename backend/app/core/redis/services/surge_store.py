"""
Surge Store - Redis caching for active surge zones.

Stores active surge zones per city for fast lookup during fare calculation.
Redis is cache only — database remains the source of truth.

Key format: surge:city:{city_id}
Value: JSON array of active surge zone objects
"""

import json
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from app.core.redis.client import redis_client
from app.core.redis.keys import SURGE_CITY_KEY, format_key

logger = logging.getLogger(__name__)

# Default TTL for surge cache (1 hour) — auto-cleanup safety net
SURGE_CACHE_TTL = 3600


class SurgeStore:
    """Redis store for active surge zones."""

    @staticmethod
    def _serialize_zone(zone) -> Dict[str, Any]:
        """
        Serialize a SurgeZone ORM object to a dict for Redis storage.

        Args:
            zone: SurgeZone model instance

        Returns:
            Dict with zone data
        """
        return {
            "surge_zone_id": zone.surge_zone_id,
            "city_id": zone.city_id,
            "name": zone.name,
            "boundary_geojson": zone.boundary_geojson,
            "multiplier": float(zone.multiplier),
            "starts_at": zone.starts_at.isoformat(),
            "ends_at": zone.ends_at.isoformat(),
        }

    @staticmethod
    def set_city_surge_zones(city_id: int, zones: list) -> bool:
        """
        Store all active surge zones for a city in Redis.
        Replaces any existing data for that city.

        Args:
            city_id: City ID
            zones: List of SurgeZone ORM objects

        Returns:
            True on success, False on failure
        """
        key = format_key(SURGE_CITY_KEY, city_id=city_id)
        try:
            serialized = [SurgeStore._serialize_zone(z) for z in zones]
            redis_client.set(key, json.dumps(serialized), ex=SURGE_CACHE_TTL)
            logger.info(f"Redis: cached {len(serialized)} surge zones for city {city_id}")
            return True
        except Exception as e:
            logger.error(f"Redis: failed to cache surge zones for city {city_id}: {e}")
            return False

    @staticmethod
    def get_city_surge_zones(city_id: int) -> Optional[List[Dict[str, Any]]]:
        """
        Get cached active surge zones for a city.

        Args:
            city_id: City ID

        Returns:
            List of surge zone dicts if cache hit, None if cache miss or error
        """
        key = format_key(SURGE_CITY_KEY, city_id=city_id)
        try:
            data = redis_client.get(key)
            if data is None:
                return None
            return json.loads(data)
        except Exception as e:
            logger.error(f"Redis: failed to read surge zones for city {city_id}: {e}")
            return None

    @staticmethod
    def invalidate_city_surge(city_id: int) -> bool:
        """
        Remove cached surge data for a city.
        Called when surge zones are modified to force a re-cache.

        Args:
            city_id: City ID

        Returns:
            True on success, False on failure
        """
        key = format_key(SURGE_CITY_KEY, city_id=city_id)
        try:
            redis_client.delete(key)
            logger.info(f"Redis: invalidated surge cache for city {city_id}")
            return True
        except Exception as e:
            logger.error(f"Redis: failed to invalidate surge cache for city {city_id}: {e}")
            return False

    @staticmethod
    def refresh_city_surge_from_db(db, city_id: int) -> bool:
        """
        Fetch active surge zones from DB and refresh Redis cache.

        Args:
            db: SQLAlchemy Session
            city_id: City ID

        Returns:
            True on success, False on failure
        """
        from app.models.pricing import SurgeZone

        now = datetime.now(timezone.utc)
        zones = (
            db.query(SurgeZone)
            .filter(
                SurgeZone.city_id == city_id,
                SurgeZone.is_active == True,
                SurgeZone.starts_at <= now,
                SurgeZone.ends_at >= now,
            )
            .all()
        )
        return SurgeStore.set_city_surge_zones(city_id, zones)
