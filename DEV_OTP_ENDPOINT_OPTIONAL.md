# 🔧 Optional: Add Development OTP Endpoint

## 📌 Why Add This Endpoint?

Currently, to get the OTP you must:
1. Call `/send-otp`
2. Look at the backend console output
3. Find the `[DEV MODE] OTP for...` line

**Easier way**: Add an API endpoint to retrieve it programmatically

---

## 📝 Code to Add

Add this to the end of `backend/app/api/v2/auth.py` (after the logout endpoint):

```python
@router.get("/get-otp-dev")
def get_otp_dev(phone_number: str):
    """
    ⚠️ DEVELOPMENT ONLY - Get OTP from Redis
    
    This endpoint is ONLY for testing and development.
    In production, this should NOT exist.
    
    Usage:
        GET /api/v2/auth/get-otp-dev?phone_number=%2B919876543210
    
    Response:
        {
            "phone_number": "+919876543210",
            "otp": "123456",
            "expires_in": 245
        }
    """
    otp = OTPStore.get_otp(phone_number)
    
    if not otp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OTP not found or expired"
        )
    
    # Get Redis TTL for this OTP
    from app.core.redis.client import redis_client
    from app.core.redis.keys import OTP_KEY, format_key
    
    otp_key = format_key(OTP_KEY, phone=phone_number)
    remaining_ttl = redis_client.ttl(otp_key)
    
    return {
        "phone_number": phone_number,
        "otp": otp,
        "expires_in": remaining_ttl,
        "warning": "⚠️ This endpoint is for development only"
    }
```

---

## 🚀 How to Use

### Step 1: Send OTP
```bash
curl -X POST http://localhost:8000/api/v2/auth/send-otp \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+919876543210"}'
```

### Step 2: Get OTP from API
```bash
curl -X GET "http://localhost:8000/api/v2/auth/get-otp-dev?phone_number=%2B919876543210"
```

**Response**:
```json
{
  "phone_number": "+919876543210",
  "otp": "456789",
  "expires_in": 245,
  "warning": "⚠️ This endpoint is for development only"
}
```

### Step 3: Use OTP to Login
```bash
curl -X POST http://localhost:8000/api/v2/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+919876543210",
    "otp_code": "456789"
  }'
```

---

## 📱 URL Encoding Note

In the GET request, `+` is a special character, so:
- Phone: `+919876543210`
- URL encoded: `%2B919876543210`

**Using curl automatically encodes**:
```bash
curl "http://localhost:8000/api/v2/auth/get-otp-dev?phone_number=%2B919876543210"
```

**Using Postman**: Just paste `+919876543210` in the query param, Postman encodes it automatically.

---

## ⚠️ IMPORTANT: Production Safety

**This endpoint should NEVER exist in production!**

To keep it dev-only, add a check at the top:

```python
import os

@router.get("/get-otp-dev")
def get_otp_dev(phone_number: str):
    # Only allow in development
    if os.getenv("ENVIRONMENT") == "production":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is not available in production"
        )
    
    # ... rest of code
```

---

## 🎯 Complete Workflow

```
1. Send OTP
   POST /api/v2/auth/send-otp
   
2. Get OTP from API
   GET /api/v2/auth/get-otp-dev?phone_number=...
   
3. Verify OTP & Get Tokens
   POST /api/v2/auth/verify-otp
   
4. Use Access Token
   GET /api/v2/any-endpoint
   Authorization: Bearer <access_token>
```

---

## 🔄 Current Flow (Without Dev Endpoint)

```
Backend Console:
[DEV MODE] OTP for +919876543210: 456789
                                    ↑ Copy this

Then use in /verify-otp endpoint
```

## ✨ New Flow (With Dev Endpoint)

```
GET /api/v2/auth/get-otp-dev?phone_number=...
↓
API Response: {"otp": "456789", ...}
                        ↑ Copy this

Then use in /verify-otp endpoint
```

---

## 📋 Summary

**Without dev endpoint**:
- ✅ Simple, minimal code
- ❌ Must check backend console

**With dev endpoint**:
- ✅ Easier testing (get OTP via API)
- ✅ Automated testing possible
- ✅ Frontend can fetch OTP for testing
- ❌ Slightly more code
- ⚠️ Must disable in production

---

**Recommendation**: Add the dev endpoint for easier testing. Just remember to remove or disable it before deploying to production!
