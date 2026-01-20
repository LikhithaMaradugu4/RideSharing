

from fastapi import APIRouter, Depends
from app.api.deps.jwt_auth import get_current_user, require_role


router = APIRouter(prefix="/test", tags=["Phase-2 Test"])


@router.get("/protected")
def test_protected(current_user: dict = Depends(get_current_user)):
 
    return {
        "message": "JWT authentication successful",
        "user": current_user
    }


@router.get("/driver-only")
def test_driver_only(current_user: dict = Depends(require_role(["DRIVER"]))):
    return {
        "message": "Driver access granted",
        "user": current_user
    }


@router.get("/admin-only")
def test_admin_only(current_user: dict = Depends(require_role(["TENANT_ADMIN"]))):
    return {
        "message": "Admin access granted",
        "user": current_user
    }
