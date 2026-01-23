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

interface TenantFormData {
  tenant_name: string;
  default_currency: string;
  default_timezone: string;
}

const TenantCreate = () => {
  const [formData, setFormData] = useState<TenantFormData>({
    tenant_name: '',
    default_currency: 'USD',
    default_timezone: 'America/New_York'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response: any = await adminService.createTenant(formData);
      navigate(`/admin/platform/tenants/${response.tenant_id}`);
    } catch (err: any) {
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
            <label htmlFor="tenant_name">Tenant Name *</label>
            <input
              type="text"
              id="tenant_name"
              name="tenant_name"
              value={formData.tenant_name}
              onChange={handleChange}
              required
              placeholder="Enter tenant name"
              disabled={loading}
            />
            <small className="form-help">This will be the organization name</small>
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
