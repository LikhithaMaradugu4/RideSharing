"""
JWT Redis Store - Handles JWT blacklisting and refresh token storage
"""

import json
from app.core.redis.client import redis_client
from app.core.redis.keys import (
    JWT_BLACKLIST_KEY,
    JWT_REFRESH_TOKEN_KEY,
    format_key
)


class JWTStore:
    """
    Manages JWT tokens in Redis
    
    Responsibilities:
    - Blacklist access tokens (by jti)
    - Store refresh tokens
    - Validate refresh tokens
    """

    @staticmethod
    def blacklist_access_token(jti: str, ttl: int) -> bool:
        """
        Add access token jti to blacklist
        
        Args:
            jti: Unique token ID from JWT payload
            ttl: Time to live (remaining token lifetime)
            
        Returns:
            bool: True if blacklisted successfully
        """
        try:
            key = format_key(JWT_BLACKLIST_KEY, jti=jti)
            redis_client.setex(key, ttl, "revoked")
            return True
        except Exception as e:
            print(f"Error blacklisting token: {e}")
            return False

    @staticmethod
    def is_access_token_blacklisted(jti: str) -> bool:
        """
        Check if access token is blacklisted
        
        Args:
            jti: Unique token ID
            
        Returns:
            bool: True if blacklisted
        """
        try:
            key = format_key(JWT_BLACKLIST_KEY, jti=jti)
            return redis_client.exists(key) > 0
        except Exception as e:
            print(f"Error checking token blacklist: {e}")
            return False

    @staticmethod
    def store_refresh_token(jti: str, user_id: int, phone_number: str, role: str, ttl: int) -> bool:
        """
        Store refresh token in Redis
        
        Args:
            jti: Unique token ID
            user_id: User ID
            phone_number: Phone number
            role: User role
            ttl: Time to live in seconds
            
        Returns:
            bool: True if stored successfully
        """
        try:
            refresh_data = {
                "user_id": user_id,
                "phone_number": phone_number,
                "role": role
            }
            key = format_key(JWT_REFRESH_TOKEN_KEY, jti=jti)
            redis_client.setex(key, ttl, json.dumps(refresh_data))
            return True
        except Exception as e:
            print(f"Error storing refresh token: {e}")
            return False

    @staticmethod
    def get_refresh_token(jti: str) -> dict | None:
        """
        Get refresh token data from Redis
        
        Args:
            jti: Unique token ID
            
        Returns:
            dict: Refresh token data if valid, None otherwise
        """
        try:
            key = format_key(JWT_REFRESH_TOKEN_KEY, jti=jti)
            data = redis_client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            print(f"Error fetching refresh token: {e}")
            return None

    @staticmethod
    def delete_refresh_token(jti: str) -> bool:
        """
        Delete refresh token from Redis (on logout)
        
        Args:
            jti: Unique token ID
            
        Returns:
            bool: True if deleted
        """
        try:
            key = format_key(JWT_REFRESH_TOKEN_KEY, jti=jti)
            redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Error deleting refresh token: {e}")
            return False

