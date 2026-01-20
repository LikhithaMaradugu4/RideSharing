"""
Session Redis Store - Handles user session management
"""

import json
from datetime import datetime
from app.core.redis.client import redis_client
from app.core.redis.keys import SESSION_KEY, format_key


class SessionStore:
    """
    Manages user session data in Redis
    
    Responsibilities:
    - Store session
    - Fetch session
    - Delete session
    - Check session validity
    """

    SESSION_TTL = 86400  # 24 hours

    @staticmethod
    def store_session(session_id: str, user_id: int, role: str, ttl: int = SESSION_TTL) -> bool:
        """
        Store session in Redis
        
        Args:
            session_id: Session ID
            user_id: User ID
            role: User role (DRIVER, RIDER, TENANT_ADMIN)
            ttl: Time to live in seconds
            
        Returns:
            bool: True if stored successfully
        """
        try:
            session_data = {
                "user_id": user_id,
                "role": role,
                "created_at": datetime.utcnow().isoformat()
            }
            
            key = format_key(SESSION_KEY, session_id=session_id)
            redis_client.setex(key, ttl, json.dumps(session_data))
            return True
        except Exception as e:
            print(f"Error storing session: {e}")
            return False

    @staticmethod
    def get_session(session_id: str) -> dict | None:
        """
        Fetch session from Redis
        
        Args:
            session_id: Session ID
            
        Returns:
            dict: Session data if valid, None otherwise
        """
        try:
            key = format_key(SESSION_KEY, session_id=session_id)
            session_json = redis_client.get(key)
            if session_json:
                return json.loads(session_json)
            return None
        except Exception as e:
            print(f"Error fetching session: {e}")
            return None

    @staticmethod
    def delete_session(session_id: str) -> bool:
        """
        Delete session from Redis (logout)
        
        Args:
            session_id: Session ID
            
        Returns:
            bool: True if deleted
        """
        try:
            key = format_key(SESSION_KEY, session_id=session_id)
            redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Error deleting session: {e}")
            return False

    @staticmethod
    def is_session_valid(session_id: str) -> bool:
        """
        Check if session is still valid
        
        Args:
            session_id: Session ID
            
        Returns:
            bool: True if session exists
        """
        try:
            key = format_key(SESSION_KEY, session_id=session_id)
            return redis_client.exists(key) > 0
        except Exception as e:
            print(f"Error checking session: {e}")
            return False
