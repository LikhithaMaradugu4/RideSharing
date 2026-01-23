import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import AdminLogin from './admin/auth/AdminLogin';
import AdminAuthGuard from './admin/auth/AdminAuthGuard';
import AdminLayout from './admin/layout/AdminLayout';
import TenantsList from './admin/platform-admin/TenantsList';
import TenantCreate from './admin/platform-admin/TenantCreate';
import TenantDetails from './admin/platform-admin/TenantDetails';
import TenantAdmins from './admin/platform-admin/TenantAdmins';
import TenantDocuments from './admin/platform-admin/TenantDocuments';
import './App.css';

interface AdminData {
  user_id: number;
  full_name: string;
  email: string;
  admin_type: 'PLATFORM' | 'TENANT';
  tenant_id?: number;
}

const ProtectedAdminRoutes = () => (
  <AdminAuthGuard>
    {({ adminData }: { adminData: AdminData }) => (
      <AdminLayout adminData={adminData}>
        <Routes>
          {/* Redirect to appropriate dashboard */}
          <Route
            path="/"
            element={
              adminData.admin_type === 'PLATFORM' ? (
                <Navigate to="/admin/platform/tenants" replace />
              ) : (
                <Navigate to="/admin/tenant/dashboard" replace />
              )
            }
          />
          
          {/* Platform Admin Routes */}
          <Route path="platform/tenants" element={<TenantsList />} />
          <Route path="platform/tenants/create" element={<TenantCreate />} />
          <Route path="platform/tenants/:tenantId" element={<TenantDetails />} />
          <Route path="platform/tenants/:tenantId/admins" element={<TenantAdmins />} />
          <Route path="platform/tenants/:tenantId/documents" element={<TenantDocuments />} />
          
          {/* Tenant Admin Routes - Placeholder */}
          <Route 
            path="tenant/dashboard" 
            element={
              <div style={{ padding: '40px' }}>
                <h1>Tenant Admin Dashboard</h1>
                <p>Coming soon...</p>
              </div>
            } 
          />
        </Routes>
      </AdminLayout>
    )}
  </AdminAuthGuard>
);

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Admin Login */}
        <Route path="/admin/login" element={<AdminLogin />} />
        
        {/* Admin Routes - Protected */}
        <Route path="/admin/*" element={<ProtectedAdminRoutes />} />
        
        {/* Root redirect */}
        <Route path="/" element={<Navigate to="/admin/login" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
