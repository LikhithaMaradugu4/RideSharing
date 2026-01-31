import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import riderService from '../../services/rider.service';
import './RiderTripStatus.css';

// Status messages and colors
const STATUS_CONFIG = {
  REQUESTED: {
    message: 'Finding a driver for you...',
    icon: '🔍',
    color: '#6366f1',
    showCancel: true
  },
  DISPATCHING: {
    message: 'Looking for nearby drivers...',
    icon: '📡',
    color: '#8b5cf6',
    showCancel: true
  },
  ASSIGNED: {
    message: 'Driver assigned! They are on their way.',
    icon: '🚗',
    color: '#22c55e',
    showCancel: true
  },
  DRIVER_EN_ROUTE: {
    message: 'Driver is heading to your pickup location.',
    icon: '🛣️',
    color: '#22c55e',
    showCancel: true
  },
  ARRIVED: {
    message: 'Driver has arrived at your pickup location!',
    icon: '📍',
    color: '#f59e0b',
    showCancel: false,
    showOTP: true
  },
  PICKED_UP: {
    message: 'You are on your way!',
    icon: '🚀',
    color: '#3b82f6',
    showCancel: false
  },
  IN_PROGRESS: {
    message: 'Trip in progress...',
    icon: '🛤️',
    color: '#3b82f6',
    showCancel: false
  },
  COMPLETED: {
    message: 'Trip completed! Thank you for riding with us.',
    icon: '✅',
    color: '#22c55e',
    showCancel: false,
    isFinal: true
  },
  CANCELLED: {
    message: 'This trip has been cancelled.',
    icon: '❌',
    color: '#ef4444',
    showCancel: false,
    isFinal: true
  },
  FAILED: {
    message: 'Sorry, no drivers are available right now.',
    icon: '😔',
    color: '#ef4444',
    showCancel: false,
    isFinal: true
  }
};

function RiderTripStatus() {
  const { tripId } = useParams();
  const navigate = useNavigate();
  
  const [trip, setTrip] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [otp, setOtp] = useState(null);
  const [otpLoading, setOtpLoading] = useState(false);
  const [cancelling, setCancelling] = useState(false);
  
  const pollingRef = useRef(null);

  useEffect(() => {
    if (!tripId) {
      navigate('/app/rider-dashboard');
      return;
    }
    
    fetchTripStatus();
    
    // Start polling
    pollingRef.current = setInterval(fetchTripStatus, 5000); // Poll every 5 seconds
    
    return () => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
      }
    };
  }, [tripId]);

  useEffect(() => {
    // Auto-generate OTP when driver arrives
    if (trip?.status === 'ARRIVED' && !otp) {
      generateOTP();
    }
    
    // Stop polling for final states
    if (trip && STATUS_CONFIG[trip.status]?.isFinal) {
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
        pollingRef.current = null;
      }
    }
  }, [trip?.status]);

  const fetchTripStatus = async () => {
    try {
      const tripData = await riderService.getTripDetails(tripId);
      setTrip(tripData);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch trip status:', err);
      setError('Failed to load trip status');
    } finally {
      setLoading(false);
    }
  };

  const generateOTP = async () => {
    try {
      setOtpLoading(true);
      const result = await riderService.generatePickupOTP(tripId);
      setOtp(result.otp || result.pickup_otp);
    } catch (err) {
      console.error('Failed to generate OTP:', err);
      // OTP might already exist, try fetching from trip
      if (trip?.pickup_otp) {
        setOtp(trip.pickup_otp);
      }
    } finally {
      setOtpLoading(false);
    }
  };

  const handleCancel = async () => {
    if (!window.confirm('Are you sure you want to cancel this ride?')) {
      return;
    }
    
    try {
      setCancelling(true);
      await riderService.cancelTrip(tripId);
      
      // Stop polling
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
        pollingRef.current = null;
      }
      
      // Update local state immediately to show cancelled status
      setTrip(prev => prev ? { ...prev, status: 'CANCELLED' } : prev);
      
      // Also fetch fresh data from server
      try {
        const tripData = await riderService.getTripDetails(tripId);
        setTrip(tripData);
      } catch (fetchErr) {
        // If fetch fails, we already updated the status locally
        console.log('Could not fetch updated trip, using local state');
      }
    } catch (err) {
      setError(err.message || 'Failed to cancel ride');
    } finally {
      setCancelling(false);
    }
  };

  const handleBackToDashboard = () => {
    navigate('/app/rider-dashboard');
  };

  const getStatusConfig = () => {
    if (!trip) return STATUS_CONFIG.REQUESTED;
    return STATUS_CONFIG[trip.status] || STATUS_CONFIG.REQUESTED;
  };

  const formatPhoneNumber = (phone) => {
    if (!phone) return 'N/A';
    // Mask middle digits for privacy
    if (phone.length >= 10) {
      return phone.slice(0, 3) + '****' + phone.slice(-3);
    }
    return phone;
  };

  if (loading) {
    return (
      <div className="trip-status-page">
        <div className="loading-state">
          <div className="spinner"></div>
          <span>Loading trip details...</span>
        </div>
      </div>
    );
  }

  const statusConfig = getStatusConfig();

  return (
    <div className="trip-status-page">
      <div className="trip-status-container">
        {/* Header */}
        <header className="trip-header">
          <button className="btn-back" onClick={handleBackToDashboard}>
            ← Back
          </button>
          <h1>Trip Status</h1>
          <span className="trip-id">#{tripId?.slice(-8)}</span>
        </header>

        {error && (
          <div className="error-banner">
            <span>⚠️ {error}</span>
            <button onClick={() => setError(null)}>×</button>
          </div>
        )}

        {/* Status Display */}
        <div 
          className="status-display"
          style={{ borderColor: statusConfig.color }}
        >
          <div 
            className="status-icon"
            style={{ backgroundColor: statusConfig.color + '20' }}
          >
            <span>{statusConfig.icon}</span>
          </div>
          <div className="status-message">
            <span style={{ color: statusConfig.color }}>{statusConfig.message}</span>
          </div>
          
          {/* Progress indicator for non-final states */}
          {!statusConfig.isFinal && (
            <div className="status-progress">
              <div 
                className="progress-bar"
                style={{ backgroundColor: statusConfig.color }}
              ></div>
            </div>
          )}
        </div>

        {/* OTP Display - Only when driver arrives */}
        {statusConfig.showOTP && (
          <div className="otp-section" style={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            borderRadius: '16px',
            padding: '24px',
            marginBottom: '20px',
            textAlign: 'center',
            color: 'white'
          }}>
            <h3 style={{ margin: '0 0 8px 0', fontSize: '20px' }}>🔐 Your Pickup OTP</h3>
            <p style={{ margin: '0 0 20px 0', opacity: 0.9, fontSize: '14px' }}>
              Share this code with your driver to start the trip
            </p>
            
            {otpLoading ? (
              <div style={{ fontSize: '16px', padding: '20px' }}>⏳ Generating OTP...</div>
            ) : (otp || trip?.pickup_otp) ? (
              <div style={{
                background: 'white',
                borderRadius: '12px',
                padding: '20px 30px',
                display: 'inline-block'
              }}>
                <span style={{
                  fontSize: '36px',
                  fontWeight: '700',
                  letterSpacing: '8px',
                  color: '#1f2937',
                  fontFamily: 'monospace'
                }}>
                  {otp || trip?.pickup_otp}
                </span>
              </div>
            ) : (
              <button 
                onClick={generateOTP}
                style={{
                  background: 'white',
                  color: '#667eea',
                  border: 'none',
                  borderRadius: '10px',
                  padding: '14px 28px',
                  fontSize: '16px',
                  fontWeight: '600',
                  cursor: 'pointer'
                }}
              >
                Generate OTP
              </button>
            )}
            
            <p style={{ margin: '16px 0 0 0', opacity: 0.8, fontSize: '12px' }}>
              ⚠️ Do not share this code with anyone except your driver
            </p>
          </div>
        )}

        {/* Driver Info - When assigned */}
        {trip?.driver && (trip.status === 'ASSIGNED' || trip.status === 'DRIVER_EN_ROUTE' || trip.status === 'ARRIVED' || trip.status === 'PICKED_UP' || trip.status === 'IN_PROGRESS') && (
          <div className="driver-info-section">
            <h3>🧑‍✈️ Your Driver</h3>
            <div className="driver-card">
              <div className="driver-avatar">
                {trip.driver.full_name?.charAt(0) || 'D'}
              </div>
              <div className="driver-details">
                <span className="driver-name">{trip.driver.full_name || 'Driver'}</span>
                <span className="driver-phone">
                  📞 {formatPhoneNumber(trip.driver.phone_number)}
                </span>
              </div>
            </div>
            
            {/* Vehicle info */}
            {trip.vehicle && (
              <div className="vehicle-info">
                <span className="vehicle-type">
                  {trip.vehicle.vehicle_category === 'BIKE' ? '🏍️' : 
                   trip.vehicle.vehicle_category === 'AUTO' ? '🛺' : '🚗'}
                  {' '}{trip.vehicle.vehicle_category || 'Vehicle'}
                </span>
                <span className="vehicle-number">
                  {trip.vehicle.registration_number || 'N/A'}
                </span>
              </div>
            )}
          </div>
        )}

        {/* Trip Details */}
        {trip && (
          <div className="trip-details-section">
            <h3>📋 Trip Details</h3>
            <div className="trip-details-card">
              <div className="detail-row">
                <span className="detail-label">
                  <span className="pickup-dot">●</span> Pickup
                </span>
                <span className="detail-value">
                  {trip.pickup_location?.lat ? `${parseFloat(trip.pickup_location.lat).toFixed(4)}, ${parseFloat(trip.pickup_location.lng).toFixed(4)}` : '--'}
                </span>
              </div>
              
              <div className="detail-row">
                <span className="detail-label">
                  <span className="drop-dot">●</span> Drop-off
                </span>
                <span className="detail-value">
                  {trip.drop_location?.lat ? `${parseFloat(trip.drop_location.lat).toFixed(4)}, ${parseFloat(trip.drop_location.lng).toFixed(4)}` : '--'}
                </span>
              </div>
              
              <div className="detail-divider"></div>
              
              <div className="detail-row">
                <span className="detail-label">Distance</span>
                <span className="detail-value">{trip.distance_km ? parseFloat(trip.distance_km).toFixed(1) : '--'} km</span>
              </div>
              
              <div className="detail-row fare">
                <span className="detail-label">Fare</span>
                <span className="detail-value">₹{trip.fare_amount ? parseFloat(trip.fare_amount).toFixed(0) : (trip.estimated_fare ? parseFloat(trip.estimated_fare).toFixed(0) : '--')}</span>
              </div>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="trip-actions">
          {statusConfig.showCancel && (
            <button 
              className="btn-cancel"
              onClick={handleCancel}
              disabled={cancelling}
            >
              {cancelling ? 'Cancelling...' : 'Cancel Ride'}
            </button>
          )}
          
          {statusConfig.isFinal && (
            <button 
              className="btn-primary btn-new-ride"
              onClick={handleBackToDashboard}
            >
              Book Another Ride
            </button>
          )}
        </div>

        {/* Completed Trip Summary */}
        {trip?.status === 'COMPLETED' && (
          <div className="trip-summary">
            <h3>🎉 Trip Summary</h3>
            <div className="summary-card">
              <div className="summary-row">
                <span>Trip Fare</span>
                <span>₹{trip.fare_amount ? parseFloat(trip.fare_amount).toFixed(0) : (trip.estimated_fare ? parseFloat(trip.estimated_fare).toFixed(0) : '--')}</span>
              </div>
              <div className="summary-row">
                <span>Distance</span>
                <span>{trip.distance_km ? parseFloat(trip.distance_km).toFixed(1) : '--'} km</span>
              </div>
              <div className="summary-row">
                <span>Payment</span>
                <span>{trip.payment_method || 'Cash'}</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default RiderTripStatus;
