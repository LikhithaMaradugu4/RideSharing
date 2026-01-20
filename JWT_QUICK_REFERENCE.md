# Phase-2 JWT Auth - Quick Reference

## 🔐 Login Flow

```bash
# 1. Send OTP
curl -X POST http://localhost:8000/api/v2/auth/send-otp \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+919876543210"}'

# Response: Check console for OTP (dev mode)

# 2. Verify OTP (get tokens)
curl -X POST http://localhost:8000/api/v2/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+919876543210",
    "otp_code": "123456"
  }'

# Response:
# {
#   "access_token": "eyJhbGc...",
#   "refresh_token": "eyJhbGc...",
#   "expires_in": 900,
#   "user": {...}
# }
```

## 🛡️ Using Access Token

```bash
curl -X GET http://localhost:8000/api/v2/test/protected \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

## 🔄 Refresh Access Token

```bash
curl -X POST http://localhost:8000/api/v2/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "<REFRESH_TOKEN>"}'
```

## 🚪 Logout

```bash
curl -X POST http://localhost:8000/api/v2/auth/logout \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

## 📝 Protecting Endpoints

```python
from fastapi import APIRouter, Depends
from app.api.deps.jwt_auth import get_current_user

router = APIRouter()

@router.get("/protected")
def my_endpoint(current_user: dict = Depends(get_current_user)):
    return {
        "user_id": current_user["user_id"],
        "phone": current_user["phone_number"],
        "role": current_user["role"]
    }
```

## 👥 Role-Based Access

```python
from app.api.deps.jwt_auth import require_role

@router.post("/driver-action")
def driver_only(current_user: dict = Depends(require_role(["driver"]))):
    return {"status": "success"}

@router.delete("/admin-action")
def admin_only(current_user: dict = Depends(require_role(["admin"]))):
    return {"status": "success"}
```

## ⏱️ Token Timings

| Token | Lifetime | Use |
|-------|----------|-----|
| Access | 15 minutes | Every API request |
| Refresh | 7 days | Get new access token |
| OTP | 5 minutes | Verify during login |

## 🔑 Current User Data

```python
def my_endpoint(current_user: dict = Depends(get_current_user)):
    # Available fields:
    current_user["user_id"]      # int
    current_user["phone_number"] # str
    current_user["role"]         # str: rider/driver/admin
    current_user["jti"]          # str: unique token ID
```

## ❌ Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| 401 Invalid token | Token expired or malformed | Get new token via refresh or login |
| 401 Token revoked | Token blacklisted on logout | Login again |
| 403 Insufficient permissions | Wrong role | Contact admin |
| 429 Too many attempts | Max OTP attempts exceeded | Wait 15 minutes |

## 📍 Endpoints

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| POST | /api/v2/auth/send-otp | ❌ | Send OTP to phone |
| POST | /api/v2/auth/verify-otp | ❌ | Verify OTP, get tokens |
| POST | /api/v2/auth/refresh | ❌ | Get new access token |
| POST | /api/v2/auth/logout | ✅ | Revoke tokens |
| GET | /api/v2/test/protected | ✅ | Test endpoint |
| GET | /api/v2/test/driver-only | ✅ | Driver test |
| GET | /api/v2/test/admin-only | ✅ | Admin test |

## 🚨 Important Rules

✅ DO: Add `Depends(get_current_user)` to Phase-2 endpoints  
❌ DON'T: Use in Phase-1 (/api/v1)  
✅ DO: Check `current_user["role"]` for authorization  
❌ DON'T: Trust `Authorization` header without verification  
✅ DO: Use `require_role()` for role-based access  
❌ DON'T: Store JWT in database  

## 🔧 Development

All code is in:
- `backend/app/utils/jwt_utils.py` - Token generation
- `backend/app/api/deps/jwt_auth.py` - Auth dependencies
- `backend/app/api/v2/` - Phase-2 routes
- `backend/app/core/redis/services/jwt_store.py` - Token revocation

For detailed docs, see: `JWT_AUTH_GUIDE.md`
