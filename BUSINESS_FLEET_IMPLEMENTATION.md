# BUSINESS Fleet Owner Onboarding - Implementation Summary

## ✅ Implementation Status: COMPLETE

This document outlines the implemented BUSINESS fleet owner onboarding flow in accordance with MVP requirements.

---

## 🎯 Core Requirements Implemented

### 1. Fleet Type Support
- **INDIVIDUAL**: Auto-created for approved drivers (not via API)
- **BUSINESS**: Explicit fleet owner onboarding via `/fleet/apply` endpoint

### 2. Eligibility Rules
✅ **Implemented:**
- Any authenticated user can apply as BUSINESS fleet owner
- Optional policy enforced: Users with **APPROVED** driver profiles are rejected
- Users can only have ONE fleet application

### 3. Application Process

**Endpoint:** `POST /v2/fleet/apply`

**Required Fields:**
```json
{
  "tenant_id": 1,
  "fleet_name": "My Fleet",
  "fleet_type": "BUSINESS",
  "documents": [
    {
      "document_type": "AADHAAR",
      "file_url": "https://..."
    }
  ]
}
```

**What Happens:**
1. Validates fleet_type is "BUSINESS"
2. Checks if user already has APPROVED driver profile (rejects if yes)
3. Checks if user already has a fleet (rejects if yes)
4. Validates documents:
   - At least ONE identity document required: **AADHAAR OR PAN**
   - Optional documents: COMPANY_REGISTRATION, BUSINESS_PAN, GST_CERTIFICATE, SIGNED_AGREEMENT
5. Creates ONE row in `fleet` table:
   - `owner_user_id` = current user
   - `tenant_id` = selected tenant
   - `fleet_type` = "BUSINESS"
   - `approval_status` = "PENDING"
   - `status` = "ACTIVE"
6. Creates document rows in `fleet_document` table:
   - `verification_status` = "PENDING"
   - `created_by` = current user

**Response:**
```json
{
  "fleet_id": 123,
  "approval_status": "PENDING"
}
```

---

## 📋 Document Requirements

### Mandatory (At Least ONE Required)
- ✅ **AADHAAR** - Aadhaar card
- ✅ **PAN** - PAN card

### Optional (NOT Enforced in MVP)
- ❌ COMPANY_REGISTRATION - Company registration certificate
- ❌ BUSINESS_PAN - Business PAN card
- ❌ GST_CERTIFICATE - GST registration
- ❌ SIGNED_AGREEMENT - Signed agreement with platform

**Backend validates document types but does NOT reject if optional documents are missing.**

---

## 🔒 Approval Workflow

### Tenant Admin Approval (ONLY Authority)
- **ONLY** tenant admin can approve/reject BUSINESS fleets
- Platform admins **CANNOT** approve fleets
- Users **CANNOT** self-approve

**Approval Actions:**
- **Approve:** `fleet.approval_status = "APPROVED"`
- **Reject:** `fleet.approval_status = "REJECTED"`

---

## 🚫 Post-Approval Access Control

### BEFORE Approval (`approval_status = "PENDING"`)
❌ Fleet owner **CANNOT**:
- Add vehicles
- Upload vehicle documents
- Manage drivers
- Perform any fleet operations

### AFTER Approval (`approval_status = "APPROVED"`)
✅ Fleet owner **CAN**:
- Create vehicles (with mandatory documents: RC, INSURANCE, VEHICLE_PHOTO)
- Upload vehicle documents
- Manage fleet drivers
- View fleet dashboard

**Implementation:** Vehicle creation endpoint validates:
```python
if fleet.approval_status != "APPROVED":
    raise HTTPException(
        status_code=403,
        detail="Fleet is not approved yet"
    )
```

---

## 🛡️ Business Rules Enforced

### Rule 1: Approved Drivers Cannot Become Fleet Owners
```python
if existing_driver and existing_driver.approval_status == "APPROVED":
    raise HTTPException(
        status_code=400,
        detail="Approved drivers cannot apply as BUSINESS fleet owners"
    )
```

### Rule 2: One Fleet Per User
```python
if existing_fleet:
    raise HTTPException(
        status_code=400,
        detail="You already have a fleet application"
    )
```

### Rule 3: Identity Document Mandatory
```python
if not (has_aadhaar or has_pan):
    raise HTTPException(
        status_code=400,
        detail="At least one identity document (AADHAAR or PAN) is required"
    )
```

### Rule 4: Only BUSINESS Type Can Be Applied
```python
if data.fleet_type != "BUSINESS":
    raise HTTPException(
        status_code=400,
        detail="Only BUSINESS fleet type can be applied for"
    )
```

---

## 📊 Database Schema

### `fleet` Table
```sql
fleet_id            BIGINT PRIMARY KEY
tenant_id           BIGINT NOT NULL
owner_user_id       BIGINT NOT NULL
fleet_name          VARCHAR(150) NOT NULL
fleet_type          VARCHAR (BUSINESS/INDIVIDUAL)
approval_status     VARCHAR (PENDING/APPROVED/REJECTED)
status              VARCHAR (ACTIVE/INACTIVE)
created_by          BIGINT
created_on          TIMESTAMP
```

### `fleet_document` Table
```sql
document_id         BIGINT PRIMARY KEY
fleet_id            BIGINT NOT NULL
document_type       VARCHAR(50) NOT NULL
file_url            TEXT NOT NULL
verification_status VARCHAR (PENDING/APPROVED/REJECTED)
verified_by         BIGINT
verified_on         TIMESTAMP
created_by          BIGINT
created_on          TIMESTAMP
```

---

## 🔄 Complete Flow Example

### Step 1: User Applies as Fleet Owner
```bash
POST /v2/fleet/apply
Authorization: Bearer <access_token>

{
  "tenant_id": 1,
  "fleet_name": "ABC Transport",
  "fleet_type": "BUSINESS",
  "documents": [
    {
      "document_type": "AADHAAR",
      "file_url": "https://storage.example.com/aadhaar.pdf"
    },
    {
      "document_type": "PAN",
      "file_url": "https://storage.example.com/pan.pdf"
    }
  ]
}
```

**Result:**
- Fleet row created with `approval_status = PENDING`
- 2 document rows created with `verification_status = PENDING`
- User receives `fleet_id` and `approval_status = PENDING`

### Step 2: Tenant Admin Reviews Application
(Admin dashboard - not implemented in this phase)
- Reviews documents
- Approves or rejects fleet

### Step 3: After Approval
- Fleet owner can now:
  - Create vehicles: `POST /v2/vehicles/create`
  - Upload vehicle documents
  - Manage operations

---

## 🎯 What This Implementation Achieves

✅ **MVP-Ready:**
- Minimal document requirements (identity only)
- No over-engineering with company compliance
- Progressive compliance model

✅ **Production-Aligned:**
- Clear separation of BUSINESS vs INDIVIDUAL fleets
- Proper approval workflow
- Access control before/after approval

✅ **Scalable:**
- Optional documents supported but not enforced
- Easy to add compliance rules later
- Extensible document types

✅ **Secure:**
- Cannot bypass approval status
- One fleet per user
- Approved drivers cannot become fleet owners

---

## 🚫 What Will Never Happen

❌ GST/Business PAN/Company registration required in MVP  
❌ Vehicle creation before approval  
❌ Auto-created fleets without admin approval  
❌ BUSINESS fleets treated same as INDIVIDUAL fleets  
❌ Mixed driver-fleet approval logic  
❌ Platform admin approving fleets  
❌ Users self-approving fleets  

---

## 📝 Testing Checklist

### Positive Cases
- [ ] User with no driver profile can apply as fleet owner with AADHAAR
- [ ] User with no driver profile can apply as fleet owner with PAN
- [ ] User with no driver profile can apply with both AADHAAR and PAN
- [ ] User with optional documents (GST, etc.) can apply successfully
- [ ] After approval, fleet owner can create vehicles

### Negative Cases
- [ ] User with APPROVED driver profile cannot apply as fleet owner
- [ ] User cannot apply without identity document
- [ ] User cannot apply with unknown document types
- [ ] User cannot create vehicles before approval
- [ ] User cannot apply twice (duplicate fleet)
- [ ] User cannot apply with fleet_type != "BUSINESS"

---

## 📂 Files Modified

1. **backend/app/services/fleet_service.py**
   - Added BUSINESS fleet type validation
   - Added identity document validation (AADHAAR OR PAN)
   - Added approved driver rejection policy
   - Explicit fleet_type = "BUSINESS"

2. **backend/app/schemas/fleet.py**
   - Added `fleet_type` field with default "BUSINESS"
   - Documents list validation

3. **backend/app/services/vehicle_service.py**
   - Already validates `approval_status = "APPROVED"` before vehicle creation
   - No changes needed

---

## 🎓 Key Takeaways

This implementation is:
- **Realistic**: Based on actual fleet onboarding processes
- **Production-Ready**: No over-engineering, clear boundaries
- **Extensible**: Easy to add compliance later
- **Secure**: Proper access control and validation

**Next Steps (Not in This Phase):**
- Tenant admin approval UI
- Document verification workflow
- Wallet & payout design
- Fleet driver management
