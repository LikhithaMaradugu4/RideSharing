import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import driverService from '../../services/driver.service';
import userService from '../../services/user.service';
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
  const [shiftReadiness, setShiftReadiness] = useState(null);
  
  // Vehicle selection for independent drivers
  const [isIndependent, setIsIndependent] = useState(false);
  const [approvedVehicles, setApprovedVehicles] = useState([]);
  const [selectedVehicleId, setSelectedVehicleId] = useState(null);
  const [vehicleSelecting, setVehicleSelecting] = useState(false);
  const [showVehicleSelector, setShowVehicleSelector] = useState(false);

  // ========== NEW: Dispatch & Trip State ==========
  const [pendingDispatches, setPendingDispatches] = useState([]);
  const [activeTrip, setActiveTrip] = useState(null);
  const [tripActionLoading, setTripActionLoading] = useState(false);
  const [otpInput, setOtpInput] = useState('');
  const [otpVerified, setOtpVerified] = useState(false);
  const [dispatchPollingActive, setDispatchPollingActive] = useState(false);

  // Polling refs
  const dispatchPollingRef = useRef(null);
  const tripPollingRef = useRef(null);

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

      // Fetch capabilities to check if independent driver
      try {
        const capabilities = await userService.getCapabilities(token);
        const driverInfo = capabilities?.driver || {};
        const independent = driverInfo.is_independent ?? false;
        setIsIndependent(independent);
        
        // For independent drivers, fetch approved vehicles
        if (independent) {
          try {
            const vehicles = await driverService.getApprovedVehicles(token);
            setApprovedVehicles(vehicles || []);
            
            // Find currently assigned vehicle
            const currentVehicle = vehicles?.find(v => v.is_currently_assigned);
            if (currentVehicle) {
              setSelectedVehicleId(currentVehicle.vehicle_id);
              setActiveVehicle({
                registration: currentVehicle.registration_no,
                category: currentVehicle.category,
                status: currentVehicle.approval_status
              });
            }
          } catch (vehicleErr) {
            console.error('Failed to fetch approved vehicles:', vehicleErr);
            setApprovedVehicles([]);
          }
        }
      } catch (capErr) {
        console.error('Failed to fetch capabilities:', capErr);
        setIsIndependent(false);
      }

      // Fetch active shift
      try {
        const shift = await driverService.getActiveShift(token);
        setShiftStatus(shift);
      } catch (err) {
        setShiftStatus(null);
      }

      // Fetch shift readiness to show missing requirements
      try {
        const readiness = await driverService.checkShiftReadiness(token);
        setShiftReadiness(readiness);
        
        // Populate activeFleet from readiness data
        if (readiness?.checks?.fleet_association?.exists) {
          setActiveFleet({
            id: readiness.checks.fleet_association.fleet_id,
            name: readiness.checks.fleet_association.fleet_name,
            type: readiness.checks.fleet_association.fleet_type,
            approval_status: readiness.checks.fleet_association.fleet_approval_status
          });
        } else {
          setActiveFleet(null);
        }
        
        // Populate activeVehicle from readiness data (for non-independent or as fallback)
        if (readiness?.checks?.vehicle_assignment?.exists) {
          setActiveVehicle({
            vehicle_id: readiness.checks.vehicle_assignment.vehicle_id,
            assignment_id: readiness.checks.vehicle_assignment.assignment_id,
            registration: readiness.checks.vehicle_assignment.registration_no,
            category: null, // Not in readiness response, would need to fetch
            status: readiness.checks.vehicle_assignment.vehicle_approval_status,
            is_approved: readiness.checks.vehicle_assignment.is_vehicle_approved,
            documents_complete: readiness.checks.vehicle_assignment.documents_complete,
            missing_documents: readiness.checks.vehicle_assignment.missing_documents || []
          });
        } else if (!isIndependent) {
          // Only clear if not independent (independent drivers set it from approved vehicles)
          setActiveVehicle(null);
        }
      } catch (err) {
        console.error('Failed to fetch shift readiness:', err);
        setShiftReadiness(null);
      }

      // Fetch active trip (if any)
      try {
        const trip = await driverService.getActiveTrip(token);
        setActiveTrip(trip);
        if (trip) {
          // Reset OTP state when trip changes
          setOtpInput('');
          setOtpVerified(false);
        }
      } catch (err) {
        console.error('Failed to fetch active trip:', err);
        setActiveTrip(null);
      }

    } catch (err) {
      setError(err.message || 'Failed to load dashboard');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  // ========== Dispatch Polling ==========
  const fetchPendingDispatches = useCallback(async () => {
    if (!token) return;
    try {
      const dispatches = await driverService.getPendingDispatches(token);
      setPendingDispatches(dispatches || []);
    } catch (err) {
      console.error('Failed to fetch pending dispatches:', err);
      setPendingDispatches([]);
    }
  }, [token]);

  const fetchActiveTrip = useCallback(async () => {
    if (!token) return;
    try {
      const trip = await driverService.getActiveTrip(token);
      setActiveTrip(trip);
    } catch (err) {
      console.error('Failed to fetch active trip:', err);
    }
  }, [token]);

  // Start/stop polling based on shift status
  useEffect(() => {
    const isOnline = shiftStatus?.shift_status === 'ONLINE' || shiftStatus?.is_online;
    const isBusy = shiftStatus?.shift_status === 'BUSY';

    // If ONLINE and no active trip, poll for dispatches
    if (isOnline && !isBusy && !activeTrip) {
      setDispatchPollingActive(true);
      fetchPendingDispatches();
      dispatchPollingRef.current = setInterval(fetchPendingDispatches, 5000);
    } else {
      setDispatchPollingActive(false);
      if (dispatchPollingRef.current) {
        clearInterval(dispatchPollingRef.current);
        dispatchPollingRef.current = null;
      }
      setPendingDispatches([]);
    }

    // If BUSY or has active trip, poll for trip updates
    if (isBusy || activeTrip) {
      tripPollingRef.current = setInterval(fetchActiveTrip, 5000);
    } else {
      if (tripPollingRef.current) {
        clearInterval(tripPollingRef.current);
        tripPollingRef.current = null;
      }
    }

    return () => {
      if (dispatchPollingRef.current) {
        clearInterval(dispatchPollingRef.current);
      }
      if (tripPollingRef.current) {
        clearInterval(tripPollingRef.current);
      }
    };
  }, [shiftStatus, activeTrip, fetchPendingDispatches, fetchActiveTrip]);

  // ========== Dispatch Handlers ==========
  const handleAcceptDispatch = async (attemptId) => {
    try {
      setTripActionLoading(true);
      setError(null);
      await driverService.acceptDispatch(token, attemptId);
      // Fetch the newly assigned trip
      await fetchActiveTrip();
      // Clear pending dispatches
      setPendingDispatches([]);
      // Refresh shift status (should be BUSY now)
      const newShift = await driverService.getActiveShift(token);
      setShiftStatus(newShift);
    } catch (err) {
      setError(err.message || 'Failed to accept dispatch');
    } finally {
      setTripActionLoading(false);
    }
  };

  const handleRejectDispatch = async (attemptId) => {
    try {
      setTripActionLoading(true);
      setError(null);
      await driverService.rejectDispatch(token, attemptId);
      // Remove from pending list
      setPendingDispatches(prev => prev.filter(d => d.attempt_id !== attemptId));
    } catch (err) {
      setError(err.message || 'Failed to reject dispatch');
    } finally {
      setTripActionLoading(false);
    }
  };

  // ========== Trip Action Handlers ==========
  const handleMarkArrived = async () => {
    if (!activeTrip) return;
    try {
      setTripActionLoading(true);
      setError(null);
      await driverService.markArrived(token, activeTrip.trip_id);
      await fetchActiveTrip();
    } catch (err) {
      setError(err.message || 'Failed to mark arrival');
    } finally {
      setTripActionLoading(false);
    }
  };

  const handleVerifyOTP = async () => {
    if (!activeTrip || !otpInput) return;
    try {
      setTripActionLoading(true);
      setError(null);
      const result = await driverService.verifyPickupOTP(token, activeTrip.trip_id, otpInput);
      if (result.verified) {
        setOtpVerified(true);
      } else {
        setError(result.message || 'Invalid OTP');
      }
    } catch (err) {
      setError(err.message || 'Failed to verify OTP');
    } finally {
      setTripActionLoading(false);
    }
  };

  const handleConfirmPickup = async () => {
    if (!activeTrip) return;
    try {
      setTripActionLoading(true);
      setError(null);
      await driverService.confirmPickup(token, activeTrip.trip_id);
      await fetchActiveTrip();
    } catch (err) {
      setError(err.message || 'Failed to confirm pickup');
    } finally {
      setTripActionLoading(false);
    }
  };

  const handleCompleteTrip = async () => {
    if (!activeTrip) return;
    try {
      setTripActionLoading(true);
      setError(null);
      const result = await driverService.completeTrip(token, activeTrip.trip_id);
      setActiveTrip(null);
      setOtpInput('');
      setOtpVerified(false);
      // Refresh shift status (should be ONLINE again)
      const newShift = await driverService.getActiveShift(token);
      setShiftStatus(newShift);
      // Show success message
      setError(null);
      alert(`Trip completed! Fare: ₹${result.fare_amount?.toFixed(0) || '--'}`);
    } catch (err) {
      setError(err.message || 'Failed to complete trip');
    } finally {
      setTripActionLoading(false);
    }
  };

  const handleSelectVehicle = async (vehicleId, endShiftIfActive = false) => {
    try {
      setVehicleSelecting(true);
      setError(null);
      
      // Check if driver is currently online
      const isCurrentlyOnline = shiftStatus?.is_online || shiftStatus?.shift_status === 'ONLINE' || shiftStatus?.shift_status === 'BUSY';
      
      // If there's an active shift and user hasn't confirmed, ask for confirmation
      if (isCurrentlyOnline && !endShiftIfActive) {
        const confirmSwitch = window.confirm(
          'You are currently online. Switching vehicles will end your current shift. Continue?'
        );
        if (!confirmSwitch) {
          setVehicleSelecting(false);
          return;
        }
        endShiftIfActive = true;
      }
      
      const result = await driverService.selectVehicle(token, vehicleId, endShiftIfActive);
      
      setSelectedVehicleId(result.vehicle_id);
      setActiveVehicle({
        registration: result.registration_no,
        category: result.category,
        status: result.approval_status
      });
      
      // Update the list to reflect new assignment
      setApprovedVehicles(prev => prev.map(v => ({
        ...v,
        is_currently_assigned: v.vehicle_id === result.vehicle_id
      })));
      
      // If we ended the shift, update shift status
      if (endShiftIfActive && isCurrentlyOnline) {
        setShiftStatus(null);
      }
      
      setShowVehicleSelector(false);
    } catch (err) {
      setError(err.message || 'Failed to select vehicle');
    } finally {
      setVehicleSelecting(false);
    }
  };

  const handleShiftToggle = async () => {
    try {
      setShiftToggling(true);
      setError(null);

      const isCurrentlyOnline = shiftStatus?.is_online || shiftStatus?.shift_status === 'ONLINE' || shiftStatus?.shift_status === 'BUSY';

      if (isCurrentlyOnline) {
        // End shift
        await driverService.endShift(token);
      } else {
        // Start shift
        await driverService.startShift(token);
      }

      // Always refresh shift status from server to ensure sync
      try {
        const newStatus = await driverService.getActiveShift(token);
        setShiftStatus(newStatus);
      } catch (refreshErr) {
        // If no active shift, set to null (offline)
        setShiftStatus(null);
      }
    } catch (err) {
      // Provide helpful error messages
      let errorMessage = err.message || 'Failed to toggle shift';
      if (err.message?.includes('no active fleet association')) {
        errorMessage = 'You are not associated with any fleet. Please contact your fleet manager or register as an independent driver.';
      } else if (err.message?.includes('no active vehicle assignment')) {
        errorMessage = 'No vehicle assigned. Please select a vehicle first.';
      } else if (err.message?.includes('Vehicle missing documents')) {
        errorMessage = err.message;
      }
      setError(errorMessage);
      console.error('Error:', err);
      
      // Refresh shift status to sync with server state
      try {
        const actualStatus = await driverService.getActiveShift(token);
        setShiftStatus(actualStatus);
      } catch (refreshErr) {
        setShiftStatus(null);
      }
    } finally {
      setShiftToggling(false);
    }
  };

  const getShiftStatusLabel = () => {
    if (!shiftStatus) return 'OFFLINE';
    // Handle both DriverShiftResponse (status) and ShiftStatusResponse (shift_status)
    return shiftStatus.shift_status || shiftStatus.status || 'OFFLINE';
  };

  const getShiftStatusColor = () => {
    const status = shiftStatus?.shift_status || shiftStatus?.status;
    if (!status || status === 'OFFLINE') return '#f44336'; // Red for offline
    if (status === 'BUSY') return '#ff9800'; // Orange for busy
    if (status === 'ONLINE') return '#4caf50'; // Green for online
    return '#f44336';
  };

  // Helper to check if driver is currently online
  const isDriverOnline = () => {
    return shiftStatus?.is_online || shiftStatus?.shift_status === 'ONLINE' || shiftStatus?.shift_status === 'BUSY';
  };

  // Helper to check if driver is busy (on a trip)
  const isDriverBusy = () => {
    const status = shiftStatus?.shift_status || shiftStatus?.status;
    return status === 'BUSY';
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
              className={`shift-toggle-btn ${isDriverOnline() ? 'go-offline' : 'go-online'}`}
              onClick={handleShiftToggle}
              disabled={shiftToggling || isDriverBusy() || (!isDriverOnline() && shiftReadiness && !shiftReadiness.can_go_online)}
              title={isDriverBusy() ? 'Cannot go offline during trip' : (isDriverOnline() ? 'Go Offline' : 'Go Online')}
            >
              {shiftToggling ? 'Processing...' : (isDriverOnline() ? 'Go Offline' : 'Go Online')}
            </button>

            {isDriverBusy() && (
              <div className="shift-warning">
                <span>You are currently on a trip</span>
              </div>
            )}

            {!isDriverOnline() && shiftReadiness && !shiftReadiness.can_go_online && (
              <div className="shift-requirements">
                <h4>⚠️ Cannot Go Online - Missing Requirements:</h4>
                <ul>
                  {!shiftReadiness.checks?.fleet_association?.exists && (
                    <li className="requirement-missing">No fleet association. Please contact your fleet manager.</li>
                  )}
                  {shiftReadiness.checks?.fleet_association?.exists && !shiftReadiness.checks?.fleet_association?.is_fleet_approved && (
                    <li className="requirement-missing">Fleet not approved. Please wait for tenant approval.</li>
                  )}
                  {!shiftReadiness.checks?.vehicle_assignment?.exists && (
                    <li className="requirement-missing">No vehicle assigned. {isIndependent ? 'Please select a vehicle.' : 'Please contact your fleet manager.'}</li>
                  )}
                  {shiftReadiness.checks?.vehicle_assignment?.exists && !shiftReadiness.checks?.vehicle_assignment?.is_vehicle_approved && (
                    <li className="requirement-missing">Vehicle not approved. Please wait for tenant approval.</li>
                  )}
                  {shiftReadiness.checks?.vehicle_assignment?.exists && !shiftReadiness.checks?.vehicle_assignment?.documents_complete && (
                    <li className="requirement-missing">
                      Missing vehicle documents: {shiftReadiness.checks?.vehicle_assignment?.missing_documents?.join(', ')}
                    </li>
                  )}
                  {shiftReadiness.checks?.vehicle_assignment?.exists && !shiftReadiness.checks?.vehicle_assignment?.belongs_to_fleet && (
                    <li className="requirement-missing">Vehicle does not belong to your active fleet.</li>
                  )}
                </ul>
              </div>
            )}

            {!isDriverOnline() && shiftReadiness?.can_go_online && (
              <div className="shift-info">
                <span>✅ Ready! Click "Go Online" to start accepting trips</span>
              </div>
            )}

            {!isDriverOnline() && !shiftReadiness && (
              <div className="shift-info">
                <span>Click "Go Online" to start accepting trips</span>
              </div>
            )}
          </div>
        </div>

        {/* ========== NEW: Readiness Banner ========== */}
        <div className="readiness-banner-section">
          {isDriverOnline() && !isDriverBusy() && !activeTrip && (
            <div className="readiness-banner ready">
              <span className="readiness-icon">✅</span>
              <span className="readiness-text">You are ONLINE and ready for trips</span>
            </div>
          )}
          {isDriverBusy() && activeTrip && (
            <div className="readiness-banner busy">
              <span className="readiness-icon">🚗</span>
              <span className="readiness-text">You are on an active trip</span>
            </div>
          )}
          {!isDriverOnline() && (
            <div className="readiness-banner offline">
              <span className="readiness-icon">⏸️</span>
              <span className="readiness-text">You are OFFLINE - Go online to accept rides</span>
            </div>
          )}
          {isDriverOnline() && !activeVehicle && (
            <div className="readiness-banner warning">
              <span className="readiness-icon">⚠️</span>
              <span className="readiness-text">No active vehicle assigned</span>
            </div>
          )}
        </div>

        {/* ========== NEW: Active Trip Section ========== */}
        {activeTrip && (
          <div className="active-trip-section">
            <div className="trip-card">
              <div className="trip-header">
                <h2>🚗 Active Trip</h2>
                <span className={`trip-status-badge status-${activeTrip.status?.toLowerCase()}`}>
                  {activeTrip.status}
                </span>
              </div>

              <div className="trip-details">
                <div className="trip-detail-row">
                  <span className="detail-label">Trip ID:</span>
                  <span className="detail-value">#{activeTrip.trip_id}</span>
                </div>
                <div className="trip-detail-row">
                  <span className="detail-label">Rider:</span>
                  <span className="detail-value">{activeTrip.rider_name || 'Rider'}</span>
                </div>
                <div className="trip-detail-row">
                  <span className="detail-label">Pickup:</span>
                  <span className="detail-value coordinates">
                    {activeTrip.pickup_lat?.toFixed(4)}, {activeTrip.pickup_lng?.toFixed(4)}
                  </span>
                </div>
                {activeTrip.drop_lat && (
                  <div className="trip-detail-row">
                    <span className="detail-label">Drop:</span>
                    <span className="detail-value coordinates">
                      {activeTrip.drop_lat?.toFixed(4)}, {activeTrip.drop_lng?.toFixed(4)}
                    </span>
                  </div>
                )}
                <div className="trip-detail-row">
                  <span className="detail-label">Fare:</span>
                  <span className="detail-value fare">₹{activeTrip.fare_amount?.toFixed(0) || '--'}</span>
                </div>
              </div>

              {/* State-driven Actions */}
              <div className="trip-actions">
                {/* ASSIGNED State: Show Mark Arrived button */}
                {activeTrip.status === 'ASSIGNED' && (
                  <div className="trip-action-group">
                    <p className="action-instruction">Navigate to the pickup location</p>
                    <button
                      className="btn-trip-action primary"
                      onClick={handleMarkArrived}
                      disabled={tripActionLoading}
                    >
                      {tripActionLoading ? 'Processing...' : 'Mark Arrived'}
                    </button>
                  </div>
                )}

                {/* ARRIVED State: Show OTP input and verify */}
                {activeTrip.status === 'ARRIVED' && (
                  <div className="trip-action-group" style={{
                    background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
                    borderRadius: '16px',
                    padding: '20px',
                    color: 'white',
                    marginTop: '16px'
                  }}>
                    <h4 style={{ margin: '0 0 8px 0', fontSize: '18px' }}>🔐 Enter Pickup OTP</h4>
                    <p style={{ margin: '0 0 16px 0', fontSize: '14px', opacity: 0.9 }}>
                      Ask the rider to share their OTP code
                    </p>
                    <div style={{
                      display: 'flex',
                      gap: '10px',
                      marginBottom: otpVerified ? '16px' : '0'
                    }}>
                      <input
                        type="text"
                        value={otpInput}
                        onChange={(e) => setOtpInput(e.target.value.replace(/\D/g, '').slice(0, 6))}
                        placeholder="Enter 6-digit OTP"
                        maxLength={6}
                        style={{
                          flex: 1,
                          padding: '14px 16px',
                          fontSize: '20px',
                          fontWeight: '600',
                          letterSpacing: '4px',
                          textAlign: 'center',
                          border: 'none',
                          borderRadius: '10px',
                          fontFamily: 'monospace',
                          background: 'white',
                          color: '#1f2937'
                        }}
                        disabled={otpVerified || tripActionLoading}
                      />
                      {!otpVerified && (
                        <button
                          onClick={handleVerifyOTP}
                          disabled={otpInput.length !== 6 || tripActionLoading}
                          style={{
                            padding: '14px 24px',
                            background: otpInput.length === 6 ? '#22c55e' : '#9ca3af',
                            color: 'white',
                            border: 'none',
                            borderRadius: '10px',
                            fontSize: '16px',
                            fontWeight: '600',
                            cursor: otpInput.length === 6 ? 'pointer' : 'default'
                          }}
                        >
                          {tripActionLoading ? '...' : 'Verify'}
                        </button>
                      )}
                    </div>
                    {otpVerified && (
                      <>
                        <div style={{
                          background: 'rgba(255,255,255,0.2)',
                          borderRadius: '8px',
                          padding: '10px',
                          marginBottom: '16px',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          gap: '8px'
                        }}>
                          <span style={{ fontSize: '20px' }}>✅</span>
                          <span style={{ fontWeight: '600' }}>OTP Verified Successfully!</span>
                        </div>
                        <button
                          onClick={handleConfirmPickup}
                          disabled={tripActionLoading}
                          style={{
                            width: '100%',
                            padding: '16px',
                            background: 'white',
                            color: '#d97706',
                            border: 'none',
                            borderRadius: '12px',
                            fontSize: '16px',
                            fontWeight: '700',
                            cursor: 'pointer'
                          }}
                        >
                          {tripActionLoading ? 'Processing...' : '🚀 Start Trip'}
                        </button>
                      </>
                    )}
                  </div>
                )}

                {/* PICKED_UP / IN_PROGRESS State: Show Complete Trip button */}
                {(activeTrip.status === 'PICKED_UP' || activeTrip.status === 'IN_PROGRESS') && (
                  <div className="trip-action-group" style={{
                    background: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
                    borderRadius: '16px',
                    padding: '20px',
                    color: 'white',
                    marginTop: '16px'
                  }}>
                    <h4 style={{ margin: '0 0 8px 0', fontSize: '18px' }}>🚗 Trip In Progress</h4>
                    <p style={{ margin: '0 0 16px 0', fontSize: '14px', opacity: 0.9 }}>
                      Navigate to the drop-off location
                    </p>
                    
                    {/* Drop Location Info */}
                    <div style={{
                      background: 'rgba(255,255,255,0.2)',
                      borderRadius: '10px',
                      padding: '12px',
                      marginBottom: '16px'
                    }}>
                      <div style={{ fontSize: '12px', opacity: 0.8, marginBottom: '4px' }}>📍 DROP-OFF LOCATION</div>
                      <div style={{ fontSize: '14px', fontWeight: '600' }}>
                        {activeTrip.drop_lat && activeTrip.drop_lng 
                          ? `${parseFloat(activeTrip.drop_lat).toFixed(4)}, ${parseFloat(activeTrip.drop_lng).toFixed(4)}`
                          : 'Location not available'}
                      </div>
                    </div>
                    
                    <button
                      onClick={handleCompleteTrip}
                      disabled={tripActionLoading}
                      style={{
                        width: '100%',
                        padding: '16px',
                        background: 'white',
                        color: '#16a34a',
                        border: 'none',
                        borderRadius: '12px',
                        fontSize: '18px',
                        fontWeight: '700',
                        cursor: 'pointer'
                      }}
                    >
                      {tripActionLoading ? 'Processing...' : '✅ Complete Trip'}
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* ========== NEW: Incoming Dispatches Section ========== */}
        {isDriverOnline() && !isDriverBusy() && !activeTrip && (
          <div className="dispatches-section">
            <div className="dispatches-header">
              <h2>📲 Incoming Ride Requests</h2>
              {dispatchPollingActive && (
                <span className="polling-indicator">
                  <span className="pulse-dot"></span> Listening
                </span>
              )}
            </div>

            {pendingDispatches.length === 0 ? (
              <div className="no-dispatches">
                <span className="no-dispatches-icon">🔍</span>
                <p>Waiting for ride requests...</p>
                <p className="hint">Stay online and nearby to receive dispatch offers</p>
              </div>
            ) : (
              <div className="dispatch-list">
                {pendingDispatches.map((dispatch) => (
                  <div key={dispatch.attempt_id} className="dispatch-card">
                    <div className="dispatch-info">
                      <div className="dispatch-row">
                        <span className="dispatch-label">Trip ID:</span>
                        <span className="dispatch-value">#{dispatch.trip_id}</span>
                      </div>
                      <div className="dispatch-row">
                        <span className="dispatch-label">Rider:</span>
                        <span className="dispatch-value">{dispatch.rider_name || 'Rider'}</span>
                      </div>
                      <div className="dispatch-row">
                        <span className="dispatch-label">Pickup:</span>
                        <span className="dispatch-value coordinates">
                          {parseFloat(dispatch.pickup_lat)?.toFixed(4)}, {parseFloat(dispatch.pickup_lng)?.toFixed(4)}
                        </span>
                      </div>
                      {dispatch.estimated_distance_km && (
                        <div className="dispatch-row">
                          <span className="dispatch-label">Distance:</span>
                          <span className="dispatch-value">{dispatch.estimated_distance_km} km</span>
                        </div>
                      )}
                      <div className="dispatch-row">
                        <span className="dispatch-label">Expires:</span>
                        <span className="dispatch-value expire-warning">
                          {dispatch.expires_in_seconds}s
                        </span>
                      </div>
                    </div>
                    <div className="dispatch-actions">
                      <button
                        className="btn-dispatch accept"
                        onClick={() => handleAcceptDispatch(dispatch.attempt_id)}
                        disabled={tripActionLoading}
                      >
                        {tripActionLoading ? '...' : 'Accept'}
                      </button>
                      <button
                        className="btn-dispatch reject"
                        onClick={() => handleRejectDispatch(dispatch.attempt_id)}
                        disabled={tripActionLoading}
                      >
                        Reject
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

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
                    <div className="context-item">
                      <span className="label">Status:</span>
                      <span className={`badge ${activeFleet.approval_status === 'APPROVED' ? 'status-approved' : 'status-pending'}`}>
                        {activeFleet.approval_status}
                      </span>
                    </div>
                  </>
                ) : (
                  <div className="empty-state-container">
                    <p className="empty-state">⚠️ No active fleet association</p>
                    <p className="empty-hint">You need to be part of a fleet to go online.</p>
                    <a href="/app/driver/fleets" className="btn-link">Join or Create Fleet</a>
                  </div>
                )}
              </div>
            </div>

            {/* Active Vehicle Card */}
            <div className="context-card">
              <div className="context-card-header">
                <h3>Active Vehicle Assignment</h3>
                <span className="context-icon">🚗</span>
              </div>
              <div className="context-card-content">
                {activeVehicle ? (
                  <>
                    <div className="context-item">
                      <span className="label">Registration:</span>
                      <span className="value">{activeVehicle.registration}</span>
                    </div>
                    {activeVehicle.category && (
                      <div className="context-item">
                        <span className="label">Category:</span>
                        <span className="value">{activeVehicle.category}</span>
                      </div>
                    )}
                    <div className="context-item">
                      <span className="label">Approval:</span>
                      <span className={`badge ${activeVehicle.is_approved ? 'status-approved' : 'status-pending'}`}>
                        {activeVehicle.status || (activeVehicle.is_approved ? 'APPROVED' : 'PENDING')}
                      </span>
                    </div>
                    <div className="context-item">
                      <span className="label">Documents:</span>
                      <span className={`badge ${activeVehicle.documents_complete ? 'status-approved' : 'status-pending'}`}>
                        {activeVehicle.documents_complete ? '✓ Complete' : '⚠️ Incomplete'}
                      </span>
                    </div>
                    {!activeVehicle.documents_complete && activeVehicle.missing_documents?.length > 0 && (
                      <div className="context-item warning">
                        <span className="label">Missing:</span>
                        <span className="value warning-text">{activeVehicle.missing_documents.join(', ')}</span>
                      </div>
                    )}
                    {/* Vehicle change button for independent drivers - always show if multiple vehicles */}
                    {isIndependent && approvedVehicles.length > 1 && (
                      <button 
                        className={`btn-change-vehicle ${isDriverOnline() ? 'warning' : ''}`}
                        onClick={() => setShowVehicleSelector(true)}
                        disabled={vehicleSelecting || isDriverBusy()}
                        title={isDriverBusy() ? 'Cannot change vehicle during trip' : (isDriverOnline() ? 'This will end your current shift' : 'Switch to another vehicle')}
                      >
                        {isDriverOnline() ? 'Change Vehicle (Ends Shift)' : 'Change Vehicle'}
                      </button>
                    )}
                  </>
                ) : isIndependent && approvedVehicles.length > 0 ? (
                  <div className="vehicle-select-prompt">
                    <p>Select a vehicle to start your shift</p>
                    <button 
                      className="btn-select-vehicle"
                      onClick={() => setShowVehicleSelector(true)}
                      disabled={vehicleSelecting}
                    >
                      Select Vehicle
                    </button>
                  </div>
                ) : isIndependent && approvedVehicles.length === 0 ? (
                  <div className="no-vehicles-prompt">
                    <p className="empty-state">⚠️ No approved vehicles</p>
                    <p className="empty-hint">Add and get a vehicle approved to go online.</p>
                    <a href="/app/driver/vehicles" className="btn-add-vehicle">
                      Add Vehicle
                    </a>
                  </div>
                ) : (
                  <div className="empty-state-container">
                    <p className="empty-state">⚠️ No active vehicle assignment</p>
                    <p className="empty-hint">
                      {isIndependent 
                        ? 'Select a vehicle from your approved list to go online.'
                        : 'Contact your fleet manager to assign a vehicle.'}
                    </p>
                    {isIndependent && (
                      <a href="/app/driver/vehicles" className="btn-link">Manage Vehicles</a>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Vehicle Selector Modal for Independent Drivers */}
            {showVehicleSelector && isIndependent && (
              <div className="vehicle-selector-modal">
                <div className="vehicle-selector-content">
                  <div className="vehicle-selector-header">
                    <h3>Select Vehicle</h3>
                    <button 
                      className="close-btn"
                      onClick={() => setShowVehicleSelector(false)}
                    >
                      ×
                    </button>
                  </div>
                  <div className="vehicle-selector-list">
                    {approvedVehicles.map(vehicle => (
                      <div 
                        key={vehicle.vehicle_id}
                        className={`vehicle-option ${vehicle.is_currently_assigned ? 'current' : ''}`}
                        onClick={() => !vehicleSelecting && handleSelectVehicle(vehicle.vehicle_id)}
                      >
                        <div className="vehicle-option-info">
                          <span className="vehicle-reg">{vehicle.registration_no}</span>
                          <span className="vehicle-cat">{vehicle.category}</span>
                        </div>
                        {vehicle.is_currently_assigned && (
                          <span className="current-badge">Current</span>
                        )}
                      </div>
                    ))}
                  </div>
                  {vehicleSelecting && (
                    <div className="vehicle-selector-loading">
                      <span>Selecting vehicle...</span>
                    </div>
                  )}
                </div>
              </div>
            )}

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
