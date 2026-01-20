# Phase-2 JWT Authentication Implementation

## Overview
Simple JWT-based authentication for Phase-2 API (`/api/v2`). Replaces database session lookups with stateless JWT tokens.

## Architecture

### Token Types
1. **Access Token** (15 minutes)
   - Used for API/WebSocket authentication
   - Contains: `user_id`, `phone_number`, `role`, `jti`
   - Verified on every request

2. **Refresh Token** (7 days)
   - Used to generate new access tokens
   - Stored in Redis for validation
   - Does NOT auto-refresh forever

### Auth Flow

#### 1. Login (OTP-based)
```
POST /api/v2/auth/send-otp
{
  "phone_number": "+919876543210"
}

Response:
{
  "message": "OTP sent successfully",
  "phone_number": "+919876543210"
}
```

```
POST /api/v2/auth/verify-otp
{
  "phone_number": "+919876543210",
  "otp_code": "123456"
}

Response:
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {
    "user_id": 5,
    "phone_number": "+919876543210",
    "full_name": "John Doe",
    "role": "driver"
  }
}
```

#### 2. Using Access Token
```
GET /api/v2/test/protected
Headers:
  Authorization: Bearer <access_token>

Response:
{
  "message": "JWT authentication successful",
  "user": {
    "user_id": 5,
    "phone_number": "+919876543210",
    "role": "driver",
    "jti": "abc-123-xyz"
  }
}
```

#### 3. Refreshing Access Token
```
POST /api/v2/auth/refresh
{
  "refresh_token": "eyJhbGc..."
}

Response:
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 900
}
```

#### 4. Logout
```
POST /api/v2/auth/logout
Headers:
  Authorization: Bearer <access_token>

Response:
{
  "message": "Logged out successfully"
}
```

## Redis Usage

### Keys Used
1. `jwt:blacklist:{jti}` - Blacklisted access tokens (TTL = remaining token lifetime)
2. `jwt:refresh:{jti}` - Active refresh tokens (TTL = 7 days)
3. `otp:{phone}` - OTP codes (TTL = 5 minutes)
4. `otp:attempts:{phone}` - Failed OTP attempts
5. `otp:lockout:{phone}` - Lockout after max attempts

### Rules
- Redis stores ONLY revoked/active tokens, NOT all tokens
- Access tokens are blacklisted on logout
- Refresh tokens are stored for validation
- OTP flow uses Redis for temporary storage

## Security Features

### OTP Security
- Max 3 attempts per OTP
- 15-minute lockout after max attempts
- 5-minute OTP expiry
- Phone-only authentication (no email)

### Token Security
- JWT signature verification
- Expiry checking
- Blacklist validation on every request
- Separate token types (access vs refresh)

### Role-Based Access
```python
from app.api.deps.jwt_auth import require_role

@router.get("/driver-only")
def driver_endpoint(current_user: dict = Depends(require_role(["driver"]))):
    return {"message": "Driver access granted"}
```

## File Structure

```
backend/app/
├── utils/
│   └── jwt_utils.py              # Token generation/verification
├── core/redis/
│   ├── keys.py                   # Redis key definitions
│   └── services/
│       ├── jwt_store.py          # JWT Redis operations
│       └── otp_store.py          # OTP Redis operations
├── api/
│   ├── deps/
│   │   └── jwt_auth.py           # JWT auth dependency
│   └── v2/
│       ├── __init__.py           # V2 router
│       ├── auth.py               # Login/logout/refresh
│       └── test.py               # Test protected endpoints
├── schemas/
│   └── jwt_auth.py               # Request/response models
└── main.py                       # App with v2 routes
```

## Phase Separation

| Aspect | Phase-1 (/api/v1) | Phase-2 (/api/v2) |
|--------|-------------------|-------------------|
| Auth | Session-based | JWT-based |
| Login | Email + password | Phone + OTP |
| Storage | PostgreSQL sessions | Redis (ephemeral) |
| Token | Session ID | Access + Refresh tokens |
| Middleware | `get_current_user_session` | `get_current_user` (JWT) |

**CRITICAL**: Phase-1 and Phase-2 are completely separate. No mixing.

## Error Handling

| Scenario | Status Code | Detail |
|----------|-------------|--------|
| Invalid token | 401 | "Invalid or expired token" |
| Blacklisted token | 401 | "Token has been revoked" |
| Wrong role | 403 | "Insufficient permissions" |
| OTP expired | 400 | "OTP expired or not found" |
| Wrong OTP | 401 | "Invalid OTP. X attempts remaining" |
| Too many attempts | 429 | "Too many attempts. Try again in X seconds" |

## Testing

### 1. Install PyJWT
```bash
pip install PyJWT==2.8.0
```

### 2. Start Backend
```bash
cd backend
uvicorn app.main:app --reload
```

### 3. Test Flow
```bash
# 1. Send OTP
curl -X POST http://localhost:8000/api/v2/auth/send-otp \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+919876543210"}'

# 2. Verify OTP (check console for OTP in dev mode)
curl -X POST http://localhost:8000/api/v2/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+919876543210", "otp_code": "123456"}'

# 3. Use access token
curl -X GET http://localhost:8000/api/v2/test/protected \
  -H "Authorization: Bearer <access_token>"

# 4. Refresh token
curl -X POST http://localhost:8000/api/v2/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "<refresh_token>"}'

# 5. Logout
curl -X POST http://localhost:8000/api/v2/auth/logout \
  -H "Authorization: Bearer <access_token>"
```

## Compliance Checklist

✅ JWT used ONLY for Phase-2  
✅ Access token (15 min) + Refresh token (7 days)  
✅ Payload: `user_id`, `phone_number`, `role`, `jti` only  
✅ OTP-based login (phone only, no email)  
✅ Logout blacklists access token  
✅ Redis used for revocation + ephemeral data  
✅ No mixing with Phase-1  
✅ Simple, clean, MVP-ready  

## Next Steps

To protect new Phase-2 endpoints:

```python
from fastapi import APIRouter, Depends
from app.api.deps.jwt_auth import get_current_user

router = APIRouter()

@router.get("/my-endpoint")
def my_endpoint(current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    role = current_user["role"]
    # Your logic here
    return {"status": "success"}
```

For role-specific endpoints:
```python
from app.api.deps.jwt_auth import require_role

@router.post("/driver-action")
def driver_action(current_user: dict = Depends(require_role(["driver"]))):
    # Only drivers can access
    return {"status": "success"}
```
