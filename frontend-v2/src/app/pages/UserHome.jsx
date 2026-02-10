import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import userService from '../../services/user.service';
import tokenStorage from '../../services/tokenStorage';
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
      <div className="user-home-container">
        <div className="loading">Loading...</div>
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
  const isApprovedDriver = driverExists && driverStatus === 'APPROVED';
  
  const fleetOwnerExists = capabilities.fleet_owner?.exists || false;
  const fleetOwnerStatus = capabilities.fleet_owner?.approval_status;
  const isApprovedFleetOwner = fleetOwnerExists && fleetOwnerStatus === 'APPROVED';

  // Determine primary identity
  const isDriver = isApprovedDriver;
  const isFleetOwner = isApprovedFleetOwner;
  const isOnlyRider = !isDriver && !isFleetOwner;

  return (
    <div className="user-home-container">
      
      {/* CASE 1: ONLY RIDER (Default behavior) */}
      {isOnlyRider && (
        <>
          <div className="primary-action-section">
            <h1 className="main-heading">Where would you like to go?</h1>
            <button 
              onClick={() => navigate('/app/rider-dashboard')}
              className="primary-action-button"
            >
              Book a Ride
            </button>
          </div>

          <div className="secondary-actions">
            <p className="earn-heading">Want to earn with us?</p>
            <div className="secondary-links">
              <button 
                onClick={() => navigate('/driver-tenant-selection')}
                className="secondary-link"
              >
                Drive with us →
              </button>
              <button 
                onClick={() => navigate('/fleet-owner-tenant-selection')}
                className="secondary-link"
              >
                Maintain a fleet →
              </button>
            </div>
          </div>
        </>
      )}

      {/* CASE 2: APPROVED DRIVER */}
      {isDriver && !isFleetOwner && (
        <>
          <div className="primary-action-section">
            <h1 className="main-heading">Ready to earn?</h1>
            <button 
              onClick={() => navigate('/app/driver/dashboard')}
              className="primary-action-button driver-primary"
            >
              Start Driving
            </button>
          </div>

          <div className="secondary-actions">
            <button 
              onClick={() => navigate('/app/rider-dashboard')}
              className="secondary-action-button"
            >
              Book a ride instead
            </button>
          </div>
        </>
      )}

      {/* CASE 3: APPROVED FLEET OWNER */}
      {isFleetOwner && (
        <>
          <div className="primary-action-section">
            <h1 className="main-heading">Manage your operations</h1>
            <button 
              onClick={() => navigate('/fleet-dashboard')}
              className="primary-action-button fleet-primary"
            >
              Manage Fleet
            </button>
          </div>

          <div className="secondary-actions">
            <button 
              onClick={() => navigate('/app/rider-dashboard')}
              className="secondary-action-button"
            >
              Book a ride instead
            </button>
          </div>
        </>
      )}

    </div>
  );
}

export default UserHome;