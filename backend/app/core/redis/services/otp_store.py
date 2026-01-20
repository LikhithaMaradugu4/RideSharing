"""
OTP Redis Store - Handles all OTP storage and retrieval logic
"""

import json
from datetime import datetime, timedelta
from app.core.redis.client import redis_client
from app.core.redis.keys import (
    OTP_KEY,
    OTP_ATTEMPTS_KEY,
    OTP_LOCKOUT_KEY,
    format_key
)


class OTPStore:
    """
    Manages OTP storage in Redis
    
    Responsibilities:
    - Store OTP
    - Fetch OTP
    - Delete OTP
    - Track attempts
    - Check lockout
    """

    OTP_TTL = 300  # 5 minutes
    MAX_ATTEMPTS = 3
    LOCKOUT_DURATION = 900  # 15 minutes after max attempts

    @staticmethod
    def store_otp(phone: str, otp_code: str, ttl: int = OTP_TTL) -> bool:
        """
        Store OTP in Redis with TTL
        
        Args:
            phone: Phone number (e.g., "+919876543210")
            otp_code: 6-digit OTP code
            ttl: Time to live in seconds
            
        Returns:
            bool: True if stored successfully
        """
        key = format_key(OTP_KEY, phone=phone)
        try:
            redis_client.setex(key, ttl, otp_code)
            # Reset attempts on new OTP
            attempts_key = format_key(OTP_ATTEMPTS_KEY, phone=phone)
            redis_client.delete(attempts_key)
            return True
        except Exception as e:
            print(f"Error storing OTP: {e}")
            return False

    @staticmethod
    def get_otp(phone: str) -> str | None:
        """
        Fetch OTP from Redis
        
        Args:
            phone: Phone number
            
        Returns:
            str: OTP code if exists, None otherwise
        """
        key = format_key(OTP_KEY, phone=phone)
        try:
            return redis_client.get(key)
        except Exception as e:
            print(f"Error fetching OTP: {e}")
            return None

    @staticmethod
    def delete_otp(phone: str) -> bool:
        """
        Delete OTP from Redis (after successful verification)
        
        Args:
            phone: Phone number
            
        Returns:
            bool: True if deleted
        """
        key = format_key(OTP_KEY, phone=phone)
        attempts_key = format_key(OTP_ATTEMPTS_KEY, phone=phone)
        lockout_key = format_key(OTP_LOCKOUT_KEY, phone=phone)
        
        try:
            redis_client.delete(key)
            redis_client.delete(attempts_key)
            redis_client.delete(lockout_key)
            return True
        except Exception as e:
            print(f"Error deleting OTP: {e}")
            return False

    @staticmethod
    def increment_attempts(phone: str) -> int:
        """
        Increment OTP verification attempts
        
        Args:
            phone: Phone number
            
        Returns:
            int: Current attempt count
        """
        attempts_key = format_key(OTP_ATTEMPTS_KEY, phone=phone)
        try:
            attempts = redis_client.incr(attempts_key)
            # Set TTL on attempts key (same as OTP TTL)
            if attempts == 1:
                redis_client.expire(attempts_key, OTPStore.OTP_TTL)
            return attempts
        except Exception as e:
            print(f"Error incrementing attempts: {e}")
            return 0

    @staticmethod
    def is_locked_out(phone: str) -> bool:
        """
        Check if phone is locked out after max attempts
        
        Args:
            phone: Phone number
            
        Returns:
            bool: True if locked out
        """
        lockout_key = format_key(OTP_LOCKOUT_KEY, phone=phone)
        try:
            return redis_client.exists(lockout_key) > 0
        except Exception as e:
            print(f"Error checking lockout: {e}")
            return False

    @staticmethod
    def set_lockout(phone: str, duration: int = LOCKOUT_DURATION) -> bool:
        """
        Lock out phone after max attempts
        
        Args:
            phone: Phone number
            duration: Lockout duration in seconds
            
        Returns:
            bool: True if lockout set
        """
        lockout_key = format_key(OTP_LOCKOUT_KEY, phone=phone)
        try:
            redis_client.setex(lockout_key, duration, "locked")
            return True
        except Exception as e:
            print(f"Error setting lockout: {e}")
            return False

    @staticmethod
    def get_remaining_lockout_time(phone: str) -> int:
        """
        Get remaining lockout time in seconds
        
        Args:
            phone: Phone number
            
        Returns:
            int: Remaining seconds, -1 if not locked out
        """
        lockout_key = format_key(OTP_LOCKOUT_KEY, phone=phone)
        try:
            return redis_client.ttl(lockout_key)
        except Exception as e:
            print(f"Error getting lockout time: {e}")
            return -1
