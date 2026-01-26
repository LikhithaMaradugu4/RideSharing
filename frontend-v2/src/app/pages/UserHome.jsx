import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import userService from '../../services/user.service';
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

      // Get token from localStorage (stored during OTP login)
      const token = localStorage.getItem('jwt_token');
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

  const handleRiderClick = () => {
    navigate('/app/rider-dashboard');
  };

  const handleApplyDriver = () => {
    navigate('/driver-tenant-selection');
  };

  const handleContinueDriver = () => {
    navigate('/app/driver/dashboard');
  };

  const handleReapplyDriver = () => {
    navigate('/driver-tenant-selection');
  };

  const handleApplyFleetOwner = () => {
    navigate('/fleet-owner-tenant-selection');
  };

  const handleContinueFleetOwner = () => {
    navigate('/app/fleet-owner-dashboard');
  };

  if (loading) {
    return (
      <div className="user-home-container">
        <div className="loading">Loading your capabilities...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="user-home-container">
        <div className="error-message">{error}</div>
        <button onClick={fetchCapabilities} className="retry-button">
          Try Again
        </button>
      </div>
    );
  }

  if (!capabilities) {
    return (
      <div className="user-home-container">
        <div className="error-message">No capabilities data available</div>
      </div>
    );
  }

  // Extract capability states
  const driverExists = capabilities.driver?.exists || false;
  const driverStatus = capabilities.driver?.approval_status;
  
  const fleetOwnerExists = capabilities.fleet_owner?.exists || false;
  const fleetOwnerStatus = capabilities.fleet_owner?.approval_status;

  return (
    <div className="user-home-container">
      {/* Header */}
      <div className="user-home-header">
        <h1>Welcome back</h1>
        <p className="subtitle">Choose how you want to continue</p>
      </div>

      {/* Main Content */}
      <div className="capabilities-section">
        {/* RIDER CARD - Always visible */}
        <div className="capability-card rider-card">
          <div className="card-header">
            <h2>Rider</h2>
          </div>
          <div className="card-body">
            <p className="description">Book rides and travel easily.</p>
          </div>
          <div className="card-footer">
            <button
              onClick={handleRiderClick}
              className="action-button primary"
            >
              Continue as Rider
            </button>
          </div>
        </div>

        {/* DRIVER CARD */}
        <div className="capability-card driver-card">
          <div className="card-header">
            <h2>Driver</h2>
          </div>
          <div className="card-body">
            {!driverExists && (
              <p className="description">
                Drive and earn by accepting ride requests.
              </p>
            )}
            {driverExists && driverStatus === 'PENDING' && (
              <p className="status-text pending">
                Application under review
              </p>
            )}
            {driverExists && driverStatus === 'APPROVED' && (
              <p className="status-text approved">
                Application approved
              </p>
            )}
            {driverExists && driverStatus === 'REJECTED' && (
              <p className="status-text rejected">
                Application rejected
              </p>
            )}
          </div>
          <div className="card-footer">
            {!driverExists && (
              <button
                onClick={handleApplyDriver}
                className="action-button primary"
              >
                Apply as Driver
              </button>
            )}
            {driverExists && driverStatus === 'PENDING' && (
              <button className="action-button disabled" disabled>
                Application in Review
              </button>
            )}
            {driverExists && driverStatus === 'APPROVED' && (
              <button
                onClick={handleContinueDriver}
                className="action-button primary"
              >
                Continue as Driver
              </button>
            )}
            {driverExists && driverStatus === 'REJECTED' && (
              <button
                onClick={handleReapplyDriver}
                className="action-button secondary"
              >
                Re-apply as Driver
              </button>
            )}
          </div>
        </div>

        {/* FLEET OWNER CARD */}
        <div className="capability-card fleet-card">
          <div className="card-header">
            <h2>Fleet Owner</h2>
          </div>
          <div className="card-body">
            {!fleetOwnerExists && (
              <p className="description">
                Manage drivers and vehicles as a fleet owner.
              </p>
            )}
            {fleetOwnerExists && fleetOwnerStatus === 'PENDING' && (
              <p className="status-text pending">
                Application under review
              </p>
            )}
            {fleetOwnerExists && fleetOwnerStatus === 'APPROVED' && (
              <p className="status-text approved">
                Application approved
              </p>
            )}
            {fleetOwnerExists && fleetOwnerStatus === 'REJECTED' && (
              <p className="status-text rejected">
                Application rejected
              </p>
            )}
          </div>
          <div className="card-footer">
            {!fleetOwnerExists && (
              <button
                onClick={handleApplyFleetOwner}
                className="action-button primary"
              >
                Apply as Fleet Owner
              </button>
            )}
            {fleetOwnerExists && fleetOwnerStatus === 'PENDING' && (
              <button className="action-button disabled" disabled>
                Application in Review
              </button>
            )}
            {fleetOwnerExists && fleetOwnerStatus === 'APPROVED' && (
              <button
                onClick={handleContinueFleetOwner}
                className="action-button primary"
              >
                Continue as Fleet Owner
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default UserHome;
