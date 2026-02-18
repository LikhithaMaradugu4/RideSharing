import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import userService from '../../services/user.service';
import tokenStorage from '../../services/tokenStorage';
import Icons from '../../components/Icons';
import './UserHome.css';

function UserHome() {
  const navigate = useNavigate();
  const [capabilities, setCapabilities] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchCapabilities();
  }, []);

  const fetchCapabilities = async () => {
    try {
      setLoading(true);
      setError(null);

      const token = tokenStorage.get('jwt_token');
      if (!token) {
        setError('Authentication token not found. Please log in again.');
        navigate('/login');
        return;
      }

      const data = await userService.getCapabilities(token);
      setCapabilities(data);
    } catch (err) {
      setError(err.message || 'Failed to load capabilities');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="user-home-layout">
        <div className="loading">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="user-home-layout">
        <div className="error-message">{error}</div>
        <button onClick={fetchCapabilities} className="retry-button">
          Try Again
        </button>
      </div>
    );
  }

  if (!capabilities) {
    return (
      <div className="user-home-layout">
        <div className="error-message">No capabilities data available</div>
      </div>
    );
  }

  // Extract capability states
  const driverExists = capabilities.driver?.exists || false;
  const driverStatus = capabilities.driver?.approval_status;
  const isApprovedDriver = driverExists && driverStatus === 'APPROVED';
  
  const fleetOwnerExists = capabilities.fleet_owner?.exists || false;
  const fleetOwnerStatus = capabilities.fleet_owner?.approval_status;
  const isApprovedFleetOwner = fleetOwnerExists && fleetOwnerStatus === 'APPROVED';

  // Determine driver application status (submitted but not yet approved)
  const hasPendingDriverApp = driverExists && (driverStatus === 'PENDING' || driverStatus === 'PARTIALLY_REJECTED' || driverStatus === 'REJECTED');

  // Determine fleet application status (submitted but not yet approved)
  const hasPendingFleetApp = fleetOwnerExists && (fleetOwnerStatus === 'PENDING' || fleetOwnerStatus === 'PARTIALLY_REJECTED' || fleetOwnerStatus === 'REJECTED');

  // Determine primary identity
  const isDriver = isApprovedDriver;
  const isFleetOwner = isApprovedFleetOwner;
  const isOnlyRider = !isDriver && !isFleetOwner;

  return (
    <div className="user-home-layout">
      <div className="user-home-card">
        <div className="brand-header">
          <div className="logo-circle">
            <Icons.Home size={24} color="white" />
          </div>
          <span className="brand-name">RideSync</span>
        </div>

        {/* CASE 1: ONLY RIDER */}
        {isOnlyRider && (
          <div className="view-container fade-in">
            <header className="home-header">
              <h1>Welcome back!</h1>
              <p>Where would you like to go today?</p>
            </header>

            <button 
              onClick={() => navigate('/app/rider-dashboard')}
              className="action-card primary-card"
            >
              <div className="card-icon">
                <Icons.Car size={32} color="black" />
              </div>
              <div className="card-text">
                <span className="card-title">Book a Ride</span>
                <span className="card-subtitle">Find a driver in minutes</span>
              </div>
            </button>

            {/* Driver Application Status (if submitted) */}
            {hasPendingDriverApp && (
              <div className="driver-app-status-card">
                <div className="app-status-row">
                  <Icons.CarSide size={18} />
                  <span className="app-status-label">Driver Application</span>
                  <span className={`app-status-badge ${
                    driverStatus === 'PENDING' ? 'status-pending' :
                    driverStatus === 'PARTIALLY_REJECTED' ? 'status-partial' :
                    'status-rejected'
                  }`}>
                    {driverStatus === 'PENDING' ? 'Under Review' :
                     driverStatus === 'PARTIALLY_REJECTED' ? 'Action Needed' :
                     'Rejected'}
                  </span>
                </div>
                <p className="app-status-desc">
                  {driverStatus === 'PENDING'
                    ? 'Your application is being reviewed. We\'ll notify you once it\'s approved.'
                    : driverStatus === 'PARTIALLY_REJECTED'
                    ? 'Some documents need attention. Please review and resubmit.'
                    : 'Your application was not approved. You may reapply.'}
                </p>
                <button
                  className="btn-app-status"
                  onClick={() => navigate('/app/driver/application-status')}
                >
                  View Application
                </button>
              </div>
            )}

            {/* Fleet Application Status (if submitted) */}
            {hasPendingFleetApp && (
              <div className="driver-app-status-card">
                <div className="app-status-row">
                  <Icons.Building size={18} />
                  <span className="app-status-label">Fleet Application</span>
                  <span className={`app-status-badge ${
                    fleetOwnerStatus === 'PENDING' ? 'status-pending' :
                    fleetOwnerStatus === 'PARTIALLY_REJECTED' ? 'status-partial' :
                    'status-rejected'
                  }`}>
                    {fleetOwnerStatus === 'PENDING' ? 'Under Review' :
                     fleetOwnerStatus === 'PARTIALLY_REJECTED' ? 'Action Needed' :
                     'Rejected'}
                  </span>
                </div>
                <p className="app-status-desc">
                  {fleetOwnerStatus === 'PENDING'
                    ? 'Your fleet application is being reviewed. We\'ll notify you once it\'s approved.'
                    : fleetOwnerStatus === 'PARTIALLY_REJECTED'
                    ? 'Some documents need attention. Please review and resubmit.'
                    : 'Your fleet application was not approved. You may reapply.'}
                </p>
                <button
                  className="btn-app-status"
                  onClick={() => navigate('/app/fleet/application-status')}
                >
                  View Application
                </button>
              </div>
            )}

            <div className="divider"><span>{(hasPendingDriverApp || hasPendingFleetApp) ? 'More options' : 'Or join the team'}</span></div>

            <div className="onboarding-grid">
              {!hasPendingDriverApp && (
                <button onClick={() => navigate('/driver-tenant-selection')} className="onboarding-option">
                  <span className="option-icon">
                    <Icons.DollarSign size={24} />
                  </span>
                  <span>Drive & Earn</span>
                </button>
              )}
              {!hasPendingFleetApp && (
                <button onClick={() => navigate('/fleet-owner-tenant-selection')} className="onboarding-option">
                  <span className="option-icon">
                    <Icons.Building size={24} />
                  </span>
                  <span>Manage Fleet</span>
                </button>
              )}
            </div>
          </div>
        )}

        {/* CASE 2: APPROVED DRIVER */}
        {isDriver && !isFleetOwner && (
          <div className="view-container fade-in">
            <header className="home-header">
              <h1>Driver Dashboard</h1>
              <p>Your vehicle is ready for the road.</p>
            </header>

            <button 
              onClick={() => navigate('/app/driver/dashboard')}
              className="action-card driver-card"
            >
              <div className="card-icon">
                <Icons.Flash size={32} color="white" />
              </div>
              <div className="card-text">
                <span className="card-title">Start Driving</span>
                <span className="card-subtitle">Go online to receive requests</span>
              </div>
            </button>

            <button onClick={() => navigate('/app/rider-dashboard')} className="ghost-button">
              Need a ride instead?
            </button>
          </div>
        )}

        {/* CASE 3: APPROVED FLEET OWNER */}
        {isFleetOwner && (
          <div className="view-container fade-in">
            <header className="home-header">
              <h1>Fleet Management</h1>
              <p>Overview of your business operations.</p>
            </header>

            <button 
              onClick={() => navigate('/fleet-dashboard')}
              className="action-card fleet-card"
            >
              <div className="card-icon">
                <Icons.BarChart size={32} color="white" />
              </div>
              <div className="card-text">
                <span className="card-title">Manage Operations</span>
                <span className="card-subtitle">Monitor vehicles and drivers</span>
              </div>
            </button>

            <button onClick={() => navigate('/app/rider-dashboard')} className="ghost-button">
              Book a personal ride
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default UserHome;