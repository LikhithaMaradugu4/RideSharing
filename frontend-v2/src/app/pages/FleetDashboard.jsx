import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import fleetService from '../../services/fleet.service';
import './FleetDashboard.css';

function FleetDashboard() {
  const navigate = useNavigate();
  const token = localStorage.getItem('jwt_token');
  
  const [fleet, setFleet] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!token) {
      navigate('/login');
      return;
    }
    fetchFleetDetails();
  }, [token, navigate]);

  const fetchFleetDetails = async () => {
    try {
      setLoading(true);
      const data = await fleetService.getMyFleet();
      setFleet(data);
    } catch (err) {
      console.error('Failed to fetch fleet:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('jwt_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_info');
    navigate('/login');
  };

  if (loading) {
    return (
      <div className="fleet-dashboard">
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <span>Loading fleet details...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="fleet-dashboard">
        <header className="fleet-header">
          <h1>🏢 Fleet Dashboard</h1>
          <button className="btn-logout" onClick={handleLogout}>Logout</button>
        </header>
        <div className="error-state">
          <span className="error-icon">⚠️</span>
          <p>{error}</p>
          <button className="btn-retry" onClick={fetchFleetDetails}>Retry</button>
          <button className="btn-secondary" onClick={() => navigate('/app/rider-dashboard')}>
            Go to Rider Dashboard
          </button>
        </div>
      </div>
    );
  }

  // Fleet is PENDING approval
  if (fleet?.approval_status === 'PENDING') {
    return (
      <div className="fleet-dashboard">
        <header className="fleet-header">
          <h1>🏢 Fleet Dashboard</h1>
          <button className="btn-logout" onClick={handleLogout}>Logout</button>
        </header>
        <div className="pending-state">
          <div className="pending-card">
            <span className="pending-icon">⏳</span>
            <h2>Application Under Review</h2>
            <p>Your fleet application for <strong>{fleet.fleet_name}</strong> is currently being reviewed.</p>
            <p className="pending-note">This usually takes 1-2 business days. We'll notify you once approved.</p>
          </div>
          <button className="btn-secondary" onClick={() => navigate('/app/rider-dashboard')}>
            Go to Rider Dashboard
          </button>
        </div>
      </div>
    );
  }

  // Fleet is REJECTED
  if (fleet?.approval_status === 'REJECTED') {
    return (
      <div className="fleet-dashboard">
        <header className="fleet-header">
          <h1>🏢 Fleet Dashboard</h1>
          <button className="btn-logout" onClick={handleLogout}>Logout</button>
        </header>
        <div className="rejected-state">
          <div className="rejected-card">
            <span className="rejected-icon">❌</span>
            <h2>Application Rejected</h2>
            <p>Your fleet application for <strong>{fleet.fleet_name}</strong> was not approved.</p>
            <p className="rejected-note">Please contact support for more information.</p>
          </div>
          <button className="btn-secondary" onClick={() => navigate('/app/rider-dashboard')}>
            Go to Rider Dashboard
          </button>
        </div>
      </div>
    );
  }

  // Fleet is APPROVED - show full dashboard
  return (
    <div className="fleet-dashboard">
      <header className="fleet-header">
        <div className="header-left">
          <h1>🏢 {fleet?.fleet_name || 'Fleet Dashboard'}</h1>
          <span className="status-badge approved">APPROVED</span>
        </div>
        <div className="header-right">
          <button className="btn-profile" onClick={() => navigate('/app/profile')} title="Profile">
            👤
          </button>
          <button className="btn-home" onClick={() => navigate('/app/rider-dashboard')} title="Rider Mode">
            🏠
          </button>
          <button className="btn-logout" onClick={handleLogout}>Logout</button>
        </div>
      </header>

      <div className="dashboard-content">
        {/* Quick Stats */}
        <div className="stats-section">
          <h2>Fleet Overview</h2>
          <div className="stats-grid">
            <div className="stat-card" onClick={() => navigate('/app/fleet/drivers')}>
              <span className="stat-icon">👥</span>
              <span className="stat-label">Drivers</span>
            </div>
            <div className="stat-card" onClick={() => navigate('/app/fleet/vehicles')}>
              <span className="stat-icon">🚗</span>
              <span className="stat-label">Vehicles</span>
            </div>
            <div className="stat-card" onClick={() => navigate('/app/fleet/assignments')}>
              <span className="stat-icon">🔗</span>
              <span className="stat-label">Assignments</span>
            </div>
            <div className="stat-card" onClick={() => navigate('/app/fleet/trips')}>
              <span className="stat-icon">📋</span>
              <span className="stat-label">Trip History</span>
            </div>
          </div>
        </div>

        {/* Management Actions */}
        <div className="actions-section">
          <h2>Quick Actions</h2>
          <div className="action-buttons">
            <button className="action-btn" onClick={() => navigate('/app/fleet/drivers')}>
              <span className="action-icon">➕</span>
              <div className="action-text">
                <span className="action-title">Invite Driver</span>
                <span className="action-desc">Add drivers to your fleet</span>
              </div>
            </button>
            
            <button className="action-btn" onClick={() => navigate('/app/fleet/vehicles')}>
              <span className="action-icon">🚙</span>
              <div className="action-text">
                <span className="action-title">Add Vehicle</span>
                <span className="action-desc">Register a new vehicle</span>
              </div>
            </button>
            
            <button className="action-btn" onClick={() => navigate('/app/fleet/assignments')}>
              <span className="action-icon">🔗</span>
              <div className="action-text">
                <span className="action-title">Assign Vehicle</span>
                <span className="action-desc">Link drivers with vehicles</span>
              </div>
            </button>
            
            <button className="action-btn" onClick={() => navigate('/app/fleet/shifts')}>
              <span className="action-icon">⏰</span>
              <div className="action-text">
                <span className="action-title">Manage Shifts</span>
                <span className="action-desc">Start/end driver shifts</span>
              </div>
            </button>
          </div>
        </div>

        {/* Info Cards */}
        <div className="info-section">
          <div className="info-card">
            <span className="info-icon">ℹ️</span>
            <div className="info-content">
              <h4>Fleet ID</h4>
              <p>{fleet?.fleet_id}</p>
            </div>
          </div>
          <div className="info-card">
            <span className="info-icon">🏷️</span>
            <div className="info-content">
              <h4>Tenant ID</h4>
              <p>{fleet?.tenant_id}</p>
            </div>
          </div>
          <div className="info-card">
            <span className="info-icon">📊</span>
            <div className="info-content">
              <h4>Status</h4>
              <p>{fleet?.status || 'ACTIVE'}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default FleetDashboard;
