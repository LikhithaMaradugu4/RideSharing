# RideSharing

One-line description: A backend-driven ride-sharing system with REST APIs and a React Vite frontend.

## Overview

- Problem: Implements core ride-hailing operations (user auth, trip lifecycle, driver onboarding, tenant and platform administration) for a multi-tenant ridesharing deployment.
- Users: Riders, Drivers, Tenant administrators, Platform administrators.
- Core idea: FastAPI backend (REST) with multi-tenant data models, OTP+JWT authentication, Redis-backed session artifacts, and a React + Vite frontend.

## Features

- Rider
  - OTP-based login (send/verify OTP). (JWT access + refresh tokens)
  - Create trip requests, get trip status, cancel trip.
  - Fare estimate and location validation.
  - Retrieve payment information for trips.

- Driver
  - List available tenants for application.
  - Apply with document uploads and create KYC records (file uploads saved under `uploads/driver_documents`).
  - View application status, re-upload rejected documents, resubmit application.
  - Go online/offline (driver shift management) and shift readiness checks.

- Tenant Admin
  - View driver applications and application details.
  - Approve or reject driver applications and update related KYC records.
  - Download driver documents (secured endpoint).

- Platform Admin
  - Create/list tenants and tenant details.
  - Assign tenant admins and upload tenant documents.
  - Manage countries, cities, fare configurations, and commission configurations.

- System
  - Backend: FastAPI application with SQLAlchemy models; creates tables at startup (`Base.metadata.create_all`).
  - Database: PostgreSQL (psycopg2 used in code). Connection configured in `backend/app/core/database.py`.
  - Caching / stores: Redis used for OTP and refresh-token storage/blacklisting.
  - Auth: OTP-based login, JWT access and refresh tokens; refresh tokens persisted in Redis.
  - Payments/settlement: Cash-only payment flow; confirming cash creates ledger entries, updates driver wallet and applies blocking rules if negative limits are exceeded.

## Tech Stack

- Backend:
  - Language: Python
  - Framework: FastAPI
  - ORM: SQLAlchemy
  - Database: PostgreSQL (via `psycopg2-binary`)
  - Auth: JWT (PyJWT) with OTP flow (Redis-backed stores)
  - Caching/Stores: Redis

- Frontend:
  - Framework/library: React
  - Tooling: Vite
  - API communication: REST (backend exposes JSON HTTP endpoints)

## Architecture Summary

- The backend exposes REST APIs (FastAPI) grouped under Phase-2 `api/v2` (JWT-based) and earlier routers. On startup the SQLAlchemy models are created if absent.
- Authentication uses an OTP-first flow: OTPs are stored in Redis, verified, then the server issues JWT access and refresh tokens. Refresh tokens are persisted/validated via Redis; access tokens can be blacklisted on logout.
- Multi-tenancy is represented in the data model (tenant entities and `tenant_id` fields). Platform admin routes manage tenants; many domain objects are scoped to tenant IDs.
- Transaction/settlement flow: the system uses a cash-only policy. When drivers confirm cash payment the service records commission DEBIT ledger entries for drivers, CREDIT entries for platform/tenant/fleet ledgers, updates driver wallet balance (which may go negative), and applies blocking rules when limits are exceeded.

## Project Structure

- `backend/` — Python backend package (FastAPI app): application code, API routers, models, services, and core utilities.
  - `backend/app/main.py` — FastAPI app entrypoint.
  - `backend/app/api/v2/` — Phase-2 JWT-protected API routers (auth, trip, driver, tenant_admin, platform_admin, payments, financial, etc.).
  - `backend/app/core/` — config, DB connection, Redis clients and settings.
  - `backend/app/models/` — SQLAlchemy models (identity, trips, ledger, fleet, vehicle, etc.).
  - `backend/app/services/` — domain services (trip, dispatch, pricing, payment, ledger, etc.).
- `frontend-v2/` — React + Vite frontend.
- `requirements.txt` — Python dependencies.
- `Edits_in_sql.sql` — database DDL/edits used by the project.

## Setup Instructions

Prerequisites

- Python 3.10+ (compatible with listed dependencies)
- PostgreSQL instance
- Redis instance
- Node.js (for frontend) and `npm`

Backend

1. From repository root, install Python dependencies:

```bash
pip install -r requirements.txt
```

2. Configure environment variables (or place them in a `.env` file in the backend root). Important variables used by the code:

```text
DATABASE_URL           # e.g. postgresql://user:pass@host:5432/dbname
REDIS_HOST             # default: localhost
REDIS_PORT             # default: 6379
REDIS_DB               # default: 0
REDIS_PASSWORD         # if applicable
JWT_SECRET_KEY         # secret for signing JWTs
SHOW_OTP_IN_LOG        # optional: 'true' to print OTPs during development
```

3. Run the backend (from repository root):

```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend

1. Change to the frontend folder and install dependencies:

```bash
cd frontend-v2
npm install
```

2. Run the dev server:

```bash
npm run dev
```

## Author

Likhitha Maradugu

B.Tech CSE
Curently Doing internship at TechVedika
Rajiv Gandhi University of Knowledge Technologies
