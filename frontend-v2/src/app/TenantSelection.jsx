import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import driverService from '../services/driver.service';
import './TenantSelection.css';

export default function TenantSelection({ applicationType }) {
  const navigate = useNavigate();
  const [tenants, setTenants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedTenant, setSelectedTenant] = useState(null);

  useEffect(() => {
    fetchTenants();
  }, []);

  const fetchTenants = async () => {
    try {
      setLoading(true);
      const data = await driverService.getTenants();
      setTenants(Array.isArray(data) ? data : (data.tenants || []));
      setError(null);
    } catch (err) {
      setError('Unable to load tenants. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleTenantSelect = (tenantId) => {
    setSelectedTenant(tenantId);
  };

  const handleProceed = () => {
    if (!selectedTenant) {
      setError('Please select a tenant to proceed');
      return;
    }

    // Navigate to the appropriate application form with tenant_id
    if (applicationType === 'driver') {
      navigate(`/apply-driver/${selectedTenant}`);
    } else if (applicationType === 'fleet-owner') {
      navigate(`/apply-fleet-owner/${selectedTenant}`);
    }
  };

  if (loading) {
    return (
      <div className="tenant-selection-container">
        <div className="loading">Loading available tenants...</div>
      </div>
    );
  }

  return (
    <div className="tenant-selection-container">
      <div className="tenant-selection-card">
        <h1>Select Your Tenant</h1>
        <p className="subtitle">
          {applicationType === 'driver'
            ? 'Choose the company you want to drive for'
            : 'Choose the platform you want to operate your fleet on'}
        </p>

        {error && <div className="error-message">{error}</div>}

        <div className="tenants-grid">
          {tenants && tenants.length > 0 ? (
            tenants.map((tenant) => (
              <div
                key={tenant.tenant_id}
                className={`tenant-card ${selectedTenant === tenant.tenant_id ? 'selected' : ''}`}
                onClick={() => handleTenantSelect(tenant.tenant_id)}
              >
                <div className="tenant-icon">
                  {tenant.name && tenant.name[0].toUpperCase()}
                </div>
                <h3>{tenant.name || tenant.tenant_name}</h3>
                <p className="tenant-code">ID: {tenant.tenant_id}</p>
                {selectedTenant === tenant.tenant_id && (
                  <div className="check-mark">✓</div>
                )}
              </div>
            ))
          ) : (
            <div className="no-tenants">
              No tenants available at the moment.
            </div>
          )}
        </div>

        <div className="actions">
          <button
            className="btn-back"
            onClick={() => navigate('/')}
          >
            Back
          </button>
          <button
            className="btn-proceed"
            onClick={handleProceed}
            disabled={!selectedTenant}
          >
            Proceed
          </button>
        </div>
      </div>
    </div>
  );
}
