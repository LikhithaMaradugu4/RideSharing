"""
JWT utilities for Phase-2 authentication
Handles access token and refresh token generation/verification
"""

import jwt
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional
from app.core.config import settings


# Token expiry constants (LOCKED)
ACCESS_TOKEN_EXPIRY_MINUTES = 15
REFRESH_TOKEN_EXPIRY_DAYS = 7


def generate_access_token(user_id: int, phone_number: str, role: str) -> Dict[str, str]:
    """
    Generate access token (short-lived, 15 minutes)
    
    Args:
        user_id: Internal user identifier
        phone_number: Login identity (phone)
        role: rider / driver / admin
        
    Returns:
        dict: {"token": jwt_string, "jti": unique_token_id}
    """
    jti = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    expiry = now + timedelta(minutes=ACCESS_TOKEN_EXPIRY_MINUTES)
    
    payload = {
        "user_id": user_id,
        "phone_number": phone_number,
        "role": role,
        "jti": jti,
        "iat": now,
        "exp": expiry
    }
    
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    return {
        "token": token,
        "jti": jti,
        "expires_at": expiry.isoformat()
    }


def generate_refresh_token(user_id: int, phone_number: str, role: str) -> Dict[str, str]:
    """
    Generate refresh token (long-lived, 7 days)
    
    Args:
        user_id: Internal user identifier
        phone_number: Login identity (phone)
        role: rider / driver / admin
        
    Returns:
        dict: {"token": jwt_string, "jti": unique_token_id}
    """
    jti = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    expiry = now + timedelta(days=REFRESH_TOKEN_EXPIRY_DAYS)
    
    payload = {
        "user_id": user_id,
        "phone_number": phone_number,
        "role": role,
        "jti": jti,
        "iat": now,
        "exp": expiry,
        "token_type": "refresh"  # Distinguish refresh from access
    }
    
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    return {
        "token": token,
        "jti": jti,
        "expires_at": expiry.isoformat()
    }


def decode_token(token: str) -> Optional[Dict]:
    """
    Decode and verify JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        dict: Decoded payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token expired
    except jwt.InvalidTokenError:
        return None  # Invalid token


def get_token_expiry_seconds(token: str) -> Optional[int]:
    """
    Get remaining seconds until token expires
    
    Args:
        token: JWT token string
        
    Returns:
        int: Remaining seconds, None if invalid
    """
    payload = decode_token(token)
    if not payload:
        return None
    
    exp = payload.get("exp")
    if not exp:
        return None
    
    now = datetime.now(timezone.utc).timestamp()
    remaining = int(exp - now)
    
    return remaining if remaining > 0 else 0
