289+4-7
"""
Admin API router initialization
Session-based auth for admins (Platform Admin & Tenant Admin)
"""

from fastapi import APIRouter
from app.api.admin import auth, tenants, documents, drivers, fleets, vehicles, operating_regions, surge_zones

router = APIRouter()

# Include admin routes
router.include_router(auth.router)  # Admin authentication
router.include_router(tenants.router)  # Platform admin - tenant management
router.include_router(documents.router)  # Platform admin - tenant documents
router.include_router(drivers.router)  # Tenant admin - driver management
router.include_router(fleets.router)  # Tenant admin - fleet management
router.include_router(vehicles.router)  # Tenant admin - vehicle management
router.include_router(operating_regions.router)  # Tenant admin - operating regions
router.include_router(surge_zones.router)  # Platform admin - surge zone management
