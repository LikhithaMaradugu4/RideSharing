import './AdminHeader.css';

interface AdminData {
  user_id: number;
  full_name: string;
  email: string;
  admin_type: 'PLATFORM' | 'TENANT';
  tenant_id?: number;
}

interface AdminHeaderProps {
  adminData: AdminData;
}

const AdminHeader = ({ adminData }: AdminHeaderProps) => {
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
