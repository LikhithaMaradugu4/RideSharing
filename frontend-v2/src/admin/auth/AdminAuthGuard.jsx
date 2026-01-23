import { useEffect, useState } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import adminService from '../../services/admin.service';

const AdminAuthGuard = ({ children }) => {
  const [loading, setLoading] = useState(true);
  const [adminData, setAdminData] = useState(null);
  const location = useLocation();

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const data = await adminService.getCurrentAdmin();
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
