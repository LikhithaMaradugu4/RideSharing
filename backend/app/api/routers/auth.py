from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime,timezone

from app.core.database import SessionLocal
from app.models import AppUser, UserAuth, UserSession
from app.schemas.auth import LoginRequest, LoginResponse, UserInfo
from app.utils.security import verify_password, generate_session_id

router = APIRouter(prefix="/auth", tags=["Auth"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(AppUser).filter(AppUser.email == data.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if user.status in ("SUSPENDED", "CLOSED"):
        raise HTTPException(status_code=403, detail="Account disabled")


    auth = db.query(UserAuth).filter(UserAuth.user_id == user.user_id).first()
    if not auth or not verify_password(data.password, auth.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    session_id = generate_session_id()

    session = UserSession(
        session_id=session_id,
        user_id=user.user_id,
        login_at=datetime.now(timezone.utc)
    )

    db.add(session)
    db.commit()

    return LoginResponse(
        session_id=session_id,
        user=UserInfo(
            user_id=user.user_id,
            full_name=user.full_name,
            role=user.role,
            status=user.status
        )
    )
