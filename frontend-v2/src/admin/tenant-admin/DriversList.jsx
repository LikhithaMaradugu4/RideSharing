import { useState, useEffect } from 'react';
import adminService from '../../services/admin.service';
import './DriversList.css';

const DriversList = () => {
  const [drivers, setDrivers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [expandedDriver, setExpandedDriver] = useState(null);
  const [statusUpdating, setStatusUpdating] = useState(null);

  useEffect(() => {
    loadApprovedDrivers();
  }, []);

  const loadApprovedDrivers = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await adminService.getAllDrivers();
      // Filter strictly for APPROVED drivers
      const approved = data.filter((d) => d.approval_status === 'APPROVED');
      setDrivers(approved);
    } catch (err) {
      console.error('Failed to load drivers:', err);
      setError(err.message || 'Failed to load drivers');
    } finally {
      setLoading(false);
    }
  };

  const handleExpand = (driver) => {
    if (expandedDriver?.driver_id === driver.driver_id) {
      setExpandedDriver(null);
    } else {
      setExpandedDriver(driver);
    }
  };

  const handleStatusChange = async (driverId, newStatus) => {
    if (!window.confirm(`Are you sure you want to change this driver's status to ${newStatus}?`)) {
      return;
    }
    try {
      setStatusUpdating(driverId);
      await adminService.updateDriverStatus(driverId, newStatus);
      await loadApprovedDrivers();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update status');
    } finally {
      setStatusUpdating(null);
    }
  };

  if (loading) {
    return (
      <div className="loading-state">
        <div className="spinner"></div>
        <p>Loading approved drivers...</p>
      </div>
    );
  }

  return (
    <div className="drivers-list-view">
      <div className="page-header">
        <h1>Approved Drivers</h1>
        <div className="count-badge">{drivers.length} Active</div>
      </div>

      {error && (
        <div className="error-banner">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
          {error}
        </div>
      )}

      {drivers.length === 0 ? (
        <div className="empty-state">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1"><circle cx="12" cy="12" r="10"></circle><path d="M16 16s-1.5-2-4-2-4 2-4 2"></path><line x1="9" y1="9" x2="9.01" y2="9"></line><line x1="15" y1="9" x2="15.01" y2="9"></line></svg>
          <p>No approved drivers found.</p>
        </div>
      ) : (
        <div className="drivers-list">
          {drivers.map((driver) => {
             const isExpanded = expandedDriver?.driver_id === driver.driver_id;
             
             return (
              <div
                key={driver.driver_id}
                className={`driver-card ${isExpanded ? 'expanded' : ''}`}
              >
                <div className="driver-header" onClick={() => handleExpand(driver)}>
                  {/* Avatar Section */}
                  <div className="driver-avatar">
                    {driver.full_name.charAt(0).toUpperCase()}
                  </div>

                  <div className="driver-info">
                    <div className="driver-name-row">
                      <h3>{driver.full_name}</h3>
                      <span className="status-badge">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"><polyline points="20 6 9 17 4 12"></polyline></svg>
                        Verified
                      </span>
                    </div>
                    
                    <div className="driver-contact">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
                      {driver.phone}
                    </div>
                  </div>

                  <div className={`toggle-icon ${isExpanded ? 'rotated' : ''}`}>
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
                  </div>
                </div>

                {isExpanded && (
                  <div className="driver-details">
                    <div className="detail-section">
                      <h4>
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="1" y="3" width="15" height="13"></rect><polygon points="16 8 20 8 23 11 23 16 16 16 16 8"></polygon><circle cx="5.5" cy="18.5" r="2.5"></circle><circle cx="18.5" cy="18.5" r="2.5"></circle></svg>
                        Allowed Vehicle Categories
                      </h4>
                      
                      <div className="tags-container">
                        {driver.allowed_vehicle_categories && driver.allowed_vehicle_categories.length > 0 ? (
                          driver.allowed_vehicle_categories.map((category, index) => (
                            <span key={index} className="vehicle-tag">
                              {category}
                            </span>
                          ))
                        ) : (
                          <span className="no-tags">No vehicles assigned</span>
                        )}
                      </div>
                    </div>

                    <div className="detail-row">
                        <span className="label">Driver ID:</span>
                        <span className="value code-font">{driver.driver_id}</span>
                    </div>

                    <div className="status-actions">
                      <label>Change Approval Status:</label>
                      <div className="action-buttons">
                        <button
                          onClick={() => handleStatusChange(driver.driver_id, 'PENDING')}
                          disabled={statusUpdating === driver.driver_id}
                          className="btn-status btn-pending"
                        >
                          {statusUpdating === driver.driver_id ? 'Updating...' : 'Set Pending'}
                        </button>
                        <button
                          onClick={() => handleStatusChange(driver.driver_id, 'REJECTED')}
                          disabled={statusUpdating === driver.driver_id}
                          className="btn-status btn-reject"
                        >
                          {statusUpdating === driver.driver_id ? 'Updating...' : 'Reject'}
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

export default DriversList;