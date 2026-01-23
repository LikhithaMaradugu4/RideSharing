import { NavLink, useNavigate } from 'react-router-dom';
import adminService from '../../services/admin.service';
import './AdminSidebar.css';

const AdminSidebar = ({ adminData }) => {
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await adminService.logout();
      navigate('/admin/login');
    } catch (error) {
      console.error('Logout error:', error);
      navigate('/admin/login');
    }
  };

  return (
    <div className="admin-sidebar">
      <div className="admin-sidebar-header">
        <h2>RideShare Admin</h2>
        <p className="admin-type">
          {adminData.admin_type === 'PLATFORM' ? 'Platform Admin' : 'Tenant Admin'}
        </p>
      </div>

      <nav className="admin-sidebar-nav">
        {adminData.admin_type === 'PLATFORM' && (
          <>
            <NavLink 
              to="/admin/platform/tenants" 
              className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
            >
              Tenants
            </NavLink>
          </>
        )}

        {adminData.admin_type === 'TENANT' && (
          <>
            <NavLink 
              to="/admin/tenant/dashboard" 
              className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
            >
              Dashboard
            </NavLink>
            <NavLink 
              to="/admin/tenant/drivers" 
              className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
            >
              Drivers
            </NavLink>
            <NavLink 
              to="/admin/tenant/fleets" 
              className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
            >
              Fleets
            </NavLink>
          </>
        )}
      </nav>

      <div className="admin-sidebar-footer">
        <button onClick={handleLogout} className="logout-button">
          Logout
        </button>
      </div>
    </div>
  );
};

export default AdminSidebar;
