import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import adminService from '../../services/admin.service';
import './TenantCreate.css';

const CURRENCIES = ['USD', 'EUR', 'GBP', 'INR', 'AUD', 'CAD', 'SGD'];
const TIMEZONES = [
  'America/New_York',
  'America/Chicago',
  'America/Los_Angeles',
  'Europe/London',
  'Europe/Paris',
  'Asia/Tokyo',
  'Asia/Singapore',
  'Asia/Kolkata',
  'Australia/Sydney'
];

const TenantCreate = () => {
  const [formData, setFormData] = useState({
    name: '',
    tenant_code: '',
    default_currency: 'USD',
    default_timezone: 'America/New_York'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await adminService.platformCreateTenant(formData);
      navigate(`/admin/platform/tenants/${response.tenant_id}`);
    } catch (err) {
      setError(err.message || 'Failed to create tenant');
      setLoading(false);
    }
  };

  return (
    <div className="tenant-create-container">
      <div className="tenant-create-header">
        <h1>Create New Tenant</h1>
        <button 
          className="btn-secondary"
          onClick={() => navigate('/admin/platform/tenants')}
        >
          Back to Tenants
        </button>
      </div>

      {error && (
        <div className="error-message">{error}</div>
      )}

      <div className="tenant-create-card">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="name">Tenant Name *</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
              placeholder="Enter tenant name"
              disabled={loading}
            />
            <small className="form-help">This will be the organization name</small>
          </div>

          <div className="form-group">
            <label htmlFor="tenant_code">Tenant Code *</label>
            <input
              type="text"
              id="tenant_code"
              name="tenant_code"
              value={formData.tenant_code}
              onChange={handleChange}
              required
              placeholder="Unique code (e.g., UBER_IND)"
              disabled={loading}
            />
            <small className="form-help">Unique identifier, uppercase recommended</small>
          </div>

          <div className="form-group">
            <label htmlFor="default_currency">Default Currency *</label>
            <select
              id="default_currency"
              name="default_currency"
              value={formData.default_currency}
              onChange={handleChange}
              required
              disabled={loading}
            >
              {CURRENCIES.map((currency) => (
                <option key={currency} value={currency}>
                  {currency}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="default_timezone">Default Timezone *</label>
            <select
              id="default_timezone"
              name="default_timezone"
              value={formData.default_timezone}
              onChange={handleChange}
              required
              disabled={loading}
            >
              {TIMEZONES.map((timezone) => (
                <option key={timezone} value={timezone}>
                  {timezone}
                </option>
              ))}
            </select>
          </div>

          <div className="form-actions">
            <button 
              type="button" 
              className="btn-cancel"
              onClick={() => navigate('/admin/platform/tenants')}
              disabled={loading}
            >
              Cancel
            </button>
            <button 
              type="submit" 
              className="btn-submit"
              disabled={loading}
            >
              {loading ? 'Creating...' : 'Create Tenant'}
            </button>
          </div>
        </form>
      </div>

      <div className="tenant-create-note">
        <h3>Note:</h3>
        <ul>
          <li>After creating the tenant, you can add a primary tenant admin</li>
          <li>Upload tenant documents for verification</li>
          <li>Tenant code will be auto-generated from the name</li>
        </ul>
      </div>
    </div>
  );
};

export default TenantCreate;
