import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import DriverLayout from '../layout/DriverLayout';
import VehicleAddForm from '../components/VehicleAddForm';
import driverService from '../../services/driver.service';
import userService from '../../services/user.service';
import './DriverVehicles.css';

export default function DriverVehicles() {
  const navigate = useNavigate();
  const token = localStorage.getItem('jwt_token');

  const [driverProfile, setDriverProfile] = useState(null);
  const [profileLoading, setProfileLoading] = useState(true);
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [submitLoading, setSubmitLoading] = useState(false);
  
  // Driver status - independent or part of a business fleet
  const [isIndependent, setIsIndependent] = useState(true);
  const [businessFleet, setBusinessFleet] = useState(null);
  const [capabilitiesLoading, setCapabilitiesLoading] = useState(true);

  const fetchCapabilities = useCallback(async () => {
    if (!token) return;
    
    try {
      setCapabilitiesLoading(true);
      const data = await userService.getCapabilities(token);
      const driverInfo = data?.driver || {};
      setIsIndependent(driverInfo.is_independent ?? true);
      setBusinessFleet(driverInfo.business_fleet || null);
    } catch (err) {
      console.error('Failed to fetch capabilities:', err);
      // Default to independent if we can't fetch
      setIsIndependent(true);
      setBusinessFleet(null);
    } finally {
      setCapabilitiesLoading(false);
    }
  }, [token]);

  const fetchVehicles = useCallback(async () => {
    if (!token) {
      return;
    }

    try {
      setLoading(true);
      setError('');
      const data = await driverService.getMyVehicles(token);
      setVehicles(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err.message || 'Failed to load vehicles');
      setVehicles([]);
    } finally {
      setLoading(false);
    }
  }, [token]);

  const fetchDriverProfile = useCallback(async () => {
    try {
      setProfileLoading(true);
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
    } catch (err) {
      console.error('Failed to fetch driver profile:', err);
      navigate('/app/home');
    } finally {
      setProfileLoading(false);
    }
  }, [token, navigate]);

  useEffect(() => {
    if (!token) {
      navigate('/login');
      return;
    }

    fetchDriverProfile();
    fetchCapabilities();
    fetchVehicles();
  }, [token, navigate, fetchDriverProfile, fetchCapabilities, fetchVehicles]);

  const handleVehicleSubmit = async (vehicleData, specData, files) => {
    try {
      setSubmitLoading(true);
      setError('');
      setSuccess('');

      const created = await driverService.createVehicle(token, vehicleData);

      // Add vehicle specifications if provided
      if (specData) {
        try {
          await driverService.addVehicleSpec(token, created.vehicle_id, specData);
        } catch (specError) {
          await fetchVehicles();
          setError(
            specError.message ||
            'Vehicle saved but specification could not be recorded. Please retry from the vehicle list.'
          );
          return;
        }
      }

      await fetchVehicles();
      setShowAddForm(false);
      setSuccess('Vehicle submitted for review successfully.');
    } catch (err) {
      setError(err.message || 'Failed to submit vehicle details.');
      throw err; // Re-throw to let the form know submission failed
    } finally {
      setSubmitLoading(false);
    }
  };

  const handleCancel = () => {
    setShowAddForm(false);
    setError('');
  };

  const getStatusBadgeClass = (approvalStatus) => {
    const statusMap = {
      APPROVED: 'badge-approved',
      PENDING: 'badge-pending',
      REJECTED: 'badge-rejected'
    };
    return statusMap[approvalStatus] || 'badge-pending';
  };

  const getStatusLabel = (approvalStatus) => {
    const labels = {
      APPROVED: 'Approved',
      PENDING: 'Under Review',
      REJECTED: 'Rejected'
    };
    return labels[approvalStatus] || approvalStatus;
  };

  // Show loading while fetching profile or capabilities
  if (profileLoading || capabilitiesLoading) {
    return (
      <DriverLayout driverProfile={driverProfile}>
        <div className="driver-vehicles-container">
          <div className="loading-state">
            <p>Loading...</p>
          </div>
        </div>
      </DriverLayout>
    );
  }

  // Show fleet member message if driver is part of a business fleet
  if (!isIndependent && businessFleet) {
    return (
      <DriverLayout driverProfile={driverProfile}>
        <div className="driver-vehicles-container">
          <div className="vehicles-header">
            <h1>Vehicles</h1>
          </div>
          
          <div className="info-banner fleet-member">
            <div className="info-icon">🚗</div>
            <div className="info-content">
              <h3>You're Part of {businessFleet.fleet_name}</h3>
              <p>
                As a member of a business fleet, you use vehicles assigned by your fleet manager.
                You cannot add your own vehicles while part of this fleet.
              </p>
              <p>
                Your fleet manager will assign you a vehicle when you start your shift.
                Contact your fleet manager if you need a vehicle assignment.
              </p>
              <div className="info-actions">
                <button
                  className="btn-secondary"
                  onClick={() => navigate('/app/driver/dashboard')}
                >
                  Go to Dashboard
                </button>
              </div>
            </div>
          </div>
        </div>
      </DriverLayout>
    );
  }

  return (
    <DriverLayout driverProfile={driverProfile}>
      <div className="driver-vehicles-container">
        <div className="vehicles-header">
          <h1>My Vehicles</h1>
          {!showAddForm && isIndependent && (
            <button
              className="btn-primary btn-add-vehicle"
              onClick={() => {
                setShowAddForm(true);
                setError('');
                setSuccess('');
              }}
            >
              Add Vehicle
            </button>
          )}
        </div>

        {error && (
          <div className="error-banner">
            <strong>Error:</strong> {error}
          </div>
        )}

        {success && (
          <div className="success-banner">
            {success}
          </div>
        )}

        {showAddForm && (
          <VehicleAddForm
            onSubmit={handleVehicleSubmit}
            onCancel={handleCancel}
            isSubmitting={submitLoading}
            mode="driver"
            includeSpec={true}
          />
        )}

        {loading ? (
          <div className="loading-state">
            <p>Loading vehicles...</p>
          </div>
        ) : vehicles.length === 0 ? (
          <div className="empty-state">
            <p>No vehicles added yet.</p>
            <button
              className="btn-primary"
              onClick={() => {
                setShowAddForm(true);
                setError('');
                setSuccess('');
              }}
            >
              Add Your First Vehicle
            </button>
          </div>
        ) : (
          <div className="vehicles-grid">
            {vehicles.map((vehicle) => (
              <div key={vehicle.vehicle_id} className="vehicle-card">
                <div className="vehicle-header">
                  <div className="vehicle-title">
                    <h3>{vehicle.registration_no || 'Unnamed Vehicle'}</h3>
                    <span className={`badge ${getStatusBadgeClass(vehicle.approval_status)}`}>
                      {getStatusLabel(vehicle.approval_status)}
                    </span>
                  </div>
                  <span className="vehicle-category">{vehicle.category || '—'}</span>
                </div>

                <div className="vehicle-details">
                  <div className="detail-item">
                    <span className="detail-label">Vehicle ID</span>
                    <span className="detail-value">{vehicle.vehicle_id}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Category</span>
                    <span className="detail-value">{vehicle.category}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Approval Status</span>
                    <span className="detail-value">{vehicle.approval_status}</span>
                  </div>
                </div>

                <div className="vehicle-actions">
                  <span className="action-info">
                    {vehicle.approval_status === 'PENDING' && 'Awaiting tenant admin review.'}
                    {vehicle.approval_status === 'APPROVED' && 'Approved and ready to use.'}
                    {vehicle.approval_status === 'REJECTED' && 'Contact support for rejection details.'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </DriverLayout>
  );
}
