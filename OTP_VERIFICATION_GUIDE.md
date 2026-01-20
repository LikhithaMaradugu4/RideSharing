# 🔑 How to Check OTP - Complete Guide

## 📌 Why OTP is in Console (Development Mode)

In the code at line 88 of `backend/app/api/v2/auth.py`:
```python
# In production: Send via SMS gateway
print(f"[DEV MODE] OTP for {phone}: {otp_code}")
```

This means:
- ✅ **In Development**: OTP is printed to the backend console
- ❌ **In Production**: OTP would be sent via SMS service (Twilio, AWS SNS, etc.)

---

## 🔍 How to Get the OTP (3 Methods)

### Method 1: Check Backend Console (EASIEST)

**Step 1**: Look at the backend terminal where FastAPI is running
```
[DEV MODE] OTP for +919876543210: 456789
```

**Step 2**: Copy the OTP code from the console output

**Step 3**: Use it in the `/verify-otp` endpoint

---

### Method 2: Check Redis Directly (Advanced)

If you want to verify OTP is actually stored in Redis:

**Step 1**: Connect to Redis CLI
```bash
redis-cli
```

**Step 2**: Get the OTP from Redis
```bash
GET otp:+919876543210
```

**Output**:
```
"456789"
```

**Step 3**: This is your OTP code

---

### Method 3: Add a Development Endpoint (Optional)

I can create a `/get-otp-dev` endpoint that returns the OTP for testing. Would you like me to do that?

---

## 📝 Complete OTP Flow Example

### Step 1: Request OTP
```bash
curl -X POST http://localhost:8000/api/v2/auth/send-otp \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+919876543210"}'
```

**Backend Console Output**:
```
[DEV MODE] OTP for +919876543210: 456789
```

**API Response**:
```json
{
  "message": "OTP sent successfully",
  "phone_number": "+919876543210"
}
```

### Step 2: Copy OTP from Console
From the console: `456789`

### Step 3: Verify OTP
```bash
curl -X POST http://localhost:8000/api/v2/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+919876543210",
    "otp_code": "456789"
  }'
```

**Success Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
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

---

## ⏱️ OTP Timing

| Event | Duration | Action |
|-------|----------|--------|
| OTP created | - | Stored in Redis |
| Valid for | 5 minutes | Then expires |
| After expiry | - | User must request new OTP |
| Max attempts | 3 | Then 15-minute lockout |

---

## 🚨 What If OTP Expires?

### Scenario: User waits too long
```
1. OTP sent at 2:00 PM
2. User checks console at 2:06 PM (6 minutes later)
3. OTP has EXPIRED
4. Response: "OTP expired or not found. Request a new one"
5. Solution: Call /send-otp again
```

### How to fix it:
Call `/send-otp` again:
```bash
curl -X POST http://localhost:8000/api/v2/auth/send-otp \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+919876543210"}'
```

New OTP will be generated and printed to console.

---

## ❌ What If OTP is Wrong?

### Scenario: User enters wrong OTP
```
Attempt 1: Enter "123456" (wrong)
  ↓ Error: "Invalid OTP. 2 attempts remaining"

Attempt 2: Enter "654321" (wrong)
  ↓ Error: "Invalid OTP. 1 attempts remaining"

Attempt 3: Enter "789012" (wrong)
  ↓ Error: "Too many attempts. Account locked for 15 minutes"

Wait 15 minutes, then try again or call /send-otp
```

---

## 🔧 Development Debugging

### To view all OTP attempts in Redis:
```bash
redis-cli KEYS "otp*"
```

Output:
```
1) "otp:attempts:+919876543210"
2) "otp:+919876543210"
```

### Check attempt count:
```bash
redis-cli GET "otp:attempts:+919876543210"
```

Output: `1` or `2` or `3`

### Check if account is locked:
```bash
redis-cli EXISTS "otp:lockout:+919876543210"
```

Output: `1` (exists/locked) or `0` (not locked)

---

## 📱 Backend Console Log Format

When you send OTP, look for this exact pattern in your terminal:

```
[DEV MODE] OTP for +919876543210: 456789
```

**Breakdown**:
- `[DEV MODE]` = Development mode (not production)
- `for +919876543210` = Phone number that requested OTP
- `: 456789` = The actual OTP code to use

---

## 🎯 Quick Reference: How to Find OTP

| Location | How to Access | When to Use |
|----------|---------------|------------|
| Backend Console | Look at terminal where FastAPI runs | Always (easiest) |
| Redis | `redis-cli GET otp:{phone}` | Debugging |
| Development API | Not created yet (optional) | If needed |

---

## ⚙️ Optional: Create Development Endpoint

Would you like me to create a `/get-otp-dev` endpoint so you can fetch the OTP via API instead of reading console?

**Pros**:
- Easier to test from Postman/frontend
- No need to look at console
- Automated testing possible

**Cons**:
- Exposes OTP via API (security risk in production)
- Only for development

**Example usage**:
```bash
curl -X GET http://localhost:8000/api/v2/auth/get-otp-dev?phone_number=%2B919876543210
```

Response:
```json
{
  "phone_number": "+919876543210",
  "otp": "456789",
  "expires_in": 245
}
```

---

## 🔒 Production Implementation

In production, replace the `print()` statement with:

```python
# In production: Send via SMS gateway
import requests

# Example with Twilio
client = TwilioClient(account_sid, auth_token)
message = client.messages.create(
    body=f"Your OTP is: {otp_code}",
    from_="+1234567890",
    to=phone
)
```

Or with AWS SNS, Firebase, etc.

---

## 📝 Summary

**Current Flow**:
1. User calls `/send-otp` with phone number
2. OTP is generated and stored in Redis (5 min TTL)
3. OTP is printed to **backend console** (dev mode)
4. User reads OTP from console
5. User sends OTP to `/verify-otp` endpoint
6. If correct → get JWT tokens
7. If wrong → error and attempt count

**Three ways to get OTP**:
1. ✅ **Read console output** (easiest)
2. ✅ **Query Redis** (technical)
3. 🆕 **Create dev endpoint** (optional)

---

## 🆚 Comparison: Dev vs Production

| Stage | OTP Delivery | How User Gets It | Security |
|-------|--------------|------------------|----------|
| Development | Console print | Read terminal | ⚠️ Low (exposed in logs) |
| Testing | Redis query | Query database | ⚠️ Medium (internal only) |
| Production | SMS/Email | User's phone/email | ✅ High (user's device only) |

---

**Next Steps**:
1. Run `/send-otp` endpoint
2. Check your backend terminal for `[DEV MODE]` message
3. Copy the OTP code
4. Use it in `/verify-otp` to get JWT tokens

Need help with the next step? Let me know! 🚀
