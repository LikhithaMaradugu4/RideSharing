import { NavLink, useNavigate } from 'react-router-dom';
import adminService from '../../services/admin.service';
import './AdminSidebar.css';

const AdminSidebar = ({ adminData = {} }) => {
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
        <h2>RideShare <span style={{ fontWeight: 300 }}>Admin</span></h2>
        <div className="admin-type-badge">
          {adminData?.admin_type === 'PLATFORM' ? 'Platform Admin' : adminData?.admin_type === 'TENANT' ? 'Tenant Admin' : 'Admin'}
        </div>
      </div>

      <nav className="admin-sidebar-nav">
        {/* PLATFORM ADMIN SECTION */}
        {adminData?.admin_type === 'PLATFORM' && (
          <>
          <NavLink 
            to="/admin/platform/tenants" 
            className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 21h18"/><path d="M5 21V7l8-4 8 4v14"/><path d="M9 10a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v11H9z"/></svg>
            <span>Tenants</span>
          </NavLink>

          <div className="nav-group-label">Platform Settings</div>

          <NavLink
            to="/admin/platform/countries"
            className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
            <span>Countries</span>
          </NavLink>

          <NavLink
            to="/admin/platform/cities"
            className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 21h18"/><path d="M9 21V9l3-3 3 3v12"/><path d="M5 21V5l4-2v18"/><path d="M19 21V11l-4-2"/></svg>
            <span>Cities</span>
          </NavLink>

          <NavLink
            to="/admin/platform/fare-config"
            className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
            <span>Fare Config</span>
          </NavLink>

          <NavLink
            to="/admin/platform/commission-config"
            className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
            <span>Commission Config</span>
          </NavLink>
          </>
        )}

        {/* TENANT ADMIN SECTION */}
        {adminData?.admin_type === 'TENANT' && (
          <>
            <NavLink 
              to="/admin/tenant/dashboard" 
              className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="7" height="9"></rect><rect x="14" y="3" width="7" height="5"></rect><rect x="14" y="12" width="7" height="9"></rect><rect x="3" y="16" width="7" height="5"></rect></svg>
              <span>Dashboard</span>
            </NavLink>

            <div className="nav-group-label">Approvals</div>

            <NavLink 
              to="/admin/tenant/driver-approvals" 
              className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="8.5" cy="7" r="4"></circle><polyline points="17 11 19 13 23 9"></polyline></svg>
              <span>Driver Approvals</span>
            </NavLink>

            <NavLink 
              to="/admin/tenant/fleet-approvals" 
              className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><path d="M9 15l2 2 4-4"></path></svg>
              <span>Fleet Approvals</span>
            </NavLink>
                      <NavLink
              to="/admin/tenant/vehicle-approvals"
              className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="1" y="3" width="15" height="13"></rect><polygon points="16 8 20 8 23 11 23 16 16 16 16 8"></polygon><circle cx="5.5" cy="18.5" r="2.5"></circle><circle cx="18.5" cy="18.5" r="2.5"></circle></svg>
              <span>Vehicle Approvals</span>
            </NavLink>
            <div className="nav-group-label">Management</div>

            <NavLink 
              to="/admin/tenant/drivers" 
              className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
              <span>Drivers</span>
            </NavLink>

            <NavLink 
              to="/admin/tenant/fleets" 
              className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path></svg>
              <span>Fleets</span>
            </NavLink>

            <NavLink 
              to="/admin/tenant/vehicles" 
              className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="1" y="3" width="15" height="13"></rect><polygon points="16 8 20 8 23 11 23 16 16 16 16 8"></polygon><circle cx="5.5" cy="18.5" r="2.5"></circle><circle cx="18.5" cy="18.5" r="2.5"></circle></svg>
              <span>Vehicles</span>
            </NavLink>

            <div className="nav-group-label">Settings</div>

            <NavLink 
              to="/admin/tenant/operating-regions" 
              className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>
              <span>Operating Regions</span>
            </NavLink>

            
          </>
        )}
      </nav>

      <div className="admin-sidebar-footer">
        <button onClick={handleLogout} className="logout-button">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>
          <span>Logout</span>
        </button>
      </div>
    </div>
  );
};

export default AdminSidebar;