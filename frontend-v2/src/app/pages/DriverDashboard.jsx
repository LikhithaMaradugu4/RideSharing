import { useState, useEffect } from 'react';
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
      } catch (err) {
        console.error('Failed to fetch shift readiness:', err);
        setShiftReadiness(null);
      }
    } catch (err) {
      setError(err.message || 'Failed to load dashboard');
      console.error('Error:', err);
    } finally {
      setLoading(false);
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
                    <p className="empty-state">No approved vehicles</p>
                    <a href="/app/driver/vehicles" className="btn-add-vehicle">
                      Add Vehicle
                    </a>
                  </div>
                ) : (
                  <p className="empty-state">No active vehicle</p>
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
