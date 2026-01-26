import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import adminService from '../../services/admin.service';
import './TenantsList.css';

const TenantsList = () => {
  const [tenants, setTenants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    loadTenants();
  }, []);

  const loadTenants = async () => {
    try {
      setLoading(true);
      const data = await adminService.platformListTenants();
      setTenants(data);
      setError('');
    } catch (err) {
      setError(err.message || 'Failed to load tenants');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (tenantId, tenantName) => {
    if (!window.confirm(`Are you sure you want to delete tenant "${tenantName}"?`)) {
      return;
    }

    try {
      await adminService.deleteTenant(tenantId);
      loadTenants();
    } catch (err) {
      alert(err.message || 'Failed to delete tenant');
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  if (loading) {
    return <div className="loading">Loading tenants...</div>;
  }

  return (
    <div className="tenants-list-container">
      <div className="tenants-header">
        <h1>Tenants</h1>
        <button 
          className="btn-primary"
          onClick={() => navigate('/admin/platform/tenants/create')}
        >
          + Create Tenant
        </button>
      </div>

      {error && (
        <div className="error-message">{error}</div>
      )}

      {tenants.length === 0 ? (
        <div className="empty-state">
          <p>No tenants found</p>
          <button 
            className="btn-primary"
            onClick={() => navigate('/admin/platform/tenants/create')}
          >
            Create First Tenant
          </button>
        </div>
      ) : (
        <div className="tenants-table-container">
          <table className="tenants-table">
            <thead>
              <tr>
                <th>Tenant Name</th>
                <th>Code</th>
                <th>Status</th>
                <th>Currency</th>
                <th>Timezone</th>
                <th>Created On</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {tenants.map((tenant) => (
                <tr key={tenant.tenant_id}>
                  <td className="tenant-name">{tenant.name}</td>
                  <td>{tenant.tenant_code}</td>
                  <td>
                    <span className={`status-badge status-${tenant.status.toLowerCase()}`}>
                      {tenant.status}
                    </span>
                  </td>
                  <td>{tenant.default_currency}</td>
                  <td>{tenant.default_timezone}</td>
                  <td>{formatDate(tenant.created_on)}</td>
                  <td className="actions-cell">
                    <button
                      className="btn-action btn-view"
                      onClick={() => navigate(`/admin/platform/tenants/${tenant.tenant_id}`)}
                    >
                      View Details
                    </button>
                    <button
                      className="btn-action btn-delete"
                      onClick={() => navigate(`/admin/platform/tenants/${tenant.tenant_id}`)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default TenantsList;
