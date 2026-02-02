import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import fleetService from '../../services/fleet.service';
import tokenStorage from '../../services/tokenStorage';
import VehicleAddForm from '../components/VehicleAddForm';
import './FleetVehicles.css';

function FleetVehicles() {
  const navigate = useNavigate();
  const token = tokenStorage.get('jwt_token');
  
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  
  // Add vehicle form
  const [showAddForm, setShowAddForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!token) {
      navigate('/login');
      return;
    }
    fetchVehicles();
  }, [token, navigate]);

  const fetchVehicles = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fleetService.listVehicles();
      setVehicles(data.vehicles || []);
    } catch (err) {
      if (err.status === 403) {
        navigate('fleet-dashboard');
        return;
      }
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleVehicleSubmit = async (vehicleData, specData, files) => {
    try {
      setSubmitting(true);
      setError(null);
      setSuccess(null);

      await fleetService.addVehicle(vehicleData);

      setSuccess('Vehicle added successfully!');
      setShowAddForm(false);
      fetchVehicles();
    } catch (err) {
      setError(err.message);
      throw err; // Re-throw to let the form know submission failed
    } finally {
      setSubmitting(false);
    }
  };

  const handleCancel = () => {
    setShowAddForm(false);
    setError(null);
  };

  const getStatusBadge = (status) => {
    const statusColors = {
      'ACTIVE': 'badge-success',
      'INACTIVE': 'badge-warning',
      'APPROVED': 'badge-success',
      'PENDING': 'badge-warning',
      'REJECTED': 'badge-danger'
    };
    return statusColors[status] || 'badge-default';
  };

  if (loading) {
    return (
      <div className="fleet-vehicles">
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <span>Loading vehicles...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="fleet-vehicles">
      <header className="page-header">
        <button className="btn-back" onClick={() => navigate('/fleet-dashboard')}>
          ← Back
        </button>
        <h1>🚗 Fleet Vehicles</h1>
        <button className="btn-add" onClick={() => setShowAddForm(true)}>
          + Add Vehicle
        </button>
      </header>

      {error && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      {/* Add Vehicle Form - Reusing shared component */}
      {showAddForm && (
        <VehicleAddForm
          onSubmit={handleVehicleSubmit}
          onCancel={handleCancel}
          isSubmitting={submitting}
          mode="fleet"
          includeSpec={false}
        />
      )}

      {/* Vehicles List */}
      <div className="vehicles-list">
        {vehicles.length === 0 ? (
          <div className="empty-state">
            <span className="empty-icon">🚗</span>
            <p>No vehicles in your fleet yet</p>
            <button className="btn-primary" onClick={() => setShowAddForm(true)}>
              Add Your First Vehicle
            </button>
          </div>
        ) : (
          vehicles.map(vehicle => (
            <div key={vehicle.vehicle_id} className="vehicle-card">
              <div className="vehicle-info">
                <span className="vehicle-reg">{vehicle.registration_no}</span>
                <span className="vehicle-category">{vehicle.category}</span>
              </div>
              <div className="vehicle-status">
                <span className={`badge ${getStatusBadge(vehicle.status)}`}>
                  {vehicle.status}
                </span>
                <span className={`badge ${getStatusBadge(vehicle.approval_status)}`}>
                  {vehicle.approval_status}
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default FleetVehicles;
