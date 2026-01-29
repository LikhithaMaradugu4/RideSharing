"""
Phase-2 JWT Authentication Router
OTP-based login with access + refresh tokens
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import random
from typing import Optional

from app.core.database import SessionLocal
from app.models import AppUser, Country
from app.schemas.jwt_auth import (
    SendOTPRequest,
    SendOTPResponse,
    VerifyOTPRequest,
    JWTTokenResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    LogoutResponse
)
from app.core.redis.services.otp_store import OTPStore
from app.core.redis.services.jwt_store import JWTStore
from app.utils.jwt_utils import (
    generate_access_token,
    generate_refresh_token,
    decode_token,
    get_token_expiry_seconds
)
from app.api.deps.jwt_auth import get_current_user


router = APIRouter(prefix="/auth", tags=["Phase-2 Auth"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _resolve_country_code(db: Session, phone: str) -> Optional[str]:
    """Find a country_code whose phone_code prefixes the given phone number."""
    digits = phone.lstrip("+")
    countries = db.query(Country).all()
    matches = [
        country for country in countries 
        if digits.startswith(country.phone_code.lstrip("+"))
    ]

    if not matches:
        return None

    # Prefer the longest phone_code match to handle overlapping prefixes
    return max(matches, key=lambda c: len(c.phone_code.lstrip("+"))).country_code


@router.post("/send-otp", response_model=SendOTPResponse)
def send_otp(data: SendOTPRequest, db: Session = Depends(get_db)):
    phone = data.phone_number

    # Check if phone is locked out
    if OTPStore.is_locked_out(phone):
        remaining_time = OTPStore.get_remaining_lockout_time(phone)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many attempts. Try again in {remaining_time} seconds"
        )

    # Ensure app_user exists (first-time numbers get created here)
    user = db.query(AppUser).filter(AppUser.phone == phone).first()
    if not user:
        country_code = _resolve_country_code(db, phone)
        if not country_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to derive country from phone number"
            )

        placeholder_name = f"User {phone[-4:]}" if len(phone) >= 4 else "User"
        user = AppUser(
            full_name=placeholder_name,
            phone=phone,
            country_code=country_code,
            role="RIDER",
            status="ACTIVE"
        )

        db.add(user)
        db.commit()
        db.refresh(user)

    # Generate 6-digit OTP
    otp_code = f"{random.randint(100000, 999999)}"

    # Store in Redis
    OTPStore.store_otp(phone, otp_code)

    # In production: Send via SMS gateway
    print(f"[DEV MODE] OTP for {phone}: {otp_code}")

    return SendOTPResponse(
        message="OTP sent successfully",
        phone_number=phone
    )


@router.post("/verify-otp", response_model=JWTTokenResponse)
def verify_otp(data: VerifyOTPRequest, db: Session = Depends(get_db)):
    phone = data.phone_number
    otp_code = data.otp_code

    # Check lockout
    if OTPStore.is_locked_out(phone):
        remaining_time = OTPStore.get_remaining_lockout_time(phone)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many attempts. Try again in {remaining_time} seconds"
        )

    # Fetch OTP from Redis
    stored_otp = OTPStore.get_otp(phone)
    if not stored_otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP expired or not found. Request a new one"
        )

    # Verify OTP
    if stored_otp != otp_code:
        attempts = OTPStore.increment_attempts(phone)

        if attempts >= OTPStore.MAX_ATTEMPTS:
            OTPStore.set_lockout(phone)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many failed attempts. Account locked for 15 minutes"
            )

        remaining = OTPStore.MAX_ATTEMPTS - attempts
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid OTP. {remaining} attempts remaining"
        )

    # OTP verified successfully - delete it
    OTPStore.delete_otp(phone)

    # Get or create user details
    user = db.query(AppUser).filter(AppUser.phone == phone).first()
    if user and user.status in ("SUSPENDED", "CLOSED"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is not active"
        )

    if not user:
        country_code = _resolve_country_code(db, phone)
        if not country_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to derive country from phone number"
            )

        placeholder_name = f"User {phone[-4:]}" if len(phone) >= 4 else "User"
        user = AppUser(
            full_name=placeholder_name,
            phone=phone,
            country_code=country_code,
            role="USER",
            status="ACTIVE"
        )

        db.add(user)
        db.commit()
        db.refresh(user)

    # Generate access token
    access_token_data = generate_access_token(
        user_id=user.user_id,
        phone_number=user.phone,
        role=user.role
    )
    
    # Generate refresh token
    refresh_token_data = generate_refresh_token(
        user_id=user.user_id,
        phone_number=user.phone,
        role=user.role
    )
    
    # Store refresh token in Redis (7 days TTL)
    JWTStore.store_refresh_token(
        jti=refresh_token_data["jti"],
        user_id=user.user_id,
        phone_number=user.phone,
        role=user.role,
        ttl=7 * 24 * 60 * 60  # 7 days
    )
    
    return JWTTokenResponse(
        access_token=access_token_data["token"],
        refresh_token=refresh_token_data["token"],
        expires_in=60 * 60,  # 60 minutes in seconds
        user={
            "user_id": user.user_id,
            "phone_number": user.phone,
            "full_name": user.full_name,
            "role": user.role
        }
    )


@router.post("/refresh", response_model=RefreshTokenResponse)
def refresh_access_token(data: RefreshTokenRequest):
    
    refresh_token = data.refresh_token
    
    # Decode refresh token
    payload = decode_token(refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    # Verify it's a refresh token
    if payload.get("token_type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    # Check if refresh token exists in Redis
    jti = payload.get("jti")
    refresh_data = JWTStore.get_refresh_token(jti)
    if not refresh_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token revoked or expired. Please login again"
        )
    
    # Generate new access token
    access_token_data = generate_access_token(
        user_id=payload["user_id"],
        phone_number=payload["phone_number"],
        role=payload["role"]
    )
    
    return RefreshTokenResponse(
        access_token=access_token_data["token"],
        expires_in=15 * 60  # 15 minutes
    )


@router.post("/logout", response_model=LogoutResponse)
def logout(current_user: dict = Depends(get_current_user)):
  
    jti = current_user["jti"]
    
    # Get remaining token lifetime for blacklist TTL
    # We don't have the token string here, so use max TTL (15 minutes)
    ttl = 15 * 60  # 15 minutes
    
    # Blacklist access token
    JWTStore.blacklist_access_token(jti, ttl)
    
    # Note: We can't delete the refresh token here because we don't have its jti
    # The refresh token will naturally expire after 7 days
    # If user wants to logout from all devices, we'd need a separate endpoint
    
    return LogoutResponse(
        message="Logged out successfully"
    )
@router.get("/get-otp-dev")
def get_otp_dev(phone_number: str):

    otp = OTPStore.get_otp(phone_number)

    if not otp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OTP not found or expired"
        )

    # Get Redis TTL for this OTP
    from app.core.redis.client import redis_client
    from app.core.redis.keys import OTP_KEY, format_key

    otp_key = format_key(OTP_KEY, phone=phone_number)
    remaining_ttl = redis_client.ttl(otp_key)

    return {
        "phone_number": phone_number,
        "otp": otp,
        "expires_in": remaining_ttl,
        "warning": "⚠️ This endpoint is for development only"
    }