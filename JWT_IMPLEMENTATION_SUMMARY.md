# Phase-2 JWT Implementation - Summary

## What Was Built

A clean, MVP-ready JWT authentication system for Phase-2 API (`/api/v2`) with OTP-based login.

## Key Components

### 1. JWT Utilities (`app/utils/jwt_utils.py`)
- `generate_access_token()` - Issues 15-minute access tokens
- `generate_refresh_token()` - Issues 7-day refresh tokens
- `decode_token()` - Verifies JWT signature and expiry
- `get_token_expiry_seconds()` - Calculates remaining token lifetime

### 2. JWT Auth Dependency (`app/api/deps/jwt_auth.py`)
- `verify_jwt()` - Verifies token + checks blacklist
- `get_current_user()` - Extracts user from JWT
- `require_role()` - Role-based access control

### 3. JWT Redis Store (`app/core/redis/services/jwt_store.py`)
- `blacklist_access_token()` - Revokes tokens on logout
- `is_access_token_blacklisted()` - Checks if token is revoked
- `store_refresh_token()` - Stores refresh token for validation
- `get_refresh_token()` - Retrieves refresh token
- `delete_refresh_token()` - Removes refresh token

### 4. Auth Router (`app/api/v2/auth.py`)
- `POST /api/v2/auth/send-otp` - Initiate OTP login
- `POST /api/v2/auth/verify-otp` - Verify OTP, issue tokens
- `POST /api/v2/auth/refresh` - Get new access token
- `POST /api/v2/auth/logout` - Revoke tokens

### 5. Test Endpoints (`app/api/v2/test.py`)
- `GET /api/v2/test/protected` - Requires JWT
- `GET /api/v2/test/driver-only` - Requires driver role
- `GET /api/v2/test/admin-only` - Requires admin role

## Token Payloads

### Access Token (15 minutes)
```json
{
  "user_id": 5,
  "phone_number": "+919876543210",
  "role": "driver",
  "jti": "unique-token-id",
  "iat": 1234567890,
  "exp": 1234568790
}
```

### Refresh Token (7 days)
```json
{
  "user_id": 5,
  "phone_number": "+919876543210",
  "role": "driver",
  "jti": "unique-refresh-id",
  "token_type": "refresh",
  "iat": 1234567890,
  "exp": 1234654290
}
```

## OTP Security Features

✅ Max 3 failed attempts  
✅ 15-minute lockout after max attempts  
✅ 5-minute OTP expiry  
✅ Phone-only login (no email)  

## Redis Keys

| Key | Purpose | TTL |
|-----|---------|-----|
| `jwt:blacklist:{jti}` | Revoked access tokens | Remaining token lifetime |
| `jwt:refresh:{jti}` | Active refresh tokens | 7 days |
| `otp:{phone}` | OTP codes | 5 minutes |
| `otp:attempts:{phone}` | Failed attempts | 5 minutes |
| `otp:lockout:{phone}` | Account lockout | 15 minutes |

## Phase Separation

**Phase-1 (/api/v1)**: Session-based auth (UNCHANGED)  
**Phase-2 (/api/v2)**: JWT-based auth (NEW)  

✅ No mixing  
✅ Phase-1 continues to work  
✅ Phase-2 is independent  

## Guard Rails Compliance

✅ Redis is NOT persistent storage (all keys have TTL)  
✅ Redis is NOT business logic (only stores tokens)  
✅ Redis is used for: OTP, token revocation, ephemeral data  
✅ PostgreSQL remains source of truth  
✅ No email-based authentication (phone only)  
✅ No OAuth/SSO/third-party auth  
✅ No permissions/scopes (roles only)  
✅ No complex token rotation  

## Files Modified/Created

### Created
- `backend/app/utils/jwt_utils.py`
- `backend/app/api/v2/__init__.py`
- `backend/app/api/v2/auth.py`
- `backend/app/api/v2/test.py`
- `backend/app/api/deps/jwt_auth.py`
- `backend/app/schemas/jwt_auth.py`
- `JWT_AUTH_GUIDE.md` (documentation)

### Modified
- `backend/app/main.py` - Added v2 routes
- `backend/app/core/redis/keys.py` - Updated JWT keys
- `backend/app/core/redis/services/jwt_store.py` - Complete rewrite
- `requirements.txt` - Added PyJWT==2.8.0

## Usage Example

```python
from fastapi import APIRouter, Depends
from app.api.deps.jwt_auth import get_current_user, require_role

router = APIRouter()

# Any authenticated user
@router.get("/my-data")
def get_data(current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    phone = current_user["phone_number"]
    return {"user_id": user_id}

# Driver only
@router.post("/accept-ride")
def accept_ride(current_user: dict = Depends(require_role(["driver"]))):
    return {"status": "ride accepted"}

# Admin only
@router.delete("/user/{user_id}")
def delete_user(user_id: int, current_user: dict = Depends(require_role(["admin"]))):
    return {"status": "user deleted"}
```

## Error Handling

| Scenario | Code | Message |
|----------|------|---------|
| Invalid token | 401 | "Invalid or expired token" |
| Revoked token | 401 | "Token has been revoked" |
| Insufficient role | 403 | "Insufficient permissions" |
| OTP expired | 400 | "OTP expired or not found" |
| Wrong OTP | 401 | "Invalid OTP. X attempts remaining" |
| Account locked | 429 | "Too many attempts. Try again in X seconds" |

## Definition of Done ✅

- [x] OTP login issues access + refresh tokens
- [x] Access token protects /api/v2 routes
- [x] Logout revokes tokens via Redis blacklist
- [x] Redis blacklist is checked on every request
- [x] Phase-1 continues unchanged
- [x] All code follows guard rails
- [x] Simple, MVP-ready design
- [x] Documentation complete
- [x] PyJWT installed and working

## Next: Integrating with Phase-2 Features

To add JWT protection to existing Phase-2 endpoints:

1. Import dependency:
   ```python
   from app.api.deps.jwt_auth import get_current_user
   ```

2. Add to endpoint:
   ```python
   @router.get("/some-endpoint")
   def endpoint(current_user: dict = Depends(get_current_user)):
       # Your code
   ```

3. Access user info:
   ```python
   user_id = current_user["user_id"]
   phone = current_user["phone_number"]
   role = current_user["role"]
   ```

That's it! No more changes needed.
