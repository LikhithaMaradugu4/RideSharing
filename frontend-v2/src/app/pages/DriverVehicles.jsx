import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import DriverLayout from '../layout/DriverLayout';
import driverService from '../../services/driver.service';
import userService from '../../services/user.service';
import './DriverVehicles.css';

const DEFAULT_BASIC_INFO = {
  registration_no: '',
  category: 'AUTO'
};

const DEFAULT_SPEC_INFO = {
  manufacturer: '',
  model_name: '',
  manufacture_year: '',
  fuel_type: 'PETROL',
  seating_capacity: ''
};

const DEFAULT_DOCUMENT_URLS = {
  rcUrl: '',
  insuranceUrl: '',
  permitUrl: '',
  fitnessUrl: ''
};

const DEFAULT_PHOTO_URLS = [''];

const FUEL_OPTIONS = ['PETROL', 'DIESEL', 'CNG', 'EV'];
const CATEGORY_OPTIONS = ['AUTO', 'BIKE', 'SEDAN', 'SUV', 'LUXURY'];
const CURRENT_YEAR = new Date().getFullYear();

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
  const [addStep, setAddStep] = useState(1);
  const [submitLoading, setSubmitLoading] = useState(false);
  
  // Driver status - independent or part of a business fleet
  const [isIndependent, setIsIndependent] = useState(true);
  const [businessFleet, setBusinessFleet] = useState(null);
  const [capabilitiesLoading, setCapabilitiesLoading] = useState(true);

  const [basicInfo, setBasicInfo] = useState({ ...DEFAULT_BASIC_INFO });
  const [specInfo, setSpecInfo] = useState({ ...DEFAULT_SPEC_INFO });
  const [documentUrls, setDocumentUrls] = useState({ ...DEFAULT_DOCUMENT_URLS });
  const [photoUrls, setPhotoUrls] = useState([...DEFAULT_PHOTO_URLS]);

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

  const resetForm = () => {
    setShowAddForm(false);
    setAddStep(1);
    setBasicInfo({ ...DEFAULT_BASIC_INFO });
    setSpecInfo({ ...DEFAULT_SPEC_INFO });
    setDocumentUrls({ ...DEFAULT_DOCUMENT_URLS });
    setPhotoUrls([...DEFAULT_PHOTO_URLS]);
    setSubmitLoading(false);
  };

  const handleBasicInfoChange = (event) => {
    const { name, value } = event.target;
    setBasicInfo((prev) => ({ ...prev, [name]: value }));
  };

  const handleSpecChange = (event) => {
    const { name, value } = event.target;
    setSpecInfo((prev) => ({ ...prev, [name]: value }));
  };

  const handleDocumentUrlChange = (event) => {
    const { name, value } = event.target;
    setDocumentUrls((prev) => ({ ...prev, [name]: value }));
  };

  const handlePhotoUrlChange = (index, value) => {
    setPhotoUrls((prev) => {
      const next = [...prev];
      next[index] = value;
      return next;
    });
  };

  const addPhotoField = () => {
    setPhotoUrls((prev) => [...prev, '']);
  };

  const removePhotoField = (index) => {
    setPhotoUrls((prev) => {
      if (prev.length === 1) {
        return prev;
      }
      return prev.filter((_, idx) => idx !== index);
    });
  };

  const hasValue = (value) => typeof value === 'string' && value.trim().length > 0;

  const validateStep = (step) => {
    if (step === 1) {
      return hasValue(basicInfo.registration_no) && hasValue(basicInfo.category);
    }

    if (step === 2) {
      const manufactureYear = Number(specInfo.manufacture_year);
      const seatingCapacity = Number(specInfo.seating_capacity);
      return (
        hasValue(specInfo.manufacturer) &&
        hasValue(specInfo.model_name) &&
        !Number.isNaN(manufactureYear) &&
        manufactureYear >= 2000 &&
        manufactureYear <= CURRENT_YEAR &&
        !Number.isNaN(seatingCapacity) &&
        seatingCapacity > 0
      );
    }

    if (step === 3) {
      return hasValue(documentUrls.rcUrl) && hasValue(documentUrls.insuranceUrl);
    }

    if (step === 4) {
      return photoUrls.some((url) => hasValue(url));
    }

    return false;
  };

  const buildDocumentPayload = () => {
    const rcUrl = documentUrls.rcUrl.trim();
    const insuranceUrl = documentUrls.insuranceUrl.trim();
    const permitUrl = documentUrls.permitUrl.trim();
    const fitnessUrl = documentUrls.fitnessUrl.trim();

    const photoEntries = photoUrls
      .map((url) => url.trim())
      .filter((url) => url.length > 0)
      .map((url) => ({
        document_type: 'VEHICLE_PHOTO',
        file_url: url
      }));

    const documents = [
      { document_type: 'RC', file_url: rcUrl },
      { document_type: 'INSURANCE', file_url: insuranceUrl }
    ];

    if (permitUrl) {
      documents.push({ document_type: 'PERMIT', file_url: permitUrl });
    }

    if (fitnessUrl) {
      documents.push({ document_type: 'FITNESS', file_url: fitnessUrl });
    }

    return { documents, photoEntries };
  };

  const handleAddVehicle = async () => {
    if (!validateStep(4)) {
      return;
    }

    const registration = basicInfo.registration_no.trim().toUpperCase();
    const { documents, photoEntries } = buildDocumentPayload();

    if (!registration) {
      setError('Registration number is required.');
      setAddStep(1);
      return;
    }

    if (photoEntries.length === 0) {
      setError('At least one vehicle photo URL is required.');
      setAddStep(4);
      return;
    }

    const vehiclePayload = {
      category: basicInfo.category,
      registration_no: registration,
      documents: [...documents, ...photoEntries]
    };

    const specPayload = {
      manufacturer: specInfo.manufacturer.trim(),
      model_name: specInfo.model_name.trim(),
      manufacture_year: Number(specInfo.manufacture_year),
      fuel_type: specInfo.fuel_type,
      seating_capacity: Number(specInfo.seating_capacity)
    };

    try {
      setSubmitLoading(true);
      setError('');
      setSuccess('');

      const created = await driverService.createVehicle(token, vehiclePayload);

      try {
        await driverService.addVehicleSpec(token, created.vehicle_id, specPayload);
      } catch (specError) {
        await fetchVehicles();
        setError(
          specError.message ||
          'Vehicle saved but specification could not be recorded. Please retry from the vehicle list.'
        );
        return;
      }

      await fetchVehicles();
      resetForm();
      setSuccess('Vehicle submitted for review successfully.');
    } catch (err) {
      setError(err.message || 'Failed to submit vehicle details.');
    } finally {
      setSubmitLoading(false);
    }
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

  const currentStepIsValid = validateStep(addStep);

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
          <div className="add-vehicle-card">
            <h2>Add New Vehicle</h2>

            <div className="step-indicator">
              {[1, 2, 3, 4].map((step) => (
                <div
                  key={step}
                  className={`step ${step === addStep ? 'active' : ''} ${step < addStep ? 'completed' : ''}`}
                >
                  <span className="step-number">{step}</span>
                  <span className="step-label">
                    {step === 1 && 'Vehicle'}
                    {step === 2 && 'Specification'}
                    {step === 3 && 'Documents'}
                    {step === 4 && 'Photos'}
                  </span>
                </div>
              ))}
            </div>

            <div className="step-content">
              {addStep === 1 && (
                <div className="form-section">
                  <h3>Vehicle Details</h3>
                  <p className="section-info">Provide the registration number and category for this vehicle.</p>

                  <div className="form-group">
                    <label>Registration Number</label>
                    <input
                      type="text"
                      name="registration_no"
                      value={basicInfo.registration_no}
                      onChange={handleBasicInfoChange}
                      placeholder="e.g., KA01AB1234"
                      maxLength="20"
                    />
                  </div>

                  <div className="form-group">
                    <label>Vehicle Category</label>
                    <select
                      name="category"
                      value={basicInfo.category}
                      onChange={handleBasicInfoChange}
                    >
                      {CATEGORY_OPTIONS.map((option) => (
                        <option key={option} value={option}>
                          {option}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              )}

              {addStep === 2 && (
                <div className="form-section">
                  <h3>Vehicle Specification</h3>
                  <p className="section-info">This information is required for compliance and pricing.</p>

                  <div className="form-row">
                    <div className="form-group">
                      <label>Manufacturer</label>
                      <input
                        type="text"
                        name="manufacturer"
                        value={specInfo.manufacturer}
                        onChange={handleSpecChange}
                        placeholder="e.g., Toyota"
                      />
                    </div>
                    <div className="form-group">
                      <label>Model Name</label>
                      <input
                        type="text"
                        name="model_name"
                        value={specInfo.model_name}
                        onChange={handleSpecChange}
                        placeholder="e.g., Corolla"
                      />
                    </div>
                  </div>

                  <div className="form-row">
                    <div className="form-group">
                      <label>Manufacture Year</label>
                      <input
                        type="number"
                        name="manufacture_year"
                        value={specInfo.manufacture_year}
                        onChange={handleSpecChange}
                        placeholder="e.g., 2022"
                        min="2000"
                        max={CURRENT_YEAR}
                      />
                    </div>
                    <div className="form-group">
                      <label>Fuel Type</label>
                      <select
                        name="fuel_type"
                        value={specInfo.fuel_type}
                        onChange={handleSpecChange}
                      >
                        {FUEL_OPTIONS.map((option) => (
                          <option key={option} value={option}>
                            {option}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>

                  <div className="form-group">
                    <label>Seating Capacity</label>
                    <input
                      type="number"
                      name="seating_capacity"
                      value={specInfo.seating_capacity}
                      onChange={handleSpecChange}
                      placeholder="e.g., 4"
                      min="1"
                      max="10"
                    />
                  </div>
                </div>
              )}

              {addStep === 3 && (
                <div className="form-section">
                  <h3>Document Links</h3>
                  <p className="section-info">Paste publicly accessible URLs for each document. Cloud storage links are acceptable.</p>

                  <div className="form-group">
                    <label>RC Document URL</label>
                    <input
                      type="url"
                      name="rcUrl"
                      value={documentUrls.rcUrl}
                      onChange={handleDocumentUrlChange}
                      placeholder="https://storage.example.com/rc.pdf"
                    />
                    <span className="helper-text">Required. We verify this during approval.</span>
                  </div>

                  <div className="form-group">
                    <label>Insurance Document URL</label>
                    <input
                      type="url"
                      name="insuranceUrl"
                      value={documentUrls.insuranceUrl}
                      onChange={handleDocumentUrlChange}
                      placeholder="https://storage.example.com/insurance.pdf"
                    />
                    <span className="helper-text">Required. Ensure the policy is valid.</span>
                  </div>

                  <div className="form-group">
                    <label>Permit URL (optional)</label>
                    <input
                      type="url"
                      name="permitUrl"
                      value={documentUrls.permitUrl}
                      onChange={handleDocumentUrlChange}
                      placeholder="https://storage.example.com/permit.pdf"
                    />
                  </div>

                  <div className="form-group">
                    <label>Fitness Certificate URL (optional)</label>
                    <input
                      type="url"
                      name="fitnessUrl"
                      value={documentUrls.fitnessUrl}
                      onChange={handleDocumentUrlChange}
                      placeholder="https://storage.example.com/fitness.pdf"
                    />
                  </div>
                </div>
              )}

              {addStep === 4 && (
                <div className="form-section">
                  <h3>Vehicle Photos</h3>
                  <p className="section-info">Add at least one photo URL. Multiple angles help speed up verification.</p>

                  {photoUrls.map((url, index) => (
                    <div className="photo-input-row" key={`photo-url-${index}`}>
                      <input
                        type="url"
                        value={url}
                        onChange={(event) => handlePhotoUrlChange(index, event.target.value)}
                        placeholder="https://storage.example.com/vehicle-front.jpg"
                      />
                      {photoUrls.length > 1 && (
                        <button
                          type="button"
                          className="btn-secondary remove-photo-btn"
                          onClick={() => removePhotoField(index)}
                        >
                          Remove
                        </button>
                      )}
                    </div>
                  ))}

                  <button
                    type="button"
                    className="btn-secondary add-photo-btn"
                    onClick={addPhotoField}
                  >
                    Add another photo link
                  </button>
                </div>
              )}
            </div>

            <div className="step-actions">
              <button
                className="btn-secondary"
                type="button"
                onClick={() => {
                  resetForm();
                  setError('');
                }}
                disabled={submitLoading}
              >
                Cancel
              </button>

              {addStep > 1 && (
                <button
                  className="btn-secondary"
                  type="button"
                  onClick={() => setAddStep(addStep - 1)}
                  disabled={submitLoading}
                >
                  Previous Step
                </button>
              )}

              {addStep < 4 ? (
                <button
                  className="btn-primary"
                  type="button"
                  onClick={() => setAddStep(addStep + 1)}
                  disabled={!currentStepIsValid || submitLoading}
                >
                  Next Step
                </button>
              ) : (
                <button
                  className="btn-primary"
                  type="button"
                  onClick={handleAddVehicle}
                  disabled={!validateStep(4) || submitLoading}
                >
                  {submitLoading ? 'Submitting...' : 'Submit Vehicle'}
                </button>
              )}
            </div>
          </div>
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
