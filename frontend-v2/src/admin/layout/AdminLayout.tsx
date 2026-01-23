import type { ReactNode } from 'react';
import AdminSidebar from './AdminSidebar';
import AdminHeader from './AdminHeader';
import './AdminLayout.css';

interface AdminData {
  user_id: number;
  full_name: string;
  email: string;
  admin_type: 'PLATFORM' | 'TENANT';
  tenant_id?: number;
}

interface AdminLayoutProps {
  adminData: AdminData;
  children: ReactNode;
}

const AdminLayout = ({ adminData, children }: AdminLayoutProps) => {
  return (
    <div className="admin-layout">
      <AdminSidebar adminData={adminData} />
      <div className="admin-main">
        <AdminHeader adminData={adminData} />
        <div className="admin-content">
          {children}
        </div>
      </div>
    </div>
  );
};

export default AdminLayout;
