"""
Phase-2 API v2 router initialization
"""

from fastapi import APIRouter
from app.api.v2 import auth, test

router = APIRouter()

# Include Phase-2 routes
router.include_router(auth.router)
router.include_router(test.router)
