import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import driverService from '../../services/driver.service';
import DriverLayout from '../layout/DriverLayout';
import './DriverDispatches.css';

function DriverDispatches() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [driverProfile, setDriverProfile] = useState(null);
  const [dispatches, setDispatches] = useState([]);
  const [shiftStatus, setShiftStatus] = useState(null);
  const [shiftReadiness, setShiftReadiness] = useState(null);
  const [processingId, setProcessingId] = useState(null);

  const token = localStorage.getItem('jwt_token');

  useEffect(() => {
    if (!token) {
      navigate('/login');
      return;
    }
    fetchData();
  }, [token, navigate]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch driver profile
      const profile = await driverService.getMyProfile(token);
      if (!profile || profile.approval_status !== 'APPROVED') {
        navigate('/app/home');
        return;
      }
      setDriverProfile(profile);

      // Fetch active shift
      try {
        const shift = await driverService.getActiveShift(token);
        setShiftStatus(shift);
      } catch {
        setShiftStatus(null);
      }

      // Fetch shift readiness to validate vehicle assignment
      try {
        const readiness = await driverService.checkShiftReadiness(token);
        setShiftReadiness(readiness);
      } catch {
        setShiftReadiness(null);
      }

      // Fetch pending dispatches
      try {
        const result = await driverService.getPendingDispatches(token);
        setDispatches(result.pending_dispatches || result || []);
      } catch (err) {
        setDispatches([]);
      }
    } catch (err) {
      setError(err.message || 'Failed to load page');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAcceptDispatch = async (dispatchId) => {
    try {
      setProcessingId(dispatchId);
      setError(null);
      await driverService.acceptDispatch(token, dispatchId);
      // Refetch dispatches
      await fetchData();
    } catch (err) {
      setError(err.message || 'Failed to accept dispatch');
    } finally {
      setProcessingId(null);
    }
  };

  const handleRejectDispatch = async (dispatchId) => {
    try {
      setProcessingId(dispatchId);
      setError(null);
      await driverService.rejectDispatch(token, dispatchId);
      // Refetch dispatches
      await fetchData();
    } catch (err) {
      setError(err.message || 'Failed to reject dispatch');
    } finally {
      setProcessingId(null);
    }
  };

  if (loading) {
    return (
      <DriverLayout driverProfile={driverProfile}>
        <div className="dispatches-container">
          <div className="loading-state">Loading dispatches...</div>
        </div>
      </DriverLayout>
    );
  }

  if (!driverProfile) {
    return null;
  }

  const isOffline = !shiftStatus;
  const hasVehicleAssignment = shiftReadiness?.checks?.vehicle_assignment?.exists;
  const isVehicleApproved = shiftReadiness?.checks?.vehicle_assignment?.is_vehicle_approved;
  const canAcceptDispatch = !isOffline && hasVehicleAssignment && isVehicleApproved;

  // Determine reason for not being able to accept
  const getBlockedReason = () => {
    if (isOffline) return 'You are offline. Go online in the Dashboard to accept dispatches.';
    if (!hasVehicleAssignment) return 'No vehicle assigned. Please assign a vehicle from the Dashboard.';
    if (!isVehicleApproved) return 'Your vehicle is not approved. Please wait for approval.';
    return null;
  };

  return (
    <DriverLayout driverProfile={driverProfile}>
      <div className="dispatches-container">
        <div className="page-header">
          <h1>Pending Dispatches</h1>
          <p className="page-subtitle">Review and respond to available trip requests</p>
        </div>

        {error && (
          <div className="error-banner">
            <span>⚠️</span>
            <span>{error}</span>
            <button className="error-close" onClick={() => setError(null)}>×</button>
          </div>
        )}

        {getBlockedReason() && (
          <div className="offline-warning">
            <span className="warning-icon">⏸</span>
            <span>{getBlockedReason()}</span>
          </div>
        )}

        {dispatches.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📭</div>
            <h2>No pending dispatches</h2>
            <p>Check back soon for available trips</p>
          </div>
        ) : (
          <div className="dispatches-list">
            {dispatches.map((dispatch) => (
              <div key={dispatch.dispatch_id} className="dispatch-card">
                <div className="dispatch-header">
                  <span className="dispatch-id">#{dispatch.dispatch_id}</span>
                  {dispatch.category && (
                    <span className="category-badge">{dispatch.category}</span>
                  )}
                </div>

                <div className="dispatch-details">
                  <div className="detail-item">
                    <span className="detail-label">Pickup</span>
                    <span className="detail-value">
                      {dispatch.pickup_area || 'Area not specified'}
                    </span>
                  </div>

                  <div className="detail-item">
                    <span className="detail-label">Drop-off</span>
                    <span className="detail-value">
                      {dispatch.drop_area || 'Area not specified'}
                    </span>
                  </div>

                  {dispatch.vehicle_category && (
                    <div className="detail-item">
                      <span className="detail-label">Vehicle Category</span>
                      <span className="detail-value">{dispatch.vehicle_category}</span>
                    </div>
                  )}
                </div>

                <div className="dispatch-actions">
                  <button
                    className="btn btn-accept"
                    onClick={() => handleAcceptDispatch(dispatch.dispatch_id)}
                    disabled={!canAcceptDispatch || processingId === dispatch.dispatch_id}
                    title={!canAcceptDispatch ? getBlockedReason() : 'Accept this dispatch'}
                  >
                    {processingId === dispatch.dispatch_id ? 'Processing...' : 'Accept'}
                  </button>

                  <button
                    className="btn btn-reject"
                    onClick={() => handleRejectDispatch(dispatch.dispatch_id)}
                    disabled={processingId === dispatch.dispatch_id}
                  >
                    {processingId === dispatch.dispatch_id ? 'Processing...' : 'Reject'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </DriverLayout>
  );
}

export default DriverDispatches;
