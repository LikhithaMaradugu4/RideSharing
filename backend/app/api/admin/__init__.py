"""
Admin API router initialization
Session-based auth for tenant admins
"""

from fastapi import APIRouter
from app.api.admin import drivers, fleets, vehicles

router = APIRouter()

# Include admin routes
router.include_router(drivers.router)
router.include_router(fleets.router)
router.include_router(vehicles.router)
