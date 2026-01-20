"""
Redis __init__ file - exports main components
"""

from app.core.redis.client import redis_client, get_redis_client, test_redis_connection
from app.core.redis.keys import (
    OTP_KEY,
    OTP_ATTEMPTS_KEY,
    OTP_LOCKOUT_KEY,
    JWT_BLACKLIST_KEY,
    DRIVER_LOCATION_KEY,
    DRIVER_SHIFT_KEY,
    SESSION_KEY,
    AVAILABLE_DRIVERS_KEY,
    format_key
)

__all__ = [
    "redis_client",
    "get_redis_client",
    "test_redis_connection",
    "OTP_KEY",
    "OTP_ATTEMPTS_KEY",
    "OTP_LOCKOUT_KEY",
    "JWT_BLACKLIST_KEY",
    "DRIVER_LOCATION_KEY",
    "DRIVER_SHIFT_KEY",
    "SESSION_KEY",
    "AVAILABLE_DRIVERS_KEY",
    "format_key"
]
