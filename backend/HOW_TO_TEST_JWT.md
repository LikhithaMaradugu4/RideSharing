# How to Test JWT Authentication

## Overview
The `jwt_auth.py` file provides secure JWT-based authentication using FastAPI's **HTTPBearer** security scheme.

## Key Features

### 1. **HTTPBearer Security Scheme**
```python
security = HTTPBearer(
    scheme_name="JWT Bearer Token",
    description="Enter your JWT access token",
    auto_error=True
)
```
- Automatically extracts `Authorization: Bearer <token>` header
- Provides interactive API docs (Swagger UI) with "Authorize" button
- Validates token format automatically

### 2. **get_current_user() Dependency**
Validates JWT token and returns user data:
```python
@router.get("/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    return {
        "user_id": current_user["user_id"],
        "role": current_user["role"],
        "phone": current_user["phone_number"]
    }
```

### 3. **require_role() Factory**
Role-based access control:
```python
@router.post("/accept-ride")
async def accept_ride(
    current_user: dict = Depends(require_role(["DRIVER"]))
):
    return {"driver_id": current_user["user_id"]}
```

### 4. **Token Blacklist Check**
Automatically checks Redis for revoked tokens (logout functionality).

---

## Testing Guide

### Step 1: Start the Server
```bash
cd backend
uvicorn app.main:app --reload
```

### Step 2: Get Access Token

#### Option A: Use Swagger UI
1. Open http://localhost:8000/docs
2. Find `/api/v2/auth/send-otp` endpoint
3. Send OTP to your phone number
4. Use `/api/v2/auth/verify-otp` to get tokens

#### Option B: Use cURL
```bash
# Step 1: Send OTP
curl -X POST http://localhost:8000/api/v2/auth/send-otp \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+1234567890"}'

# Step 2: Verify OTP
curl -X POST http://localhost:8000/api/v2/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+1234567890",
    "otp_code": "123456"
  }'

# Response:
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 900
}
```

### Step 3: Test Protected Endpoints

#### Using Swagger UI (Recommended)
1. Click **"Authorize"** button (lock icon) at top right
2. Enter: `Bearer <your_access_token>` or just `<your_access_token>`
3. Click "Authorize"
4. Now all requests will include the token automatically!

#### Using cURL
```bash
# Test protected endpoint
curl -X GET http://localhost:8000/api/v2/test/protected \
  -H "Authorization: Bearer eyJhbGc..."

# Test driver-only endpoint
curl -X GET http://localhost:8000/api/v2/test/driver-only \
  -H "Authorization: Bearer <driver_token>"

# Test admin-only endpoint
curl -X GET http://localhost:8000/api/v2/test/admin-only \
  -H "Authorization: Bearer <admin_token>"
```

#### Using Python
```python
import requests

# Get token first
response = requests.post(
    "http://localhost:8000/api/v2/auth/verify-otp",
    json={"phone_number": "+1234567890", "otp_code": "123456"}
)
token = response.json()["access_token"]

# Use token in protected endpoints
headers = {"Authorization": f"Bearer {token}"}

# Test authentication
response = requests.get(
    "http://localhost:8000/api/v2/test/protected",
    headers=headers
)
print(response.json())
# Output: {"message": "JWT authentication successful", "user": {...}}

# Test role-based access
response = requests.get(
    "http://localhost:8000/api/v2/test/driver-only",
    headers=headers
)
print(response.json())
```

---

## What Happens Behind the Scenes

### 1. **Client sends request with token**
```
GET /api/v2/test/protected
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 2. **HTTPBearer extracts token**
FastAPI's `HTTPBearer` security scheme automatically:
- Validates header format
- Extracts token from "Bearer <token>"
- Passes token to `get_current_user()`

### 3. **get_current_user() validates token**
```python
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials  # Auto-extracted by HTTPBearer
    
    # Decode JWT
    user_data = decode_token(token)  # Verifies signature & expiry
    
    # Check blacklist
    if jwt_store.is_access_token_blacklisted(jti):
        raise HTTPException(401, "Token revoked")
    
    return user_data  # {"user_id": 123, "role": "DRIVER", ...}
```

### 4. **Role check (if using require_role)**
```python
def require_role(["DRIVER"]):
    # First calls get_current_user() to get user data
    # Then checks: user_data["role"] in ["DRIVER"]
    # Returns user_data if authorized, raises 403 if not
```

---

## Error Responses

### 401 Unauthorized (Invalid Token)
```json
{
  "detail": "Invalid or expired token"
}
```

### 401 Unauthorized (No Token)
```json
{
  "detail": "Not authenticated"
}
```

### 401 Unauthorized (Revoked Token)
```json
{
  "detail": "Token has been revoked"
}
```

### 403 Forbidden (Wrong Role)
```json
{
  "detail": "Access denied. Required role(s): DRIVER"
}
```

---

## Token Structure

Access tokens contain:
```json
{
  "user_id": 123,
  "phone_number": "+1234567890",
  "role": "DRIVER",
  "jti": "550e8400-e29b-41d4-a716-446655440000",
  "iat": 1705747200,
  "exp": 1705748100
}
```

---

## Best Practices

### ✅ DO:
- Use `Depends(get_current_user)` for all protected endpoints
- Use `Depends(require_role([...]))` for role-specific endpoints
- Test with Swagger UI for quick verification
- Check token expiry (15 minutes for access tokens)

### ❌ DON'T:
- Don't store tokens in URL parameters
- Don't send tokens in request body
- Don't forget to handle 401/403 errors in frontend
- Don't use expired or revoked tokens

---

## Integration Example

```python
from fastapi import APIRouter, Depends
from app.api.deps.jwt_auth import get_current_user, require_role

router = APIRouter()

# Public endpoint (no auth)
@router.get("/public")
async def public_data():
    return {"message": "No authentication required"}

# Protected endpoint (any authenticated user)
@router.get("/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    return {
        "user_id": current_user["user_id"],
        "role": current_user["role"]
    }

# Driver-only endpoint
@router.post("/start-shift")
async def start_shift(current_user: dict = Depends(require_role(["DRIVER"]))):
    driver_id = current_user["user_id"]
    return {"message": "Shift started", "driver_id": driver_id}

# Admin-only endpoint
@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: dict = Depends(require_role(["TENANT_ADMIN"]))
):
    return {"message": f"User {user_id} deleted by admin"}

# Multiple roles allowed
@router.get("/dashboard")
async def dashboard(
    current_user: dict = Depends(require_role(["DRIVER", "TENANT_ADMIN"]))
):
    return {"role": current_user["role"], "dashboard": "data"}
```

---

## Summary

✅ **HTTPBearer** handles token extraction automatically  
✅ **get_current_user** validates JWT and checks blacklist  
✅ **require_role** provides role-based access control  
✅ **Swagger UI** provides interactive testing with "Authorize" button  
✅ **Token blacklist** prevents usage of revoked tokens  

Now your JWT authentication is **production-ready** and **easy to test**! 🚀
