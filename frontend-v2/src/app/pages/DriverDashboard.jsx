import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import driverService from '../../services/driver.service';
import DriverLayout from '../layout/DriverLayout';
import './DriverDashboard.css';

function DriverDashboard() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [driverProfile, setDriverProfile] = useState(null);
  const [shiftStatus, setShiftStatus] = useState(null);
  const [activeFleet, setActiveFleet] = useState(null);
  const [activeVehicle, setActiveVehicle] = useState(null);
  const [shiftToggling, setShiftToggling] = useState(false);

  const token = localStorage.getItem('jwt_token');

  useEffect(() => {
    if (!token) {
      navigate('/login');
      return;
    }
    fetchDashboardData();
  }, [token, navigate]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch driver profile
      const profile = await driverService.getMyProfile(token);
      
      if (!profile) {
        navigate('/app/home');
        return;
      }

      if (profile.approval_status !== 'APPROVED') {
        navigate('/app/home');
        return;
      }

      setDriverProfile(profile);

      // Fetch active shift
      try {
        const shift = await driverService.getActiveShift(token);
        setShiftStatus(shift);
      } catch (err) {
        setShiftStatus(null);
      }

      // TODO: Fetch active fleet and vehicle once backend APIs are ready
      // For now, show placeholder context
    } catch (err) {
      setError(err.message || 'Failed to load dashboard');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleShiftToggle = async () => {
    try {
      setShiftToggling(true);
      setError(null);

      if (shiftStatus) {
        // End shift
        await driverService.endShift(token);
        setShiftStatus(null);
      } else {
        // Start shift
        const shift = await driverService.startShift(token);
        setShiftStatus(shift);
      }
    } catch (err) {
      setError(err.message || 'Failed to toggle shift');
      console.error('Error:', err);
    } finally {
      setShiftToggling(false);
    }
  };

  const getShiftStatusLabel = () => {
    if (!shiftStatus) return 'OFFLINE';
    return shiftStatus.status || 'OFFLINE';
  };

  const getShiftStatusColor = () => {
    if (!shiftStatus) return '#f44336'; // Red for offline
    if (shiftStatus.status === 'BUSY') return '#ff9800'; // Orange for busy
    if (shiftStatus.status === 'ONLINE') return '#4caf50'; // Green for online
    return '#f44336';
  };

  if (loading) {
    return (
      <DriverLayout driverProfile={driverProfile}>
        <div className="dashboard-container">
          <div className="loading-state">
            <p>Loading dashboard...</p>
          </div>
        </div>
      </DriverLayout>
    );
  }

  if (!driverProfile) {
    return null;
  }

  return (
    <DriverLayout driverProfile={driverProfile}>
      <div className="dashboard-container">
        <div className="dashboard-header">
          <h1>Driver Dashboard</h1>
          <p className="dashboard-subtitle">
            Welcome back, {driverProfile.full_name || 'Driver'}
          </p>
        </div>

        {error && (
          <div className="error-banner">
            <span className="error-icon">⚠️</span>
            <span>{error}</span>
            <button className="error-close" onClick={() => setError(null)}>×</button>
          </div>
        )}

        {/* Shift Control Section - PRIMARY */}
        <div className="shift-control-section">
          <div className="shift-control-card">
            <h2>Shift Status</h2>
            
            <div 
              className="shift-status-display"
              style={{ borderColor: getShiftStatusColor() }}
            >
              <div className="status-indicator" style={{ backgroundColor: getShiftStatusColor() }}></div>
              <div className="status-text">
                <span className="status-label">{getShiftStatusLabel()}</span>
                {shiftStatus && shiftStatus.started_at && (
                  <span className="status-time">
                    Since {new Date(shiftStatus.started_at).toLocaleTimeString()}
                  </span>
                )}
              </div>
            </div>

            <button 
              className={`shift-toggle-btn ${shiftStatus ? 'go-offline' : 'go-online'}`}
              onClick={handleShiftToggle}
              disabled={shiftToggling}
              title={shiftStatus ? 'Go Offline' : 'Go Online'}
            >
              {shiftToggling ? 'Processing...' : (shiftStatus ? 'Go Offline' : 'Go Online')}
            </button>

            {shiftStatus && shiftStatus.status === 'BUSY' && (
              <div className="shift-warning">
                <span>You are currently on a trip</span>
              </div>
            )}

            {!shiftStatus && (
              <div className="shift-info">
                <span>Click "Go Online" to start accepting trips</span>
              </div>
            )}
          </div>
        </div>

        {/* Current Context Summary - READ-ONLY */}
        <div className="context-summary-section">
          <h2>Current Context</h2>

          <div className="context-grid">
            {/* Active Fleet Card */}
            <div className="context-card">
              <div className="context-card-header">
                <h3>Active Fleet</h3>
                <span className="context-icon">🏢</span>
              </div>
              <div className="context-card-content">
                {activeFleet ? (
                  <>
                    <div className="context-item">
                      <span className="label">Name:</span>
                      <span className="value">{activeFleet.name}</span>
                    </div>
                    <div className="context-item">
                      <span className="label">Type:</span>
                      <span className="badge" style={{
                        backgroundColor: activeFleet.type === 'INDIVIDUAL' ? '#e3f2fd' : '#f3e5f5',
                        color: activeFleet.type === 'INDIVIDUAL' ? '#1976d2' : '#7b1fa2'
                      }}>
                        {activeFleet.type}
                      </span>
                    </div>
                  </>
                ) : (
                  <p className="empty-state">No active fleet</p>
                )}
              </div>
            </div>

            {/* Active Vehicle Card */}
            <div className="context-card">
              <div className="context-card-header">
                <h3>Active Vehicle</h3>
                <span className="context-icon">🚗</span>
              </div>
              <div className="context-card-content">
                {activeVehicle ? (
                  <>
                    <div className="context-item">
                      <span className="label">Registration:</span>
                      <span className="value">{activeVehicle.registration}</span>
                    </div>
                    <div className="context-item">
                      <span className="label">Category:</span>
                      <span className="value">{activeVehicle.category}</span>
                    </div>
                    <div className="context-item">
                      <span className="label">Status:</span>
                      <span className={`badge status-${activeVehicle.status?.toLowerCase()}`}>
                        {activeVehicle.status}
                      </span>
                    </div>
                  </>
                ) : (
                  <p className="empty-state">No active vehicle</p>
                )}
              </div>
            </div>

            {/* Today's Availability Card */}
            <div className="context-card">
              <div className="context-card-header">
                <h3>Today's Availability</h3>
                <span className="context-icon">📅</span>
              </div>
              <div className="context-card-content">
                <p className="empty-state">Manage availability in the Availability section</p>
              </div>
            </div>

            {/* Quick Links Card */}
            <div className="context-card">
              <div className="context-card-header">
                <h3>Quick Actions</h3>
                <span className="context-icon">⚡</span>
              </div>
              <div className="context-card-content quick-actions">
                <a href="/app/driver/vehicles" className="quick-link">
                  Add Vehicle
                </a>
                <a href="/app/driver/dispatches" className="quick-link">
                  View Dispatches
                </a>
                <a href="/app/driver/fleets" className="quick-link">
                  Join Fleet
                </a>
              </div>
            </div>
          </div>
        </div>

        {/* Info Section */}
        <div className="dashboard-info-section">
          <div className="info-box">
            <h3>Driver Guidelines</h3>
            <ul>
              <li>You must be ONLINE to accept dispatches</li>
              <li>Complete all vehicle documents for approval</li>
              <li>Set your availability if joining a business fleet</li>
              <li>Manage vehicles from the Vehicles page</li>
            </ul>
          </div>
        </div>
      </div>
    </DriverLayout>
  );
}

export default DriverDashboard;
