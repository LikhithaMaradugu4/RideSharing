import './AdminHeader.css';

const AdminHeader = ({ adminData }) => {
  return (
    <div className="admin-header">
      <div className="admin-header-content">
        <h1 className="admin-header-title">Admin Panel</h1>
        <div className="admin-header-user">
          <div className="admin-user-info">
            <span className="admin-user-name">{adminData.full_name}</span>
            <span className="admin-user-email">{adminData.email}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminHeader;
