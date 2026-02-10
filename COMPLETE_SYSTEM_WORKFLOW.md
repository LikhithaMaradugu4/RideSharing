# 🚗 RideSharing Platform - Complete System Workflow

**Last Updated:** February 2026  
**Version:** Phase-2  
**Architecture:** FastAPI Backend + React Frontend (Vite)

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Roles & Capabilities](#roles--capabilities)
3. [Authentication Systems](#authentication-systems)
4. [Detailed Role Workflows](#detailed-role-workflows)
5. [System Architecture](#system-architecture)
6. [Setup & Running Instructions](#setup--running-instructions)
7. [Database Backup & Restore](#database-backup--restore)

---

## 🎯 System Overview

The RideSharing platform is a **multi-tenant ride-sharing system** with distinct authentication flows for regular users (OTP-based) and administrators (email/password). The system manages drivers, riders, fleet owners, and tenant administrators under a platform admin.

### Key Principles:
- **Separation of Concerns**: Users and Admins have completely different auth flows
- **Role-based Capabilities**: Roles (Driver, Fleet Owner) are inferred from data records, not flags
- **Tenant Isolation**: Multi-tenant architecture with tenant admin approval workflows
- **Backend Authority**: Backend is the single source of truth for file validation and approvals

---

## 👥 Roles & Capabilities

### **1. RIDER** 👤
**Status:** Regular User (OTP-based authentication)

**What They Can Do:**
- Create account via phone + OTP
- View available rides
- Request rides
- Track ride in real-time
- Rate drivers after trip completion
- Manage payment methods
- View trip history and receipts
- Manage profile and preferences
- Wallet management

**Entry Point:** Mobile app → Phone number → OTP verification

---

### **2. DRIVER** 🚗
**Status:** Regular User with APPROVED Driver Capability (OTP-based authentication)

**Prerequisites:**
- Must be a registered app user (phone + OTP)
- Must apply for driver role (documents required)
- Must be approved by Tenant Admin

**What They Can Do:**
- Apply for driver role with documents:
  - Driving License (URL)
  - Aadhaar ID (URL)
  - Passport Photo (URL)
  - Alternate phone number
- View application status (Pending/Approved/Rejected)
- Once approved:
  - Access driver dashboard
  - Add vehicles under their INDIVIDUAL fleet (auto-created after approval)
  - Upload vehicle documents (RC, Insurance, Photos)
  - Start/End shifts (Go Online/Offline)
  - Accept/Reject ride requests
  - Track earnings and trips
  - Upload vehicle photos and documents

**Key Constraint:** 
- Driver can only add vehicles in categories allowed by Tenant Admin
- Vehicle categories set based on driving license type
- Cannot add vehicles until approved

**Entry Flow:**
1. Login via phone + OTP (becomes Rider by default)
2. Navigate to "Become Driver"
3. Submit driver application with documents (URLs only)
4. Status: PENDING
5. Wait for Tenant Admin approval
6. Once approved → INDIVIDUAL fleet auto-created
7. Can now add vehicles and go online

---

### **3. FLEET OWNER** 🏢
**Status:** Regular User with Business Fleet Capability (OTP-based authentication)

**Prerequisites:**
- Must be a registered app user (phone + OTP)
- Must apply for fleet owner role
- Must be approved by Tenant Admin

**What They Can Do:**
- Apply as fleet owner (business) with documents:
  - Company registration documents (URLs)
  - Company GST (if applicable)
  - Company address proof
  - Bank account details
- Create a BUSINESS fleet (application pending)
- Manage drivers (add drivers to their fleet)
- Manage vehicles under their fleet
- Track fleet earnings
- View driver performance
- Approve driver documents for vehicles

**Fleet Characteristics:**
- Fleet Type: BUSINESS
- Can manage multiple drivers
- Can add multiple vehicles
- No license-based vehicle category restrictions

**Entry Flow:**
1. Login via phone + OTP
2. Navigate to "Become Fleet Owner"
3. Submit fleet application with company documents
4. Status: PENDING
5. Wait for Tenant Admin approval
6. Once approved → can add vehicles and drivers

---

### **4. TENANT ADMIN** 🧑‍💼
**Status:** Administrator (Email + Password authentication)

**Entry:** Web admin panel → Email + Password (no OTP, no JWT)

**What They Can Do:**
- **Driver Approvals:**
  - View pending driver applications
  - Review uploaded documents
  - Approve/Reject drivers
  - Set allowed vehicle categories per driver
  - Suspend/Reactivate drivers

- **Fleet Approvals:**
  - View pending business fleet applications
  - Review company documents
  - Approve/Reject fleet applications
  - Suspend fleets

- **Vehicle Management:**
  - Review vehicle documents
  - Approve/Reject vehicles
  - Set vehicle status

- **Ride Oversight:**
  - View all rides in tenant
  - Monitor ride metrics
  - Handle disputes

- **User Management:**
  - View all users
  - Manage user accounts
  - Handle complaints

- **Reporting:**
  - View tenant analytics
  - Monitor driver and rider activity
  - Generate reports

**Authentication:** Email + Password (Server-side sessions, no JWT)

---

### **5. PLATFORM ADMIN** 👨‍💻
**Status:** Super Administrator (Email + Password authentication)

**Entry:** Web admin panel → Email + Password (no OTP, no JWT)

**What They Can Do:**
- **Tenant Management:**
  - Create new tenants
  - Configure tenant settings (currency, timezone)
  - View all tenants

- **Tenant Admin Management:**
  - Create tenant admins
  - Assign admins to tenants
  - Manage admin permissions
  - View admin activity logs

- **Platform Oversight:**
  - View all rides across all tenants
  - View all users across all tenants
  - Monitor system health
  - Access audit logs

- **Configuration:**
  - Set platform-wide settings
  - Configure pricing models
  - Manage commissions

**Authentication:** Email + Password (Server-side sessions, no JWT)

**Important:** Platform Admin DOES NOT approve drivers or fleets directly. Only Tenant Admins can approve.

---

## 🔐 Authentication Systems

### **System A: User Authentication (Riders, Drivers, Fleet Owners)**

**Type:** OTP + JWT (Phone-based)  
**Used For:** `/api/v2/*` routes  
**Data Flow:**
1. User enters phone number
2. System sends OTP via SMS
3. User verifies OTP
4. System creates `app_user` record
5. JWT token issued
6. User can now access v2 APIs

**Key Features:**
- Phone number is unique identifier
- Country code extracted from phone
- User created with minimal data (phone, country_code, status)
- User is always a Rider by default
- Capabilities (Driver, Fleet Owner) are inferred from other records
- No app_user.role field used for regular users

**Token Details:**
- Token stored in JWT
- Short-lived tokens with refresh mechanism
- No server-side sessions
- Redis may be used for token blacklisting

---

### **System B: Admin Authentication (Tenant Admin, Platform Admin)**

**Type:** Email + Password + Server-side Sessions  
**Used For:** `/api/admin/*` and `/api/v1/*` routes  
**Data Flow:**
1. Admin enters email and password
2. System validates credentials against `user_auth` table
3. Server creates session
4. Session ID sent via HTTP cookies or X-Session-ID header
5. Session stored in database
6. No JWT, no OTP

**Key Features:**
- Email/password stored with bcrypt hash
- Session-based (like traditional web apps)
- CORS configured for admin origins
- No OTP authentication
- No phone requirement
- Completely separate from user auth system

**Session Details:**
- Session stored in `user_session` table
- Includes login_at, logout_at, ip_address, user_agent
- Server validates session on each request
- Sessions can be invalidated server-side

**Critical:** NEVER mix these two auth systems. They are completely separate.

---

## 📊 Detailed Role Workflows

### **RIDER WORKFLOW**

```
┌─────────────────────────────────────────┐
│   1. User Registration                  │
│   Phone + OTP → app_user created        │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│   2. Rider Dashboard                    │
│   - Search rides                        │
│   - Request ride                        │
│   - Track in real-time                  │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│   3. Ride Completion                    │
│   - Rate driver                         │
│   - Pay via wallet/card                 │
│   - View receipt                        │
└─────────────────────────────────────────┘
```

**Key Endpoints:**
- POST `/api/v2/auth/send-otp` - Send OTP
- POST `/api/v2/auth/verify-otp` - Verify & create user
- GET `/api/v2/me/profile` - View profile
- POST `/api/v2/rides/request` - Request ride
- GET `/api/v2/rides/{trip_id}` - Track ride
- POST `/api/v2/trips/{trip_id}/rate` - Rate driver
- GET `/api/v2/rides/history` - View history

---

### **DRIVER WORKFLOW**

```
┌──────────────────────────────────┐
│   1. Register as User (OTP)      │
│   Becomes Rider by default       │
└────────────┬─────────────────────┘
             ↓
┌──────────────────────────────────┐
│   2. Apply for Driver            │
│   Submit documents:              │
│   - License, Aadhaar, Photo      │
│   - Status: PENDING              │
└────────────┬─────────────────────┘
             ↓
┌──────────────────────────────────┐
│   3. Wait for Tenant Admin       │
│   Tenant Admin reviews docs      │
│   Decision: Approve/Reject       │
└────────────┬─────────────────────┘
             ↓ (Approved)
┌──────────────────────────────────┐
│   4. Auto-Created INDIVIDUAL     │
│   Fleet                          │
│   - fleet_type: INDIVIDUAL       │
│   - approval_status: APPROVED    │
│   - Allowed categories set       │
└────────────┬─────────────────────┘
             ↓
┌──────────────────────────────────┐
│   5. Add Vehicles                │
│   - Upload RC, Insurance, Photos │
│   - Vehicle category must match  │
│     allowed categories           │
│   - Upload documents (URLs only) │
└────────────┬─────────────────────┘
             ↓
┌──────────────────────────────────┐
│   6. Assign Vehicle              │
│   - Select vehicle to use        │
│   - Assign for shift             │
└────────────┬─────────────────────┘
             ↓
┌──────────────────────────────────┐
│   7. Go Online (Start Shift)     │
│   - POST /availability/online    │
│   - driver_shift created         │
│   - Status: ONLINE               │
└────────────┬─────────────────────┘
             ↓
┌──────────────────────────────────┐
│   8. Accept Rides                │
│   - Accept trip from queue       │
│   - Status: BUSY                 │
│   - Pick up rider                │
│   - Complete trip                │
│   - Status: ONLINE (ready again) │
└────────────┬─────────────────────┘
             ↓
┌──────────────────────────────────┐
│   9. Go Offline (End Shift)      │
│   - POST /availability/offline   │
│   - driver_shift.ended_at = now()│
│   - Status: OFFLINE              │
└──────────────────────────────────┘
```

**Key Endpoints:**
- POST `/api/v2/driver/apply` - Apply for driver role
- GET `/api/v2/driver/status` - Check application status
- POST `/api/v2/vehicles/add` - Add vehicle
- POST `/api/v2/vehicles/{id}/documents` - Upload vehicle docs
- POST `/api/v2/driver/vehicle/assign` - Assign vehicle for shift
- POST `/api/v2/driver/availability/online` - Start shift
- POST `/api/v2/driver/availability/offline` - End shift
- GET `/api/v2/driver/trips` - View completed trips
- GET `/api/v2/driver/earnings` - View earnings

---

### **FLEET OWNER WORKFLOW**

```
┌──────────────────────────────────┐
│   1. Register as User (OTP)      │
│   Becomes Rider by default       │
└────────────┬─────────────────────┘
             ↓
┌──────────────────────────────────┐
│   2. Apply for Fleet Owner       │
│   Submit documents:              │
│   - Company registration         │
│   - GST, Bank details            │
│   - Status: PENDING              │
└────────────┬─────────────────────┘
             ↓
┌──────────────────────────────────┐
│   3. Wait for Tenant Admin       │
│   Tenant Admin reviews company   │
│   docs                           │
│   Decision: Approve/Reject       │
└────────────┬─────────────────────┘
             ↓ (Approved)
┌──────────────────────────────────┐
│   4. BUSINESS Fleet Created      │
│   - fleet_type: BUSINESS         │
│   - approval_status: APPROVED    │
│   - Can add vehicles & drivers   │
└────────────┬─────────────────────┘
             ↓
┌──────────────────────────────────┐
│   5. Add Vehicles                │
│   - Multiple vehicles allowed    │
│   - No license restrictions      │
│   - Upload documents             │
│   - Tenant admin reviews         │
└────────────┬─────────────────────┘
             ↓
┌──────────────────────────────────┐
│   6. Manage Drivers              │
│   - Invite drivers to fleet      │
│   - Assign vehicles to drivers   │
│   - Monitor performance          │
│   - View driver earnings         │
└────────────┬─────────────────────┘
             ↓
┌──────────────────────────────────┐
│   7. Monitor Operations          │
│   - Fleet earnings               │
│   - Driver activity              │
│   - Vehicle status               │
│   - Trip analytics               │
└──────────────────────────────────┘
```

**Key Endpoints:**
- POST `/api/v2/fleet/apply` - Apply as fleet owner
- GET `/api/v2/fleet/status` - Check fleet status
- POST `/api/v2/fleet/vehicles` - Add vehicle to fleet
- POST `/api/v2/fleet/drivers` - Invite driver
- GET `/api/v2/fleet/earnings` - View fleet earnings
- GET `/api/v2/fleet/vehicles` - List fleet vehicles
- GET `/api/v2/fleet/drivers` - List fleet drivers

---

### **TENANT ADMIN WORKFLOW**

```
┌────────────────────────────────────┐
│   Admin Login                      │
│   Email + Password                 │
│   (Server-side session created)    │
└──────────────┬─────────────────────┘
               ↓
┌────────────────────────────────────┐
│   Admin Dashboard                  │
│   - View pending approvals         │
│   - View users & drivers           │
│   - View rides                     │
└──────────────┬─────────────────────┘
               ↓
┌────────────────────────────────────┐
│   Driver Approval Workflow         │
│   - List pending drivers           │
│   - Review documents               │
│   - Approve & set categories       │
│   OR Reject with reason            │
│   → Auto-creates INDIVIDUAL fleet  │
└──────────────┬─────────────────────┘
               ↓
┌────────────────────────────────────┐
│   Fleet Approval Workflow          │
│   - List pending fleets            │
│   - Review company docs            │
│   - Approve BUSINESS fleet         │
│   OR Reject                        │
└──────────────┬─────────────────────┘
               ↓
┌────────────────────────────────────┐
│   Vehicle Document Review          │
│   - Review vehicle papers          │
│   - Approve vehicle                │
│   OR Request changes               │
└──────────────┬─────────────────────┘
               ↓
┌────────────────────────────────────┐
│   Ongoing Monitoring               │
│   - View all rides                 │
│   - Monitor drivers & fleets       │
│   - Handle disputes                │
│   - View analytics                 │
└────────────────────────────────────┘
```

**Key Endpoints:**
- GET `/api/admin/drivers/pending` - Pending drivers
- POST `/api/admin/drivers/{id}/approve` - Approve driver
- POST `/api/admin/drivers/{id}/reject` - Reject driver
- GET `/api/admin/fleets/pending` - Pending fleets
- POST `/api/admin/fleets/{id}/approve` - Approve fleet
- GET `/api/admin/vehicles/pending` - Pending vehicles
- GET `/api/admin/users` - List all users
- GET `/api/admin/rides` - List all rides
- GET `/api/admin/analytics` - View analytics

---

### **PLATFORM ADMIN WORKFLOW**

```
┌────────────────────────────────────┐
│   Super Admin Login                │
│   Email + Password                 │
│   (Server-side session created)    │
└──────────────┬─────────────────────┘
               ↓
┌────────────────────────────────────┐
│   Platform Admin Dashboard         │
│   - View all tenants               │
│   - View all users/rides           │
│   - Manage admins                  │
└──────────────┬─────────────────────┘
               ↓
┌────────────────────────────────────┐
│   Tenant Management                │
│   - Create new tenant              │
│   - Configure tenant settings      │
│     (currency, timezone)           │
│   - Update tenant status           │
└──────────────┬─────────────────────┘
               ↓
┌────────────────────────────────────┐
│   Admin Management                 │
│   - Create tenant admin            │
│   - Assign admin to tenant         │
│   - Manage admin permissions       │
│   - View admin activity            │
└──────────────┬─────────────────────┘
               ↓
┌────────────────────────────────────┐
│   Platform Oversight               │
│   - View system metrics            │
│   - Access audit logs              │
│   - Configure commissions          │
│   - Manage pricing tiers           │
└────────────────────────────────────┘
```

**Key Endpoints:**
- POST `/api/admin/tenants` - Create tenant
- GET `/api/admin/tenants` - List tenants
- POST `/api/admin/admins` - Create tenant admin
- GET `/api/admin/admins` - List admins
- GET `/api/admin/users` - View all users (all tenants)
- GET `/api/admin/analytics` - Platform analytics

**Important:** Platform Admin delegates driver/fleet approval to Tenant Admins.

---

## 🏗️ System Architecture

### **Database Model (Core Entities)**

```
app_user (Identity)
├── user_id (PK)
├── phone (unique)
├── email (unique)
├── full_name
├── role (RIDER | DRIVER | FLEET_OWNER | PLATFORM_ADMIN | TENANT_ADMIN)
├── country_code (FK → country)
├── city_id (FK → city)
├── status

driver_profile (Driver Capability)
├── driver_id (PK, FK → app_user)
├── approval_status (PENDING | APPROVED | REJECTED | SUSPENDED)
├── allowed_vehicle_categories (JSON array)

fleet (Vehicle Ownership Unit)
├── fleet_id (PK)
├── owner_user_id (FK → app_user)
├── tenant_id (FK → tenant)
├── fleet_type (INDIVIDUAL | BUSINESS)
├── approval_status (APPROVED | PENDING | REJECTED)
├── name (nullable, required for BUSINESS)

vehicle (Vehicles in Fleet)
├── vehicle_id (PK)
├── fleet_id (FK → fleet)
├── vehicle_type
├── vehicle_category (BIKE | AUTO | CAR | SUV)
├── registration_number
├── approval_status

driver_vehicle_assignment (Active Assignment)
├── assignment_id (PK)
├── driver_id (FK → driver_profile)
├── vehicle_id (FK → vehicle)
├── assigned_at
├── end_time (NULL = active)

driver_shift (Online Sessions)
├── shift_id (PK)
├── driver_id (FK → driver_profile)
├── status (ONLINE | BUSY | OFFLINE)
├── started_at
├── ended_at (NULL = active shift)

user_kyc (Driver Documents)
├── kyc_id (PK)
├── user_id (FK → app_user)
├── document_type (DRIVING_LICENSE | AADHAAR | PASSPORT_PHOTO)
├── document_number
├── file_url
├── verification_status

trip (Rides)
├── trip_id (PK)
├── rider_id (FK → app_user)
├── driver_id (FK → driver_profile)
├── status (REQUESTED | ACCEPTED | COMPLETED | CANCELLED)
├── pickup_location
├── dropoff_location
├── amount

tenant (Multi-tenancy)
├── tenant_id (PK)
├── tenant_code
├── name
├── default_currency
├── default_timezone

user_session (Admin Sessions)
├── session_id (PK)
├── user_id (FK → app_user)
├── login_at
├── logout_at
├── ip_address
```

### **API Architecture**

```
Backend: FastAPI
├── /api/v1/*                    (Legacy Phase-1, session-based)
├── /api/v2/*                    (Phase-2, JWT + OTP)
│   ├── /auth                    (OTP login)
│   ├── /driver                  (Driver operations)
│   ├── /fleet                   (Fleet operations)
│   ├── /vehicles                (Vehicle management)
│   ├── /rides                   (Ride requests)
│   ├── /trips                   (Trip management)
│   ├── /profile                 (User profile)
│   └── /me                      (Current user)
└── /api/admin/*                 (Admin APIs, session-based)
    ├── /drivers                 (Driver approvals)
    ├── /fleets                  (Fleet approvals)
    ├── /vehicles                (Vehicle approvals)
    ├── /tenants                 (Tenant management)
    └── /admins                  (Admin management)

Frontend: React + Vite
├── src/
│   ├── components/              (Shared UI components)
│   ├── services/                (API client)
│   ├── app/                     (Rider routes)
│   ├── admin/                   (Admin panel routes)
│   └── assets/                  (Static assets)
```

### **Key Design Decisions**

1. **No User Roles Table:** Driver/Fleet owner capabilities are inferred from existence of records
2. **Auto-created Individual Fleet:** Created by system when driver is approved, not by user
3. **Backend File Validation:** Frontend uploads to object storage, backend only stores URLs
4. **Session-based Admin Auth:** Uses traditional cookie/session model for admins
5. **Separated Auth Flows:** Users and admins never share authentication logic
6. **Tenant Isolation:** All data queries filtered by tenant
7. **Single Active Shift:** DB constraint ensures only one active shift per driver

---

## 🚀 Setup & Running Instructions

### **Prerequisites**

**System Requirements:**
- PostgreSQL 12+ (database)
- Python 3.9+
- Node.js 16+
- Redis (optional, for token blacklisting)
- Linux/macOS/Windows with bash

**Required Files:**
- Database backup: `ridesharing_fulldump.backup` (one backup file assumed)

---

### **1. Backend Setup**

#### **Step 1: Navigate to Backend**
```bash
cd /home/likhitha.maradugu/Downloads/RideSharing\ \(Jan\ 14\)\ \(2\)/RideSharing\ \(Jan\ 14\)/RideSharing\ \(Jan\ 14\)/backend
```

#### **Step 2: Create Virtual Environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### **Step 3: Install Dependencies**
```bash
pip install -r ../requirements.txt
```

#### **Step 4: Configure Database Connection**

Edit `app/core/config.py`:
```python
DATABASE_URL = "postgresql://username:password@localhost:5432/ridesharing"
```

Or set environment variable:
```bash
export DATABASE_URL="postgresql://username:password@localhost:5432/ridesharing"
```

#### **Step 5: Start Backend Server**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
INFO: 
    POST   http://localhost:8000/api/v2/auth/send-otp
    GET    http://localhost:8000/api/v2/me/profile
    POST   http://localhost:8000/api/admin/drivers
```

**Verify Backend is Running:**
```bash
curl http://localhost:8000/docs  # Swagger UI
curl http://localhost:8000/openapi.json  # OpenAPI spec
```

---

### **2. Frontend Setup**

#### **Step 1: Navigate to Frontend**
```bash
cd /home/likhitha.maradugu/Downloads/RideSharing\ \(Jan\ 14\)\ \(2\)/RideSharing\ \(Jan\ 14\)/RideSharing\ \(Jan\ 14\)/frontend-v2
```

#### **Step 2: Install Dependencies**
```bash
npm install
```

#### **Step 3: Start Development Server**
```bash
npm run dev
```

**Expected Output:**
```
  VITE v7.2.4  ready in 145 ms

  ➜  Local:   http://localhost:5173/
  ➜  press h to show help
```

**Access Frontend:** Open browser → `http://localhost:5173`

---

### **3. Database Setup**

#### **Step 1: Create PostgreSQL Database**

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Inside psql:
CREATE DATABASE ridesharing;
CREATE USER ridesharing_user WITH PASSWORD 'your_secure_password';
ALTER ROLE ridesharing_user SET client_encoding TO 'utf8';
ALTER ROLE ridesharing_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE ridesharing_user SET default_transaction_deferrable TO on;
ALTER ROLE ridesharing_user SET default_timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE ridesharing TO ridesharing_user;

\q  # Exit psql
```

#### **Step 2: Restore Database from Backup**

See [Database Backup & Restore](#database-backup--restore) section below.

---

### **4. Redis (Optional)**

If using Redis for token management:

```bash
# Start Redis server
redis-server

# Or using Docker
docker run -d -p 6379:6379 redis:7-alpine
```

---

### **Complete Startup Checklist**

```
✓ PostgreSQL running on port 5432
✓ Database 'ridesharing' created
✓ Backend virtual environment activated
✓ Backend dependencies installed
✓ Backend running on http://localhost:8000
✓ Frontend dependencies installed
✓ Frontend running on http://localhost:5173
✓ Redis running on port 6379 (optional)
✓ CORS configured (localhost:3000, 5173, 5174)
```

---

## 💾 Database Backup & Restore

### **Database Backup File**
**Location:** `/home/likhitha.maradugu/Downloads/RideSharing(Jan 14) (2)/RideSharing(Jan 14)/RideSharing(Jan 14)/ridesharing_fulldump.backup`

---

### **Restore Database from Backup**

#### **Method 1: Using pg_restore (Recommended)**

```bash
# Ensure PostgreSQL is running
# Database must exist (created in step 1 above)

# Navigate to backup file location
cd /home/likhitha.maradugu/Downloads/RideSharing\ \(Jan\ 14\)\ \(2\)/RideSharing\ \(Jan\ 14\)/RideSharing\ \(Jan\ 14\)

# Restore the backup
pg_restore --username=ridesharing_user \
           --dbname=ridesharing \
           --verbose \
           ridesharing_fulldump.backup

# You may be prompted for password
# Enter: your_secure_password
```

**Expected Output:**
```
pg_restore: connecting to database for restore
pg_restore: processing schema
pg_restore: processing data
pg_restore: executing DOMAIN...
pg_restore: executing SCHEMA...
...
pg_restore: completed successfully
```

#### **Method 2: Using psql (If backup is SQL format)**

```bash
psql --username=ridesharing_user \
     --dbname=ridesharing \
     < ridesharing_fulldump.backup
```

#### **Method 3: Using Docker (If PostgreSQL in Docker)**

```bash
# First, copy backup into Docker container
docker cp ridesharing_fulldump.backup postgres_container:/tmp/

# Then restore inside container
docker exec postgres_container pg_restore \
    --username=ridesharing_user \
    --dbname=ridesharing \
    --verbose \
    /tmp/ridesharing_fulldump.backup
```

---

### **Verify Backup Restoration**

```bash
# Connect to database
psql --username=ridesharing_user --dbname=ridesharing

# Inside psql:
\dt                    # List all tables
\d app_user            # Describe app_user table
SELECT COUNT(*) FROM app_user;  # Count users
SELECT COUNT(*) FROM trip;      # Count trips

\q  # Exit
```

**Expected Output:**
```
               List of relations
 Schema |           Name            | Type  | Owner
--------+---------------------------+-------+------------------
 public | app_user                  | table | ridesharing_user
 public | trip                      | table | ridesharing_user
 public | driver_profile            | table | ridesharing_user
 public | fleet                     | table | ridesharing_user
 ...
```

---

### **Create New Backup**

```bash
# Navigate to backup location
cd /home/likhitha.maradugu/Downloads/RideSharing\ \(Jan\ 14\)\ \(2\)/RideSharing\ \(Jan\ 14\)/RideSharing\ \(Jan\ 14\)

# Create backup with timestamp
pg_dump --username=ridesharing_user \
        --dbname=ridesharing \
        --format=custom \
        > ridesharing_fulldump_$(date +%Y%m%d_%H%M%S).backup

# Or keep it simple
pg_dump --username=ridesharing_user \
        --dbname=ridesharing \
        --format=custom \
        > ridesharing_fulldump.backup
```

---

### **Backup File Information**

| Property | Value |
|----------|-------|
| **Format** | Binary (pg_restore format) or SQL |
| **Location** | Project root directory |
| **Size** | Varies (typically 50-200 MB) |
| **Compression** | Built-in to format |
| **Tables Included** | All tables, sequences, views, triggers |
| **Restore Time** | 2-5 minutes (depends on size) |

---

## 🔑 Default Admin Credentials Setup

After restoring database, create platform admin:

```bash
# Connect to database
psql --username=ridesharing_user --dbname=ridesharing

# Insert platform admin
INSERT INTO app_user (user_id, full_name, email, phone, country_code, role, status)
VALUES (1, 'Platform Admin', 'admin@ridesharing.com', '+1234567890', 'US', 'PLATFORM_ADMIN', 'ACTIVE');

INSERT INTO user_auth (user_id, password_hash, is_locked)
VALUES (1, '$2b$12$...hash_here...', false);

\q
```

**Generate password hash in Python:**
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hash = pwd_context.hash("your_admin_password")
print(hash)
```

---

## 🎯 Testing the System

### **Test User Registration (OTP Flow)**

```bash
# 1. Send OTP
curl -X POST "http://localhost:8000/api/v2/auth/send-otp" \
  -H "Content-Type: application/json" \
  -d '{"phone": "+1234567890", "country_code": "US"}'

# Expected Response:
# {"message": "OTP sent", "request_id": "..."}

# 2. Verify OTP (simulate with any 4-digit code in dev mode)
curl -X POST "http://localhost:8000/api/v2/auth/verify-otp" \
  -H "Content-Type: application/json" \
  -d '{"phone": "+1234567890", "request_id": "...", "otp": "1234"}'

# Expected Response:
# {"access_token": "eyJ0eXAi...", "token_type": "bearer", "user": {...}}
```

### **Test Admin Login**

```bash
curl -X POST "http://localhost:8000/api/admin/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@ridesharing.com", "password": "your_admin_password"}'

# Expected Response:
# {"session_id": "...", "user": {...}}
```

### **Test Driver Apply**

```bash
# Get JWT token from OTP verification first, then:

curl -X POST "http://localhost:8000/api/v2/driver/apply" \
  -H "Authorization: Bearer {JWT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "driving_license_number": "DL123456",
    "driving_license_url": "https://...",
    "aadhaar_number": "123456789012",
    "aadhaar_url": "https://...",
    "passport_photo_url": "https://...",
    "alternate_phone_number": "+1987654321"
  }'

# Expected Response:
# {"driver_id": 1, "approval_status": "PENDING", "message": "Application submitted"}
```

---

## 📚 Quick Reference

### **Important Endpoints**

| Endpoint | Method | Purpose | Auth |
|----------|--------|---------|------|
| `/api/v2/auth/send-otp` | POST | Send OTP to phone | None |
| `/api/v2/auth/verify-otp` | POST | Verify OTP & login | None |
| `/api/v2/driver/apply` | POST | Apply as driver | JWT |
| `/api/v2/fleet/apply` | POST | Apply as fleet owner | JWT |
| `/api/v2/vehicles/add` | POST | Add vehicle | JWT |
| `/api/v2/driver/availability/online` | POST | Start shift | JWT |
| `/api/v2/driver/availability/offline` | POST | End shift | JWT |
| `/api/admin/drivers/pending` | GET | View pending drivers | Session |
| `/api/admin/drivers/{id}/approve` | POST | Approve driver | Session |
| `/api/admin/fleets/pending` | GET | View pending fleets | Session |
| `/api/admin/tenants` | POST | Create tenant | Session |

### **File Structure**

```
backend/
├── app/
│   ├── main.py                  (FastAPI entry point)
│   ├── api/
│   │   ├── v1/                  (Phase-1 routes)
│   │   ├── v2/                  (Phase-2 routes)
│   │   └── admin/               (Admin routes)
│   ├── models/                  (SQLAlchemy models)
│   ├── schemas/                 (Pydantic schemas)
│   ├── services/                (Business logic)
│   ├── core/
│   │   ├── config.py            (Configuration)
│   │   ├── database.py          (DB connection)
│   │   └── commission_config.py (Pricing config)
│   └── db/                      (Database utilities)
├── requirements.txt             (Python dependencies)
└── .env                         (Environment variables)

frontend-v2/
├── src/
│   ├── main.jsx                 (Entry point)
│   ├── App.jsx                  (Router)
│   ├── services/                (API client)
│   ├── components/              (React components)
│   ├── admin/                   (Admin pages)
│   ├── app/                     (User pages)
│   └── assets/                  (Images, CSS)
├── package.json                 (Dependencies)
├── vite.config.js               (Vite config)
└── index.html                   (HTML entry)
```

### **Environment Variables**

**Backend (.env):**
```bash
DATABASE_URL=postgresql://ridesharing_user:password@localhost:5432/ridesharing
REDIS_URL=redis://localhost:6379/0
JWT_SECRET=your_jwt_secret_key_here
JWT_ALGORITHM=HS256
OTP_EXPIRY=300  # 5 minutes
SMS_API_KEY=your_sms_api_key
```

**Frontend (.env):**
```bash
VITE_API_URL=http://localhost:8000
VITE_MAPS_API_KEY=your_google_maps_key
```

---

## 🔗 System Flow Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                    RIDESHARING PLATFORM                        │
└────────────────────────────────────────────────────────────────┘

USERS (OTP + JWT)
├── Rider
│   ├── Request ride
│   ├── Track in real-time
│   └── Rate & pay
│
├── Driver
│   ├── Apply (pending)
│   ├── [Tenant Admin Approval]
│   ├── Add vehicles
│   ├── Go online (start shift)
│   ├── Accept rides
│   └── Go offline (end shift)
│
└── Fleet Owner
    ├── Apply (pending)
    ├── [Tenant Admin Approval]
    ├── Add vehicles
    ├── Manage drivers
    └── Track earnings

ADMINS (Email + Password + Sessions)
├── Tenant Admin
│   ├── Approve drivers
│   ├── Set vehicle categories
│   ├── Approve fleets & vehicles
│   ├── View all rides/users
│   └── Handle disputes
│
└── Platform Admin
    ├── Create tenants
    ├── Create tenant admins
    ├── View all data
    └── Manage settings

DATABASE (PostgreSQL)
├── app_user (identity)
├── driver_profile (driver capability)
├── fleet (vehicle ownership)
├── vehicle (vehicles)
├── trip (rides)
├── driver_shift (online sessions)
└── [50+ tables]

EXTERNAL SERVICES
├── SMS Gateway (OTP)
├── Object Storage (Files)
├── Payment Gateway (Transactions)
└── Maps API (Location)
```

---

## ✅ Troubleshooting

### **Backend Issues**

**Error: "Cannot connect to database"**
```bash
# Check PostgreSQL is running
sudo service postgresql status

# Check DATABASE_URL is correct
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL
```

**Error: "ModuleNotFoundError"**
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Activate virtual environment
source venv/bin/activate
```

**Error: "CORS error"**
- Check frontend URL is in `CORSMiddleware` allowed_origins
- Ensure backend is running on correct port
- Clear browser cache

### **Frontend Issues**

**Error: "Cannot reach http://localhost:8000"**
```bash
# Check backend is running
curl http://localhost:8000/docs

# Check VITE_API_URL in .env
cat .env | grep VITE_API_URL
```

**Error: "npm: command not found"**
```bash
# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### **Database Issues**

**Error: "FATAL: role 'ridesharing_user' does not exist"**
```bash
# Create the role
sudo -u postgres createuser ridesharing_user --password

# Grant privileges
sudo -u postgres psql -c "ALTER USER ridesharing_user CREATEDB;"
```

**Error: "Restore fails"**
```bash
# Drop existing database
dropdb --username=ridesharing_user ridesharing

# Recreate database
createdb --username=ridesharing_user ridesharing

# Restore again
pg_restore --username=ridesharing_user --dbname=ridesharing ridesharing_fulldump.backup
```

---

## 📞 Support & Documentation

- **FastAPI Docs:** http://localhost:8000/docs (Swagger UI)
- **OpenAPI Spec:** http://localhost:8000/openapi.json
- **Frontend:** http://localhost:5173
- **PostgreSQL Docs:** https://www.postgresql.org/docs/
- **Vite Docs:** https://vitejs.dev

---

**End of Complete System Workflow Document**

*Generated: February 2026*  
*Version: Phase-2 (Multi-tenant, OTP + Admin Auth)*

