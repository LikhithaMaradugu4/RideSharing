import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import fleetService from '../../services/fleet.service';
import Icons from '../../components/Icons';
import './FleetAssignments.css';

function FleetAssignments() {
  const navigate = useNavigate();
  
  // State
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Data
  const [assignments, setAssignments] = useState([]);
  const [drivers, setDrivers] = useState([]);
  const [vehicles, setVehicles] = useState([]);
  
  // Create assignment state
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedDriver, setSelectedDriver] = useState('');
  const [selectedVehicle, setSelectedVehicle] = useState('');
  const [creating, setCreating] = useState(false);

  // Load data
  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      setError('');
      
      const [assignmentsRes, driversRes, vehiclesRes] = await Promise.all([
        fleetService.listActiveAssignments(),
        fleetService.listDrivers(),
        fleetService.listVehicles()
      ]);
      
      setAssignments(assignmentsRes.assignments || []);
      setDrivers(driversRes.drivers || []);
      setVehicles(vehiclesRes.vehicles || []);
    } catch (err) {
      console.error('Load data error:', err);
      if (err.status === 404 || err.status === 403) {
        navigate('/rider-dashboard');
        return;
      }
      setError(err.message || 'Failed to load assignments');
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Get driver name by ID
  const getDriverName = (driverId) => {
    const driver = drivers.find(d => d.driver_id === driverId);
    return driver ? driver.full_name : `Driver #${driverId}`;
  };

  // Get vehicle info by ID
  const getVehicleInfo = (vehicleId) => {
    const vehicle = vehicles.find(v => v.vehicle_id === vehicleId);
    return vehicle ? vehicle.registration_no : `Vehicle #${vehicleId}`;
  };

  // Filter available drivers and vehicles (not currently assigned)
  const getAvailableDrivers = () => {
    const assignedDriverIds = new Set(assignments.map(a => a.driver_id));
    return drivers.filter(d => !assignedDriverIds.has(d.driver_id));
  };

  const getAvailableVehicles = () => {
    const assignedVehicleIds = new Set(assignments.map(a => a.vehicle_id));
    // Also filter by approval status
    return vehicles.filter(v => 
      !assignedVehicleIds.has(v.vehicle_id) && 
      v.approval_status === 'APPROVED'
    );
  };

  // Create assignment
  const handleCreateAssignment = async (e) => {
    e.preventDefault();
    
    if (!selectedDriver || !selectedVehicle) {
      setError('Please select both a driver and a vehicle');
      return;
    }
    
    try {
      setCreating(true);
      setError('');
      
      await fleetService.createAssignment(
        parseInt(selectedDriver),
        parseInt(selectedVehicle)
      );
      
      setSuccess('Assignment created successfully');
      setShowCreateModal(false);
      setSelectedDriver('');
      setSelectedVehicle('');
      
      await loadData();
      
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      console.error('Create assignment error:', err);
      setError(err.message || 'Failed to create assignment');
    } finally {
      setCreating(false);
    }
  };

  // End assignment
  const handleEndAssignment = async (assignmentId) => {
    if (!window.confirm('Are you sure you want to end this assignment?')) {
      return;
    }
    
    try {
      setError('');
      await fleetService.endAssignment(assignmentId);
      setSuccess('Assignment ended successfully');
      await loadData();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      console.error('End assignment error:', err);
      setError(err.message || 'Failed to end assignment');
    }
  };

  if (loading) {
    return (
      <div className="fleet-assignments">
        <div className="loading-state">
          <p>Loading assignments...</p>
        </div>
      </div>
    );
  }

  const availableDrivers = getAvailableDrivers();
  const availableVehicles = getAvailableVehicles();

  return (
    <div className="fleet-assignments">
      <div className="page-header">
        <button className="btn-back" onClick={() => navigate('/fleet-dashboard')}>
          ← Back
        </button>
        <h1>Driver-Vehicle Assignments</h1>
        <button 
          className="btn-add"
          onClick={() => setShowCreateModal(true)}
          disabled={availableDrivers.length === 0 || availableVehicles.length === 0}
        >
          + Assign
        </button>
      </div>

      {error && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      {/* Quick Stats */}
      <div className="stats-row">
        <div className="stat-card">
          <span className="stat-value">{assignments.length}</span>
          <span className="stat-label">Active Assignments</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">{availableDrivers.length}</span>
          <span className="stat-label">Available Drivers</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">{availableVehicles.length}</span>
          <span className="stat-label">Available Vehicles</span>
        </div>
      </div>

      {/* Active Assignments */}
      <div className="section">
        <h2>Active Assignments</h2>
        {assignments.length === 0 ? (
          <div className="empty-state">
            <span className="empty-icon"><Icons.Link size={48} /></span>
            <p>No active driver-vehicle assignments</p>
            <p className="hint">Assign drivers to vehicles so they can take trips</p>
            {(availableDrivers.length > 0 && availableVehicles.length > 0) && (
              <button 
                className="btn-primary"
                onClick={() => setShowCreateModal(true)}
              >
                Create Assignment
              </button>
            )}
          </div>
        ) : (
          <div className="assignments-list">
            {assignments.map((assignment) => (
              <div key={assignment.assignment_id} className="assignment-card">
                <div className="assignment-info">
                  <div className="assignment-pair">
                    <span className="driver-name">{getDriverName(assignment.driver_id)}</span>
                    <span className="arrow">→</span>
                    <span className="vehicle-reg">{getVehicleInfo(assignment.vehicle_id)}</span>
                  </div>
                  <p className="assignment-date">
                    Since: {assignment.start_time ? new Date(assignment.start_time).toLocaleString() : 'N/A'}
                  </p>
                </div>
                <button 
                  className="btn-end"
                  onClick={() => handleEndAssignment(assignment.assignment_id)}
                >
                  End
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Create Assignment Modal */}
      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Create Assignment</h2>
              <button className="btn-close" onClick={() => setShowCreateModal(false)}>×</button>
            </div>
            <form className="assignment-form" onSubmit={handleCreateAssignment}>
              <div className="form-group">
                <label>Select Driver</label>
                <select
                  value={selectedDriver}
                  onChange={(e) => setSelectedDriver(e.target.value)}
                  required
                >
                  <option value="">-- Choose a driver --</option>
                  {availableDrivers.map((driver) => (
                    <option key={driver.driver_id} value={driver.driver_id}>
                      {driver.full_name} ({driver.phone})
                    </option>
                  ))}
                </select>
              </div>
              
              <div className="form-group">
                <label>Select Vehicle</label>
                <select
                  value={selectedVehicle}
                  onChange={(e) => setSelectedVehicle(e.target.value)}
                  required
                >
                  <option value="">-- Choose a vehicle --</option>
                  {availableVehicles.map((vehicle) => (
                    <option key={vehicle.vehicle_id} value={vehicle.vehicle_id}>
                      {vehicle.registration_no} ({vehicle.category})
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-actions">
                <button 
                  type="button" 
                  className="btn-cancel"
                  onClick={() => setShowCreateModal(false)}
                  disabled={creating}
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  className="btn-submit"
                  disabled={creating || !selectedDriver || !selectedVehicle}
                >
                  {creating ? 'Creating...' : 'Create Assignment'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default FleetAssignments;
