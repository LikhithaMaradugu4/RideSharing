"""
Surge Service - Surge zone CRUD with Redis sync.

Handles creation, update, activation/deactivation, and deletion
of surge zones. Keeps Redis cache in sync after every mutation.
Database is always the source of truth.
"""

import logging
from typing import List, Optional
from datetime import datetime, timezone

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.pricing import SurgeZone
from app.core.redis.services.surge_store import SurgeStore

logger = logging.getLogger(__name__)


class SurgeService:
    """Service for surge zone management."""

    # ------------------------------------------------------------------ #
    #  READ
    # ------------------------------------------------------------------ #

    @staticmethod
    def get_all(db: Session, city_id: Optional[int] = None) -> List[SurgeZone]:
        """List surge zones, optionally filtered by city."""
        query = db.query(SurgeZone)
        if city_id is not None:
            query = query.filter(SurgeZone.city_id == city_id)
        return query.order_by(SurgeZone.surge_zone_id.desc()).all()

    @staticmethod
    def get_by_id(db: Session, surge_zone_id: int) -> SurgeZone:
        """Get a single surge zone or raise 404."""
        zone = db.query(SurgeZone).filter(
            SurgeZone.surge_zone_id == surge_zone_id
        ).first()
        if not zone:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Surge zone {surge_zone_id} not found",
            )
        return zone

    # ------------------------------------------------------------------ #
    #  CREATE
    # ------------------------------------------------------------------ #

    @staticmethod
    def create(
        db: Session,
        city_id: int,
        name: Optional[str],
        boundary_geojson: str,
        multiplier: float,
        starts_at: datetime,
        ends_at: datetime,
        is_active: bool,
        created_by: int,
    ) -> SurgeZone:
        """Create a new surge zone and sync Redis."""
        if multiplier < 1.0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Surge multiplier must be >= 1.0",
            )
        if ends_at <= starts_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ends_at must be after starts_at",
            )

        zone = SurgeZone(
            city_id=city_id,
            name=name,
            boundary_geojson=boundary_geojson,
            multiplier=multiplier,
            starts_at=starts_at,
            ends_at=ends_at,
            is_active=is_active,
            created_by=created_by,
        )
        db.add(zone)
        db.commit()
        db.refresh(zone)

        # Sync Redis
        SurgeStore.refresh_city_surge_from_db(db, city_id)

        logger.info(
            f"Surge zone {zone.surge_zone_id} created for city {city_id} "
            f"(multiplier={multiplier}, active={is_active})"
        )
        return zone

    # ------------------------------------------------------------------ #
    #  UPDATE
    # ------------------------------------------------------------------ #

    @staticmethod
    def update(
        db: Session,
        surge_zone_id: int,
        update_data: dict,
        updated_by: int,
    ) -> SurgeZone:
        """Update a surge zone and sync Redis."""
        zone = SurgeService.get_by_id(db, surge_zone_id)

        # Validate multiplier if provided
        if "multiplier" in update_data and update_data["multiplier"] is not None:
            if update_data["multiplier"] < 1.0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Surge multiplier must be >= 1.0",
                )

        # Validate time window if both provided
        new_starts = update_data.get("starts_at") or zone.starts_at
        new_ends = update_data.get("ends_at") or zone.ends_at
        if new_ends <= new_starts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ends_at must be after starts_at",
            )

        # Apply updates
        for field, value in update_data.items():
            if value is not None:
                setattr(zone, field, value)

        zone.updated_by = updated_by
        db.commit()
        db.refresh(zone)

        # Sync Redis for the city
        SurgeStore.refresh_city_surge_from_db(db, zone.city_id)

        logger.info(f"Surge zone {surge_zone_id} updated")
        return zone

    # ------------------------------------------------------------------ #
    #  ACTIVATE / DEACTIVATE
    # ------------------------------------------------------------------ #

    @staticmethod
    def set_active(
        db: Session,
        surge_zone_id: int,
        is_active: bool,
        updated_by: int,
    ) -> SurgeZone:
        """Activate or deactivate a surge zone and sync Redis."""
        zone = SurgeService.get_by_id(db, surge_zone_id)
        zone.is_active = is_active
        zone.updated_by = updated_by
        db.commit()
        db.refresh(zone)

        # Sync Redis
        SurgeStore.refresh_city_surge_from_db(db, zone.city_id)

        action = "activated" if is_active else "deactivated"
        logger.info(f"Surge zone {surge_zone_id} {action}")
        return zone

    # ------------------------------------------------------------------ #
    #  DELETE
    # ------------------------------------------------------------------ #

    @staticmethod
    def delete(db: Session, surge_zone_id: int) -> dict:
        """Delete a surge zone and sync Redis."""
        zone = SurgeService.get_by_id(db, surge_zone_id)
        city_id = zone.city_id

        db.delete(zone)
        db.commit()

        # Sync Redis
        SurgeStore.refresh_city_surge_from_db(db, city_id)

        logger.info(f"Surge zone {surge_zone_id} deleted")
        return {"detail": f"Surge zone {surge_zone_id} deleted"}
