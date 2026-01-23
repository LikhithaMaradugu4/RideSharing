import { useEffect, useState, type ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import adminService from '../../services/admin.service';

interface AdminData {
  user_id: number;
  full_name: string;
  email: string;
  admin_type: 'PLATFORM' | 'TENANT';
  tenant_id?: number;
}

interface AdminAuthGuardProps {
  children: (props: { adminData: AdminData }) => ReactNode;
}

const AdminAuthGuard = ({ children }: AdminAuthGuardProps) => {
  const [loading, setLoading] = useState(true);
  const [adminData, setAdminData] = useState<AdminData | null>(null);
  const location = useLocation();

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const data: AdminData = await adminService.getCurrentAdmin();
      setAdminData(data);
    } catch (error) {
      setAdminData(null);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh' 
      }}>
        <div>Loading...</div>
      </div>
    );
  }

  if (!adminData) {
    return <Navigate to="/admin/login" state={{ from: location }} replace />;
  }

  return children({ adminData });
};

export default AdminAuthGuard;
