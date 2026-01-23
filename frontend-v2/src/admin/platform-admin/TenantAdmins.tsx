import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import adminService from '../../services/admin.service';
import './TenantAdmins.css';

interface TenantAdmin {
  tenant_admin_id: number;
  user_id: number;
  email: string;
  full_name: string;
  is_primary: boolean;
  created_on: string;
}

interface AdminFormData {
  email: string;
  full_name: string;
}

const TenantAdmins = () => {
  const { tenantId } = useParams();
  const navigate = useNavigate();
  const [admin, setAdmin] = useState<TenantAdmin | null>(null);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState<AdminFormData>({
    email: '',
    full_name: ''
  });

  useEffect(() => {
    loadTenantAdmin();
  }, [tenantId]);

  const loadTenantAdmin = async () => {
    try {
      setLoading(true);
      const data: TenantAdmin = await adminService.getTenantAdmin(Number(tenantId));
      setAdmin(data);
      setError('');
    } catch (err: any) {
      if (err.message.includes('404')) {
        setAdmin(null);
      } else {
        setError(err.message || 'Failed to load tenant admin');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError('');
    setCreating(true);

    try {
      await adminService.createTenantAdmin(Number(tenantId), formData);
      loadTenantAdmin();
      setFormData({ email: '', full_name: '' });
    } catch (err: any) {
      setError(err.message || 'Failed to create tenant admin');
    } finally {
      setCreating(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return <div className="loading">Loading tenant admin...</div>;
  }

  return (
    <div className="tenant-admins-container">
      <div className="tenant-admins-header">
        <h1>Primary Tenant Admin</h1>
        <button 
          className="btn-secondary"
          onClick={() => navigate(`/admin/platform/tenants/${tenantId}`)}
        >
          Back to Tenant
        </button>
      </div>

      {error && (
        <div className="error-message">{error}</div>
      )}

      {admin ? (
        <div className="admin-details-card">
          <div className="admin-badge">
            <span className="badge-primary">Primary Admin</span>
          </div>
          <div className="admin-info-grid">
            <div className="info-item">
              <span className="info-label">Full Name</span>
              <span className="info-value">{admin.full_name}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Email</span>
              <span className="info-value">{admin.email}</span>
            </div>
            <div className="info-item">
              <span className="info-label">User ID</span>
              <span className="info-value">{admin.user_id}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Created On</span>
              <span className="info-value">{formatDate(admin.created_on)}</span>
            </div>
          </div>
          <div className="admin-note">
            <strong>Note:</strong> The primary tenant admin has full access to manage this tenant's operations.
          </div>
        </div>
      ) : (
        <div className="admin-create-card">
          <div className="create-header">
            <h2>Create Primary Tenant Admin</h2>
            <p>This admin will have full access to manage the tenant's operations.</p>
          </div>

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="email">Email *</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                placeholder="admin@example.com"
                disabled={creating}
              />
              <small className="form-help">Admin will use this email to log in</small>
            </div>

            <div className="form-group">
              <label htmlFor="full_name">Full Name (Optional)</label>
              <input
                type="text"
                id="full_name"
                name="full_name"
                value={formData.full_name}
                onChange={handleChange}
                placeholder="John Doe"
                disabled={creating}
              />
              <small className="form-help">If not provided, email will be used as name</small>
            </div>

            <div className="form-info-box">
              <h4>Auto-Generated Credentials</h4>
              <ul>
                <li>A default password will be auto-generated</li>
                <li>Format: [email username] + "123"</li>
                <li>Admin should change password after first login</li>
              </ul>
            </div>

            <div className="form-actions">
              <button 
                type="button" 
                className="btn-cancel"
                onClick={() => navigate(`/admin/platform/tenants/${tenantId}`)}
                disabled={creating}
              >
                Cancel
              </button>
              <button 
                type="submit" 
                className="btn-submit"
                disabled={creating}
              >
                {creating ? 'Creating...' : 'Create Primary Admin'}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};

export default TenantAdmins;
