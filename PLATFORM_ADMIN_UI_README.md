# Platform Admin UI - Implementation Guide

## Overview

This is a complete Platform Admin UI implementation for the RideSharing platform. It includes both backend APIs and a React-based frontend for managing tenants, tenant admins, and documents.

## Features Implemented

### Backend APIs (FastAPI)
- ✅ Admin Authentication (Session-based with cookies)
- ✅ Tenant Management (CRUD operations)
- ✅ Primary Tenant Admin Creation
- ✅ Tenant Document Management (Upload, List, Download, Delete)
- ✅ Platform Admin & Tenant Admin role separation

### Frontend (React + Vite)
- ✅ Admin Login Screen
- ✅ Auth Guard with session validation
- ✅ Clean Admin Layout (Sidebar, Header)
- ✅ Tenants List with actions
- ✅ Create Tenant Form
- ✅ Tenant Details Page
- ✅ Tenant Admin Management
- ✅ Document Upload/Download Interface
- ✅ Professional UI with clean styling

## Project Structure

```
backend/app/api/admin/
├── auth.py              # Admin authentication endpoints
├── tenants.py           # Tenant CRUD operations
├── documents.py         # Document management
├── drivers.py           # Existing tenant admin features
├── fleets.py           # Existing tenant admin features
└── vehicles.py         # Existing tenant admin features

frontend-v2/src/
├── admin/
│   ├── auth/
│   │   ├── AdminLogin.jsx
│   │   └── AdminAuthGuard.jsx
│   ├── layout/
│   │   ├── AdminLayout.jsx
│   │   ├── AdminSidebar.jsx
│   │   └── AdminHeader.jsx
│   └── platform-admin/
│       ├── TenantsList.jsx
│       ├── TenantCreate.jsx
│       ├── TenantDetails.jsx
│       ├── TenantAdmins.jsx
│       └── TenantDocuments.jsx
└── services/
    └── admin.service.js
```

## Setup Instructions

### Backend Setup

1. **Database Setup**
   Make sure your database has the following tables (they should already exist):
   - `tenant`
   - `tenant_admin`
   - `tenant_document`
   - `app_user`
   - `user_auth`
   - `user_session`
   - `lu_tenant_role` (with 'PLATFORM_ADMIN' and 'TENANT_ADMIN' roles)

2. **Create a Platform Admin User**
   
   Run this SQL to create a platform admin account:
   
   ```sql
   -- Insert Platform Admin user
   INSERT INTO app_user (full_name, email, country_code, role, status, created_on, updated_on)
   VALUES ('Platform Admin', 'admin@rideshare.com', 'US', 'PLATFORM_ADMIN', 'ACTIVE', NOW(), NOW());

   -- Get the user_id (replace with actual ID from above insert)
   -- Then insert auth credentials (password: admin123)
   INSERT INTO user_auth (user_id, password_hash, is_locked, created_on, updated_on)
   VALUES (1, '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5tdcZxquAE5Eq', false, NOW(), NOW());
   ```
   
   Default Credentials:
   - Email: `admin@rideshare.com`
   - Password: `admin123`

3. **Start Backend Server**
   ```bash
   cd backend
   uvicorn app.main:app --reload --port 8000
   ```

### Frontend Setup

1. **Install Dependencies**
   ```bash
   cd frontend-v2
   npm install
   ```

2. **Start Development Server**
   ```bash
   npm run dev
   ```
   
   Frontend will run on http://localhost:3000

## API Endpoints

### Authentication
- `POST /api/admin/auth/login` - Admin login
- `GET /api/admin/auth/me` - Get current admin info
- `POST /api/admin/auth/logout` - Logout

### Tenant Management (Platform Admin Only)
- `GET /api/admin/tenants` - List all tenants
- `POST /api/admin/tenants` - Create tenant
- `GET /api/admin/tenants/{id}` - Get tenant details
- `DELETE /api/admin/tenants/{id}` - Delete tenant

### Tenant Admin Management (Platform Admin Only)
- `POST /api/admin/tenants/{id}/admins` - Create primary tenant admin
- `GET /api/admin/tenants/{id}/admins` - Get primary tenant admin

### Document Management (Platform Admin Only)
- `GET /api/admin/tenants/{id}/documents` - List documents
- `POST /api/admin/tenants/{id}/documents` - Upload document
- `GET /api/admin/tenants/{id}/documents/{doc_id}/download` - Download document
- `DELETE /api/admin/tenants/{id}/documents/{doc_id}` - Delete document

## User Flows

### Platform Admin Flow

1. **Login** → Navigate to http://localhost:3000/admin/login
2. **View Tenants** → Automatically redirected to tenants list
3. **Create Tenant** → Click "Create Tenant" button
   - Enter tenant name, currency, timezone
   - Submit to create
4. **View Tenant Details** → Click "View Details" on any tenant
5. **Add Tenant Admin** → Click "Create Admin" button
   - Enter email and optional full name
   - Auto-generates password: [email username]123
6. **Upload Documents** → Click "Manage Documents"
   - Select document type
   - Upload file
   - View, download, or delete documents

### Tenant Admin Flow (Future)
- Will have separate dashboard
- Can manage drivers, fleets, vehicles
- Limited to their tenant's data only

## Security Features

- ✅ Session-based authentication with HTTP-only cookies
- ✅ Role-based access control (Platform Admin vs Tenant Admin)
- ✅ Backend validates admin privileges on every request
- ✅ Frontend adapts UI based on admin type
- ✅ No role/permission flags stored in frontend
- ✅ Automatic session expiration (7 days)

## Design Principles

1. **API-First**: All data comes from backend APIs, no mocked data
2. **Backend Authority**: Backend decides admin type and permissions
3. **Clean UI**: Professional styling with consistent design
4. **Session-Based**: No JWT tokens, uses HTTP-only cookies
5. **Role Separation**: Platform Admin and Tenant Admin have different access

## Testing the System

### Test Scenario 1: Create Complete Tenant Setup

1. Login as Platform Admin
2. Create new tenant "Test Taxi Company"
3. View tenant details
4. Create primary admin with email `testadmin@taxi.com`
5. Upload company registration document
6. Verify all data is stored correctly

### Test Scenario 2: Document Management

1. Upload multiple document types
2. Download a document
3. Delete a document
4. Verify document count updates

### Test Scenario 3: Admin Authentication

1. Logout from platform admin
2. Login with tenant admin credentials
3. Verify different sidebar/dashboard
4. Try to access platform admin routes (should redirect)

## Configuration

### Backend Configuration
- Database: Configure in `backend/app/core/database.py`
- CORS: Already configured for `http://localhost:3000`
- Upload Directory: `/tmp/tenant_documents` (change in `documents.py`)

### Frontend Configuration
- API Base URL: `http://localhost:8000/api/admin` (in `admin.service.js`)
- Vite Proxy: Configured to proxy `/api` to backend

## Troubleshooting

### CORS Issues
- Ensure backend CORS middleware allows `http://localhost:3000`
- Check credentials are set to `true` in CORS config

### Session Not Persisting
- Ensure cookies are being set with `httponly=True`
- Check browser allows cookies from localhost
- Verify `credentials: 'include'` in fetch calls

### File Upload Fails
- Check upload directory exists and has write permissions
- Verify file size limits in backend
- Check Content-Type in upload request

### 403 Forbidden Errors
- Verify user has correct role (PLATFORM_ADMIN)
- Check session is valid
- Ensure admin_session_id cookie is being sent

## Next Steps

To extend this implementation:

1. **Add Tenant Admin Dashboard**
   - Create dedicated pages for tenant admin features
   - Integrate existing driver/fleet management
   
2. **Add Tenant Metrics**
   - Show rider count, driver count, trip count
   - Add analytics dashboard

3. **Enhanced Document Verification**
   - Add approval workflow
   - Add document expiry tracking

4. **Audit Logs**
   - Track all admin actions
   - Add activity history

5. **Email Notifications**
   - Send credentials to new tenant admins
   - Notify on important events

## Non-Negotiable Rules (Followed)

✅ Frontend NEVER decides admin type
✅ Frontend NEVER stores role flags  
✅ Frontend NEVER mocks data
✅ Backend is source of truth
✅ Session-based auth only (no JWT in admin)
✅ Simple text sidebar (no icons)
✅ API-first approach

## Completion Checklist

✅ Platform admin can login
✅ See all tenants
✅ Create a tenant
✅ Add primary tenant admin
✅ Upload tenant documents
✅ Delete tenant
✅ Professional, clean UI
✅ All APIs working and integrated
✅ Session-based authentication
✅ Role-based access control

---

## Support

For questions or issues, refer to:
- Backend API docs: http://localhost:8000/docs
- Frontend console for debug logs
- Network tab for API call inspection
