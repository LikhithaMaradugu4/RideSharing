import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import adminService from '../../services/admin.service';
import './TenantDetails.css';

const TenantDetails = () => {
  const { tenantId } = useParams();
  const navigate = useNavigate();
  const [tenant, setTenant] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadTenantDetails();
  }, [tenantId]);

  const loadTenantDetails = async () => {
    try {
      setLoading(true);
      const data = await adminService.platformGetTenantDetails(tenantId);
      console.log('Tenant Details Response:', data);
      setTenant(data);
      setError('');
    } catch (err) {
      setError(err.message || 'Failed to load tenant details');
    } finally {
      setLoading(false);
    }
  };

  // Status updates and admin assignment handled via respective screens

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return <div className="loading">Loading tenant details...</div>;
  }

  if (error) {
    return (
      <div>
        <div className="error-message">{error}</div>
        <button 
          className="btn-secondary"
          onClick={() => navigate('/admin/platform/tenants')}
        >
          Back to Tenants
        </button>
      </div>
    );
  }

  return (
    <div className="tenant-details-container">
      <div className="tenant-details-header">
        <h1>{tenant.name}</h1>
        <button 
          className="btn-secondary"
          onClick={() => navigate('/admin/platform/tenants')}
        >
          Back to Tenants
        </button>
      </div>

      <div className="tenant-details-grid">
        {/* Tenant Information Card */}
        <div className="details-card">
          <h2>Tenant Information</h2>
          <div className="info-grid">
            <div className="info-item">
              <span className="info-label">Tenant Code</span>
              <span className="info-value">{tenant.tenant_code}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Status</span>
              <span className={`status-badge status-${tenant.status.toLowerCase()}`}>
                {tenant.status}
              </span>
            </div>
            <div className="info-item">
              <span className="info-label">Default Currency</span>
              <span className="info-value" style={{color: '#2c3e50', fontWeight: '500'}}>
                {tenant.default_currency || 'N/A'}
              </span>
            </div>
            <div className="info-item">
              <span className="info-label">Default Timezone</span>
              <span className="info-value" style={{color: '#2c3e50', fontWeight: '500'}}>
                {tenant.default_timezone || 'N/A'}
              </span>
            </div>
            <div className="info-item">
              <span className="info-label">Created On</span>
              <span className="info-value">{formatDate(tenant.created_on)}</span>
            </div>
          </div>
        </div>

        {/* Primary Admin Card */}
        <div className="details-card">
          <div className="card-header">
            <h2>Primary Tenant Admin</h2>
            {!tenant.primary_admin && (
              <button
                className="btn-primary"
                onClick={() => navigate(`/admin/platform/tenants/${tenantId}/admins`)}
              >
                Create Admin
              </button>
            )}
          </div>
          {tenant.primary_admin ? (
            <div className="admin-info">
              <div className="info-item">
                <span className="info-label">Name</span>
                <span className="info-value">{tenant.primary_admin.full_name}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Email</span>
                <span className="info-value">{tenant.primary_admin.email}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Created On</span>
                <span className="info-value">{formatDate(tenant.primary_admin.created_on)}</span>
              </div>
              <button
                className="btn-secondary btn-block"
                onClick={() => navigate(`/admin/platform/tenants/${tenantId}/admins`)}
              >
                View Details
              </button>
            </div>
          ) : (
            <div className="empty-admin">
              <p>No primary admin assigned yet</p>
              <button
                className="btn-primary"
                onClick={() => navigate(`/admin/platform/tenants/${tenantId}/admins`)}
              >
                Create Primary Admin
              </button>
            </div>
          )}
        </div>

        {/* Documents Card */}
        <div className="details-card">
          <div className="card-header">
            <h2>Documents</h2>
            <button
              className="btn-primary"
              onClick={() => navigate(`/admin/platform/tenants/${tenantId}/documents`)}
            >
              Manage Documents
            </button>
          </div>
          <div className="documents-summary">
            <div className="doc-count">
              <span className="count-number">{tenant.document_count}</span>
              <span className="count-label">Documents Uploaded</span>
            </div>
            <button
              className="btn-secondary btn-block"
              onClick={() => navigate(`/admin/platform/tenants/${tenantId}/documents`)}
            >
              View All Documents
            </button>
          </div>
        </div>
      </div>


    </div>
  );
};

export default TenantDetails;
