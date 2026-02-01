import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import riderService from '../../services/rider.service';
import fleetService from '../../services/fleet.service';
import './RiderDashboard.css';

function RiderDashboard() {
  const navigate = useNavigate();
  const token = localStorage.getItem('jwt_token');
  
  // User state
  const [userInfo, setUserInfo] = useState(null);
  const [fleetData, setFleetData] = useState(null); // null = not checked, false = no fleet, object = fleet exists
  const [fleetChecked, setFleetChecked] = useState(false);
  const [loading, setLoading] = useState(true);
  const [checkingTrip, setCheckingTrip] = useState(true);

  useEffect(() => {
    if (!token) {
      navigate('/login');
      return;
    }
    
    fetchUserInfo();
    checkFleetExists();
    checkActiveTrip();
  }, [token, navigate]);

  const fetchUserInfo = async () => {
    try {
      const user = JSON.parse(localStorage.getItem('user_info') || '{}');
      setUserInfo(user);
    } catch (err) {
      console.error('Failed to get user info:', err);
    } finally {
      setLoading(false);
    }
  };

  const checkFleetExists = async () => {
    try {
      const fleet = await fleetService.checkFleetExists();
      setFleetData(fleet);
    } catch (err) {
      console.error('Failed to check fleet:', err);
      setFleetData(null);
    } finally {
      setFleetChecked(true);
    }
  };

  const checkActiveTrip = async () => {
    try {
      const response = await riderService.getActiveTrip();
      if (response && response.active_trip) {
        navigate(`/app/rider/trip/${response.active_trip.trip_id}`);
      }
    } catch (err) {
      // No active trip - stay on dashboard
      console.log('No active trip');
    } finally {
      setCheckingTrip(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('jwt_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_info');
    navigate('/login');
  };

  const handleBookRide = () => {
    navigate('/app/rider/book');
  };

  const handleProfile = () => {
    navigate('/app/profile');
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  };

  const getFirstName = () => {
    if (!userInfo?.full_name) return '';
    return userInfo.full_name.split(' ')[0];
  };

  if (loading || checkingTrip) {
    return (
      <div className="rider-dashboard">
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <span>Loading...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="rider-dashboard">
      {/* Header */}
      <header className="rider-header">
        <div className="header-left">
          <h1>🚕 RideShare</h1>
        </div>
        <div className="header-right">
          <button className="btn-profile" onClick={handleProfile} title="Profile">
            👤
          </button>
          <button className="btn-logout" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </header>

      {/* Main Content */}
      <div className="dashboard-main">
        {/* Greeting Section */}
        <div className="greeting-section">
          <h2 className="greeting-text">
            {getGreeting()}{getFirstName() ? `, ${getFirstName()}` : ''}! 👋
          </h2>
          <p className="greeting-subtitle">Where would you like to go today?</p>
        </div>

        {/* Primary CTA - Book a Ride */}
        <div className="cta-section">
          <button className="btn-book-ride" onClick={handleBookRide}>
            <div className="btn-content">
              <span className="btn-icon">🚗</span>
              <div className="btn-text-wrapper">
                <span className="btn-title">Book a Ride</span>
                <span className="btn-subtitle">Select pickup & destination on map</span>
              </div>
            </div>
            <span className="btn-arrow">→</span>
          </button>
        </div>

        {/* Quick Stats */}
        <div className="info-cards">
          <div className="info-card">
            <span className="info-icon">📍</span>
            <span className="info-text">Available in your area</span>
          </div>
          <div className="info-card">
            <span className="info-icon">⚡</span>
            <span className="info-text">Fast pickup times</span>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="quick-actions">
          <button className="action-card" onClick={handleProfile}>
            <span className="action-icon">👤</span>
            <span className="action-text">Profile</span>
          </button>
          <button className="action-card" onClick={() => navigate('/app/rider/history')}>
            <span className="action-icon">📋</span>
            <span className="action-text">Trip History</span>
          </button>
          <button className="action-card" onClick={() => navigate('/app/help')}>
            <span className="action-icon">❓</span>
            <span className="action-text">Help</span>
          </button>
        </div>

        {/* Become a Partner Section */}
        <div className="partner-section">
          <h4>Want to earn with us?</h4>
          <div className="partner-buttons">
            {/* Show Drive with us - always available for riders */}
            <button 
              className="btn-partner"
              onClick={() => navigate('/driver-tenant-selection')}
            >
              <span className="partner-icon">🚘</span>
              <span className="partner-text">Drive with us</span>
            </button>
            
            {/* Show Fleet Partner only if NO fleet exists (any status) */}
            {fleetChecked && !fleetData && (
              <button 
                className="btn-partner"
                onClick={() => navigate('/fleet-owner-tenant-selection')}
              >
                <span className="partner-icon">🏢</span>
                <span className="partner-text">Fleet Partner</span>
              </button>
            )}
            
            {/* If user has approved fleet, show link to fleet dashboard */}
            {fleetData && fleetData.approval_status === 'APPROVED' && (
              <button 
                className="btn-partner"
                onClick={() => navigate('/fleet-dashboard')}
              >
                <span className="partner-icon">🏢</span>
                <span className="partner-text">Go to Fleet Dashboard</span>
              </button>
            )}
          </div>
          
          {/* Show pending fleet status */}
          {fleetData && fleetData.approval_status === 'PENDING' && (
            <p style={{color: '#f59e0b', marginTop: '0.5rem', fontSize: '0.9rem'}}>
              ⏳ Your fleet application is under review
            </p>
          )}
          
          {/* Show rejected fleet status */}
          {fleetData && fleetData.approval_status === 'REJECTED' && (
            <p style={{color: '#ef4444', marginTop: '0.5rem', fontSize: '0.9rem'}}>
              ❌ Your fleet application was rejected
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

export default RiderDashboard;
