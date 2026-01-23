from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta

from app.core.database import SessionLocal
from app.models.identity import AppUser, UserAuth, UserSession
from app.models.tenant import TenantAdmin
from app.schemas.admin import AdminLoginRequest, AdminLoginResponse, AdminMeResponse
from app.utils.security import verify_password, generate_session_id

router = APIRouter(prefix="/auth", tags=["Admin Auth"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_admin_session(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get current admin session from cookie"""
    session_id = request.cookies.get("admin_session_id")
    
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    session = db.query(UserSession).filter(
        UserSession.session_id == session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    if session.logout_at:
        raise HTTPException(status_code=401, detail="Session logged out")
    
    if session.login_at + timedelta(days=7) < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Session expired")
    
    user = db.query(AppUser).filter(
        AppUser.user_id == session.user_id
    ).first()
    
    if not user or user.status != "ACTIVE":
        raise HTTPException(status_code=401, detail="User inactive")
    
    # Check if user is an admin
    if user.role not in ("PLATFORM_ADMIN", "TENANT_ADMIN"):
        raise HTTPException(status_code=403, detail="Not an admin")
    
    return {"user": user, "session": session}


@router.post("/login", response_model=AdminLoginResponse)
def admin_login(
    data: AdminLoginRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    """Admin login endpoint - works for both Platform Admin and Tenant Admin"""
    
    # Find user by email
    user = db.query(AppUser).filter(AppUser.email == data.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Check if user is an admin
    if user.role not in ("PLATFORM_ADMIN", "TENANT_ADMIN"):
        raise HTTPException(status_code=403, detail="Not an admin account")
    
    # Check account status
    if user.status in ("SUSPENDED", "CLOSED"):
        raise HTTPException(status_code=403, detail="Account disabled")
    
    # Verify password
    auth = db.query(UserAuth).filter(UserAuth.user_id == user.user_id).first()
    if not auth or not verify_password(data.password, auth.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create session
    session_id = generate_session_id()
    session = UserSession(
        session_id=session_id,
        user_id=user.user_id,
        login_at=datetime.now(timezone.utc)
    )
    db.add(session)
    db.commit()
    
    # Set session cookie
    response.set_cookie(
        key="admin_session_id",
        value=session_id,
        httponly=True,
        max_age=7 * 24 * 60 * 60,  # 7 days
        samesite="lax"
    )
    
    # Determine admin type
    admin_type = "PLATFORM" if user.role == "PLATFORM_ADMIN" else "TENANT"
    
    # Get tenant_id if tenant admin
    tenant_id = None
    if admin_type == "TENANT":
        tenant_admin = db.query(TenantAdmin).filter(
            TenantAdmin.user_id == user.user_id
        ).first()
        if tenant_admin:
            tenant_id = tenant_admin.tenant_id
    
    return AdminLoginResponse(
        message="Login successful",
        admin_type=admin_type,
        full_name=user.full_name,
        email=user.email,
        tenant_id=tenant_id
    )


@router.get("/me", response_model=AdminMeResponse)
def get_current_admin(
    admin_data: dict = Depends(get_admin_session),
    db: Session = Depends(get_db)
):
    """Get current admin info - used by frontend to determine admin type"""
    user = admin_data["user"]
    
    # Determine admin type
    admin_type = "PLATFORM" if user.role == "PLATFORM_ADMIN" else "TENANT"
    
    # Get tenant_id if tenant admin
    tenant_id = None
    if admin_type == "TENANT":
        tenant_admin = db.query(TenantAdmin).filter(
            TenantAdmin.user_id == user.user_id
        ).first()
        if tenant_admin:
            tenant_id = tenant_admin.tenant_id
    
    return AdminMeResponse(
        user_id=user.user_id,
        full_name=user.full_name,
        email=user.email,
        admin_type=admin_type,
        tenant_id=tenant_id
    )


@router.post("/logout")
def admin_logout(
    response: Response,
    admin_data: dict = Depends(get_admin_session),
    db: Session = Depends(get_db)
):
    """Logout admin and clear session"""
    session = admin_data["session"]
    
    # Mark session as logged out
    session.logout_at = datetime.now(timezone.utc)
    db.commit()
    
    # Clear cookie
    response.delete_cookie(key="admin_session_id")
    
    return {"message": "Logged out successfully"}
