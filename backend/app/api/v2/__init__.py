"""
Phase-2 API v2 router initialization
"""

from fastapi import APIRouter
from app.api.v2 import auth, test, me, driver, profile, fleet, vehicles, platform_admin

router = APIRouter()

# Include Phase-2 routes
router.include_router(auth.router)
router.include_router(test.router)
router.include_router(me.router)
router.include_router(driver.router)
router.include_router(profile.router)
router.include_router(fleet.router)
router.include_router(vehicles.router)
router.include_router(platform_admin.router)
