from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone,timedelta

from app.core.database import SessionLocal
from app.models import UserSession, AppUser


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    x_session_id: str = Header(...),
    db: Session = Depends(get_db)
):
    session = db.query(UserSession).filter(
        UserSession.session_id == x_session_id
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

    return user
