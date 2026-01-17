from fastapi import APIRouter, Depends
from app.api.deps.roles import require_roles

router = APIRouter(prefix="/test", tags=["Test"])

@router.get("/admin-only")
def admin_only(user = Depends(require_roles("PLATFORM_ADMIN"))):
    return {"message": f"Hello {user.full_name}, you are an admin"}
