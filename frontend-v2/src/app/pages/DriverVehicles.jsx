import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import DriverLayout from '../layout/DriverLayout';
import driverService from '../../services/driver.service';
import './DriverVehicles.css';

export default function DriverVehicles() {
  const navigate = useNavigate();
  const token = localStorage.getItem('jwt_token');
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [addStep, setAddStep] = useState(1);
  const [submitLoading, setSubmitLoading] = useState(false);

  const [basicInfo, setBasicInfo] = useState({
    plate_number: '',
    vin: '',
    color: ''
  });

  const [specifications, setSpecifications] = useState({
    make: '',
    model: '',
    year: '',
    category: 'SEDAN'
  });

  const [documents, setDocuments] = useState({
    registration_doc: null,
    insurance_doc: null,
    pollution_doc: null
  });

  const [photos, setPhotos] = useState({
    front_photo: null,
    rear_photo: null,
    left_photo: null,
    right_photo: null
  });

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
      setError('');
      const data = await driverService.getMyVehicles(token);
      setVehicles(data);
    } catch (err) {
      setError(err.message || 'Failed to load vehicles');
      setVehicles([]);
    } finally {
      setLoading(false);
    }
  };

  const handleBasicInfoChange = (e) => {
    const { name, value } = e.target;
    setBasicInfo(prev => ({ ...prev, [name]: value }));
  };

  const handleSpecChange = (e) => {
    const { name, value } = e.target;
    setSpecifications(prev => ({ ...prev, [name]: value }));
  };

  const handleDocumentChange = (e) => {
    const { name, files } = e.target;
    if (files && files[0]) {
      setDocuments(prev => ({ ...prev, [name]: files[0] }));
    }
  };

  const handlePhotoChange = (e) => {
    const { name, files } = e.target;
    if (files && files[0]) {
      setPhotos(prev => ({ ...prev, [name]: files[0] }));
    }
  };

  const validateStep = (step) => {
    if (step === 1) {
      return basicInfo.plate_number.trim() && basicInfo.vin.trim() && basicInfo.color.trim();
    }
    if (step === 2) {
      return specifications.make.trim() && specifications.model.trim() && specifications.year;
    }
    if (step === 3) {
      return documents.registration_doc && documents.insurance_doc && documents.pollution_doc;
    }
    if (step === 4) {
      return photos.front_photo && photos.rear_photo && photos.left_photo && photos.right_photo;
    }
    return false;
  };

  const handleAddVehicle = async () => {
    try {
      setSubmitLoading(true);
      setError('');
      // Backend expects JSON: { category, registration_no, documents: [{document_type, file_url}] }
      const docUrl = (file) => file ? `local://driver_uploads/${file.name}` : null;
      const vehicleData = {
        category: specifications.category,
        registration_no: basicInfo.plate_number,
        documents: [
          { document_type: 'RC', file_url: docUrl(documents.registration_doc) },
          { document_type: 'INSURANCE', file_url: docUrl(documents.insurance_doc) },
          { document_type: 'VEHICLE_PHOTO', file_url: docUrl(photos.front_photo) }
        ].filter(d => d.file_url)
      };

      // Optionally include FITNESS document mapped from pollution_doc if provided
      if (documents.pollution_doc) {
        vehicleData.documents.push({ document_type: 'FITNESS', file_url: docUrl(documents.pollution_doc) });
      }

      await driverService.createVehicle(token, vehicleData);

      setShowAddForm(false);
      setAddStep(1);
      setBasicInfo({ plate_number: '', vin: '', color: '' });
      setSpecifications({ make: '', model: '', year: '', category: 'SEDAN' });
      setDocuments({ registration_doc: null, insurance_doc: null, pollution_doc: null });
      setPhotos({ front_photo: null, rear_photo: null, left_photo: null, right_photo: null });

      await fetchVehicles();
    } catch (err) {
      setError(err.message || 'Failed to add vehicle');
    } finally {
      setSubmitLoading(false);
    }
  };

  const handleApproveVehicle = async (vehicleId) => {
    try {
      setError('');
      await driverService.updateVehicle(token, vehicleId, { action: 'approve' });
      await fetchVehicles();
    } catch (err) {
      setError(err.message || 'Failed to approve vehicle');
    }
  };

  const handleRemoveVehicle = async (vehicleId) => {
    if (!window.confirm('Are you sure you want to remove this vehicle?')) return;

    try {
      setError('');
      await driverService.removeVehicle(token, vehicleId);
      await fetchVehicles();
    } catch (err) {
      setError(err.message || 'Failed to remove vehicle');
    }
  };

  const getStatusBadgeClass = (status) => {
    const statusMap = {
      'ACTIVE': 'badge-approved',
      'PENDING': 'badge-pending',
      'REJECTED': 'badge-rejected',
      'INACTIVE': 'badge-inactive'
    };
    return statusMap[status] || 'badge-pending';
  };

  const getStatusLabel = (status) => {
    const labels = {
      'ACTIVE': 'Active',
      'PENDING': 'Under Review',
      'REJECTED': 'Rejected',
      'INACTIVE': 'Inactive'
    };
    return labels[status] || status;
  };

  return (
    <DriverLayout>
      <div className="driver-vehicles-container">
        <div className="vehicles-header">
          <h1>My Vehicles</h1>
          {!showAddForm && (
            <button
              className="btn-primary btn-add-vehicle"
              onClick={() => setShowAddForm(true)}
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

        {showAddForm && (
          <div className="add-vehicle-card">
            <h2>Add New Vehicle</h2>
            
            <div className="step-indicator">
              {[1, 2, 3, 4].map(step => (
                <div
                  key={step}
                  className={`step ${step === addStep ? 'active' : ''} ${step < addStep ? 'completed' : ''}`}
                >
                  <span className="step-number">{step}</span>
                  <span className="step-label">
                    {step === 1 && 'Basic Info'}
                    {step === 2 && 'Specifications'}
                    {step === 3 && 'Documents'}
                    {step === 4 && 'Photos'}
                  </span>
                </div>
              ))}
            </div>

            <div className="step-content">
              {addStep === 1 && (
                <div className="form-section">
                  <h3>Basic Vehicle Information</h3>
                  
                  <div className="form-group">
                    <label>License Plate Number</label>
                    <input
                      type="text"
                      name="plate_number"
                      value={basicInfo.plate_number}
                      onChange={handleBasicInfoChange}
                      placeholder="e.g., ABC 1234"
                      maxLength="20"
                    />
                  </div>

                  <div className="form-group">
                    <label>VIN (Vehicle Identification Number)</label>
                    <input
                      type="text"
                      name="vin"
                      value={basicInfo.vin}
                      onChange={handleBasicInfoChange}
                      placeholder="17-character VIN"
                      maxLength="17"
                    />
                  </div>

                  <div className="form-group">
                    <label>Color</label>
                    <select
                      name="color"
                      value={basicInfo.color}
                      onChange={handleBasicInfoChange}
                    >
                      <option value="">Select color</option>
                      <option value="BLACK">Black</option>
                      <option value="WHITE">White</option>
                      <option value="SILVER">Silver</option>
                      <option value="GRAY">Gray</option>
                      <option value="RED">Red</option>
                      <option value="BLUE">Blue</option>
                      <option value="GREEN">Green</option>
                      <option value="YELLOW">Yellow</option>
                      <option value="BROWN">Brown</option>
                      <option value="OTHER">Other</option>
                    </select>
                  </div>
                </div>
              )}

              {addStep === 2 && (
                <div className="form-section">
                  <h3>Vehicle Specifications</h3>
                  
                  <div className="form-row">
                    <div className="form-group">
                      <label>Make (Brand)</label>
                      <input
                        type="text"
                        name="make"
                        value={specifications.make}
                        onChange={handleSpecChange}
                        placeholder="e.g., Toyota"
                      />
                    </div>
                    <div className="form-group">
                      <label>Model</label>
                      <input
                        type="text"
                        name="model"
                        value={specifications.model}
                        onChange={handleSpecChange}
                        placeholder="e.g., Corolla"
                      />
                    </div>
                  </div>

                  <div className="form-row">
                    <div className="form-group">
                      <label>Year</label>
                      <input
                        type="number"
                        name="year"
                        value={specifications.year}
                        onChange={handleSpecChange}
                        placeholder="e.g., 2021"
                        min="2010"
                        max={new Date().getFullYear()}
                      />
                    </div>
                    <div className="form-group">
                      <label>Category</label>
                      <select
                        name="category"
                        value={specifications.category}
                        onChange={handleSpecChange}
                      >
                        <option value="SEDAN">Sedan</option>
                        <option value="SUV">SUV</option>
                        <option value="HATCHBACK">Hatchback</option>
                        <option value="VAN">Van</option>
                        <option value="PICKUP">Pickup</option>
                      </select>
                    </div>
                  </div>
                </div>
              )}

              {addStep === 3 && (
                <div className="form-section">
                  <h3>Required Documents</h3>
                  <p className="section-info">Upload clear, legible copies of all documents</p>
                  
                  <div className="form-group">
                    <label>Registration Certificate</label>
                    <input
                      type="file"
                      name="registration_doc"
                      onChange={handleDocumentChange}
                      accept="image/*,.pdf"
                    />
                    {documents.registration_doc && (
                      <span className="file-selected">{documents.registration_doc.name}</span>
                    )}
                  </div>

                  <div className="form-group">
                    <label>Insurance Document</label>
                    <input
                      type="file"
                      name="insurance_doc"
                      onChange={handleDocumentChange}
                      accept="image/*,.pdf"
                    />
                    {documents.insurance_doc && (
                      <span className="file-selected">{documents.insurance_doc.name}</span>
                    )}
                  </div>

                  <div className="form-group">
                    <label>Pollution Certificate</label>
                    <input
                      type="file"
                      name="pollution_doc"
                      onChange={handleDocumentChange}
                      accept="image/*,.pdf"
                    />
                    {documents.pollution_doc && (
                      <span className="file-selected">{documents.pollution_doc.name}</span>
                    )}
                  </div>
                </div>
              )}

              {addStep === 4 && (
                <div className="form-section">
                  <h3>Vehicle Photos</h3>
                  <p className="section-info">Clear photos from each angle for verification</p>
                  
                  <div className="form-row">
                    <div className="form-group">
                      <label>Front View</label>
                      <input
                        type="file"
                        name="front_photo"
                        onChange={handlePhotoChange}
                        accept="image/*"
                      />
                      {photos.front_photo && (
                        <span className="file-selected">{photos.front_photo.name}</span>
                      )}
                    </div>
                    <div className="form-group">
                      <label>Rear View</label>
                      <input
                        type="file"
                        name="rear_photo"
                        onChange={handlePhotoChange}
                        accept="image/*"
                      />
                      {photos.rear_photo && (
                        <span className="file-selected">{photos.rear_photo.name}</span>
                      )}
                    </div>
                  </div>

                  <div className="form-row">
                    <div className="form-group">
                      <label>Left Side View</label>
                      <input
                        type="file"
                        name="left_photo"
                        onChange={handlePhotoChange}
                        accept="image/*"
                      />
                      {photos.left_photo && (
                        <span className="file-selected">{photos.left_photo.name}</span>
                      )}
                    </div>
                    <div className="form-group">
                      <label>Right Side View</label>
                      <input
                        type="file"
                        name="right_photo"
                        onChange={handlePhotoChange}
                        accept="image/*"
                      />
                      {photos.right_photo && (
                        <span className="file-selected">{photos.right_photo.name}</span>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>

            <div className="step-actions">
              <button
                className="btn-secondary"
                onClick={() => {
                  setShowAddForm(false);
                  setAddStep(1);
                }}
                disabled={submitLoading}
              >
                Cancel
              </button>

              {addStep > 1 && (
                <button
                  className="btn-secondary"
                  onClick={() => setAddStep(addStep - 1)}
                  disabled={submitLoading}
                >
                  Previous Step
                </button>
              )}

              {addStep < 4 ? (
                <button
                  className="btn-primary"
                  onClick={() => setAddStep(addStep + 1)}
                  disabled={!validateStep(addStep) || submitLoading}
                >
                  Next Step
                </button>
              ) : (
                <button
                  className="btn-primary"
                  onClick={handleAddVehicle}
                  disabled={!validateStep(addStep) || submitLoading}
                >
                  {submitLoading ? 'Adding Vehicle...' : 'Add Vehicle'}
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
            <p>No vehicles added yet</p>
            <button
              className="btn-primary"
              onClick={() => setShowAddForm(true)}
            >
              Add Your First Vehicle
            </button>
          </div>
        ) : (
          <div className="vehicles-grid">
            {vehicles.map(vehicle => (
              <div key={vehicle.vehicle_id} className="vehicle-card">
                <div className="vehicle-header">
                  <div className="vehicle-title">
                    <h3>{specifications.year || ''} {specifications.make || ''} {specifications.model || ''}</h3>
                    <span className={`badge ${getStatusBadgeClass(vehicle.status)}`}>
                      {getStatusLabel(vehicle.status)}
                    </span>
                  </div>
                  <span className="vehicle-category">{vehicle.category}</span>
                </div>

                <div className="vehicle-details">
                  <div className="detail-item">
                    <span className="detail-label">Plate Number</span>
                    <span className="detail-value">{vehicle.registration_no}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">VIN</span>
                    <span className="detail-value">{basicInfo.vin}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Color</span>
                    <span className="detail-value">{basicInfo.color}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Added On</span>
                    <span className="detail-value">
                      {/* created_at not in response; show category */}
                      {vehicle.category}
                    </span>
                  </div>
                </div>

                <div className="vehicle-actions">
                  {vehicle.status === 'PENDING' && (
                    <span className="action-info">Awaiting admin review</span>
                  )}
                  {vehicle.status === 'REJECTED' && (
                    <button
                      className="btn-secondary"
                      onClick={() => handleRemoveVehicle(vehicle.vehicle_id)}
                    >
                      Remove
                    </button>
                  )}
                  {vehicle.status === 'ACTIVE' && (
                    <span className="action-info">Ready to use</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </DriverLayout>
  );
}
