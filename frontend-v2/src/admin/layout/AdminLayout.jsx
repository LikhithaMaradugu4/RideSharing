import { Outlet } from 'react-router-dom';
import AdminSidebar from './AdminSidebar';
import AdminHeader from './AdminHeader';
import './AdminLayout.css';

const AdminLayout = ({ adminData }) => {
  return (
    <div className="admin-layout">
      <AdminSidebar adminData={adminData} />
      <div className="admin-main">
        <AdminHeader adminData={adminData} />
        <div className="admin-content">
          <Outlet context={{ adminData }} />
        </div>
      </div>
    </div>
  );
};

export default AdminLayout;
