"""
JWT Authentication Dependencies for Phase-2
Provides JWT token validation and role-based access control using HTTPBearer security
"""

from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Callable

from app.utils.jwt_utils import decode_token
from app.core.redis.services.jwt_store import JWTStore


# HTTP Bearer security scheme for OpenAPI documentation
security = HTTPBearer(
    scheme_name="JWT Bearer Token",
    description="Enter your JWT access token",
    auto_error=True
)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    token = credentials.credentials
    
    # Decode and validate JWT token
    user_data = decode_token(token)
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Optional: Check if token is blacklisted in Redis
    jti = user_data.get("jti")
    if jti:
        jwt_store = JWTStore()
        if jwt_store.is_token_blacklisted(jti):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
                headers={"WWW-Authenticate": "Bearer"}
            )
    
    return user_data


def require_role(allowed_roles: List[str]) -> Callable:
    
    async def role_checker(
        current_user: dict = Depends(get_current_user)
    ) -> dict:
        """Validate user has required role"""
        user_role = current_user.get("role", "").upper()
        allowed_roles_upper = [role.upper() for role in allowed_roles]
        
        if user_role not in allowed_roles_upper:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role(s): {', '.join(allowed_roles)}"
            )
        
        return current_user
    
    return role_checker


# ============================================================================
# TESTING HELPER FUNCTIONS (Optional)
# ============================================================================

async def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False))
) -> dict | None:
    if not credentials:
        return None
    
    user_data = decode_token(credentials.credentials)
    return user_data if user_data else None
