import { useState, useEffect } from 'react';
import adminService from '../../services/admin.service';
import './VehiclesList.css';

const VehiclesList = () => {
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [expandedVehicle, setExpandedVehicle] = useState(null);
  const [statusUpdating, setStatusUpdating] = useState(null);

  useEffect(() => {
    loadApprovedVehicles();
  }, []);

  const loadApprovedVehicles = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await adminService.getApprovedVehicles();
      setVehicles(data);
    } catch (err) {
      console.error('Failed to load vehicles:', err);
      setError(err.message || 'Failed to load vehicles');
    } finally {
      setLoading(false);
    }
  };

  const handleExpand = (vehicle) => {
    if (expandedVehicle?.vehicle_id === vehicle.vehicle_id) {
      setExpandedVehicle(null);
    } else {
      setExpandedVehicle(vehicle);
    }
  };

  const handleStatusChange = async (vehicleId, newStatus) => {
    if (!window.confirm(`Are you sure you want to change status to ${newStatus}?`)) {
      return;
    }

    try {
      setStatusUpdating(vehicleId);
      await adminService.updateVehicleStatus(vehicleId, newStatus);
      await loadApprovedVehicles();
    } catch (err) {
      alert(err.message || 'Failed to update status');
    } finally {
      setStatusUpdating(null);
    }
  };

  if (loading) {
    return (
      <div className="loading-state">
        <p>Loading approved vehicles...</p>
      </div>
    );
  }

  return (
    <div className="vehicles-list-view">
      <div className="page-header">
        <h1>Approved Vehicles</h1>
        <div className="count-badge">{vehicles.length} Active</div>
      </div>

      {error && (
        <div className="error-banner">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
          {error}
        </div>
      )}

      {vehicles.length === 0 ? (
        <div className="empty-state">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1">
            <rect x="1" y="3" width="15" height="13"></rect>
            <polygon points="16 8 20 8 23 11 23 16 16 16 16 8"></polygon>
            <circle cx="5.5" cy="18.5" r="2.5"></circle>
            <circle cx="18.5" cy="18.5" r="2.5"></circle>
          </svg>
          <p>No approved vehicles found.</p>
        </div>
      ) : (
        <div className="vehicles-list">
          {vehicles.map((vehicle) => {
            const isExpanded = expandedVehicle?.vehicle_id === vehicle.vehicle_id;

            return (
              <div
                key={vehicle.vehicle_id}
                className={`vehicle-card ${isExpanded ? 'expanded' : ''}`}
              >
                <div className="vehicle-header" onClick={() => handleExpand(vehicle)}>
                  <div className="vehicle-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <rect x="1" y="3" width="15" height="13"></rect>
                      <polygon points="16 8 20 8 23 11 23 16 16 16 16 8"></polygon>
                      <circle cx="5.5" cy="18.5" r="2.5"></circle>
                      <circle cx="18.5" cy="18.5" r="2.5"></circle>
                    </svg>
                  </div>

                  <div className="vehicle-info">
                    <div className="vehicle-name-row">
                      <h3>{vehicle.registration_no}</h3>
                      <span className="status-badge approved">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                          <polyline points="20 6 9 17 4 12"></polyline>
                        </svg>
                        Approved
                      </span>
                    </div>

                    <div className="vehicle-meta">
                      <span className="category-badge">{vehicle.category}</span>
                      {vehicle.fleet_id && (
                        <span className="fleet-id">Fleet #{vehicle.fleet_id}</span>
                      )}
                    </div>
                  </div>

                  <div className={`toggle-icon ${isExpanded ? 'rotated' : ''}`}>
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <polyline points="6 9 12 15 18 9"></polyline>
                    </svg>
                  </div>
                </div>

                {isExpanded && (
                  <div className="vehicle-details">
                    <div className="detail-row">
                      <span className="label">Vehicle ID:</span>
                      <span className="value code-font">{vehicle.vehicle_id}</span>
                    </div>

                    <div className="detail-row">
                      <span className="label">Category:</span>
                      <span className="value">{vehicle.category}</span>
                    </div>

                    <div className="detail-row">
                      <span className="label">Status:</span>
                      <span className={`value status-${vehicle.status?.toLowerCase()}`}>
                        {vehicle.status}
                      </span>
                    </div>

                    <div className="detail-row">
                      <span className="label">Created:</span>
                      <span className="value">
                        {new Date(vehicle.created_on).toLocaleDateString()}
                      </span>
                    </div>

                    <div className="status-actions">
                      <label>Change Status:</label>
                      <div className="action-buttons">
                        <button
                          className="btn-status btn-pending"
                          onClick={() => handleStatusChange(vehicle.vehicle_id, 'PENDING')}
                          disabled={statusUpdating === vehicle.vehicle_id || vehicle.approval_status === 'PENDING'}
                        >
                          Set Pending
                        </button>
                        <button
                          className="btn-status btn-reject"
                          onClick={() => handleStatusChange(vehicle.vehicle_id, 'REJECTED')}
                          disabled={statusUpdating === vehicle.vehicle_id || vehicle.approval_status === 'REJECTED'}
                        >
                          Reject
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default VehiclesList;
