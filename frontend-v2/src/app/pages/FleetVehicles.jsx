import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import fleetService from '../../services/fleet.service';
import './FleetVehicles.css';

const CATEGORY_OPTIONS = ['AUTO', 'BIKE', 'SEDAN', 'SUV', 'LUXURY'];

function FleetVehicles() {
  const navigate = useNavigate();
  const token = localStorage.getItem('jwt_token');
  
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  
  // Add vehicle form
  const [showAddForm, setShowAddForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    registration_no: '',
    category: 'AUTO'
  });
  const [documents, setDocuments] = useState({
    rc: null,
    insurance: null,
    permit: null,
    vehiclePhoto: null
  });
  const [fileErrors, setFileErrors] = useState({});

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
        navigate('/app/fleet/dashboard');
        return;
      }
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const validateFile = (file, fieldName, maxSizeMB = 5) => {
    if (!file) return {};
    
    const maxSize = maxSizeMB * 1024 * 1024;
    if (file.size > maxSize) {
      return { [fieldName]: `File size must be less than ${maxSizeMB}MB` };
    }
    
    const allowedTypes = ['image/jpeg', 'image/png', 'application/pdf'];
    if (!allowedTypes.includes(file.type)) {
      return { [fieldName]: 'Only JPG, PNG, or PDF files are allowed' };
    }
    
    return {};
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleFileChange = (e) => {
    const { name, files } = e.target;
    const file = files[0];
    
    if (file) {
      const errors = validateFile(file, name);
      if (Object.keys(errors).length > 0) {
        setFileErrors(prev => ({ ...prev, ...errors }));
        return;
      }
    }
    
    setDocuments(prev => ({ ...prev, [name]: file || null }));
    setFileErrors(prev => ({ ...prev, [name]: undefined }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    
    if (!formData.registration_no.trim()) {
      setError('Registration number is required');
      return;
    }
    
    if (!documents.rc) {
      setFileErrors(prev => ({ ...prev, rc: 'RC document is required' }));
      return;
    }
    
    if (!documents.insurance) {
      setFileErrors(prev => ({ ...prev, insurance: 'Insurance document is required' }));
      return;
    }

    try {
      setSubmitting(true);
      
      // For now, use URL-based API (backend doesn't have file upload for vehicles yet)
      // Convert files to data URLs temporarily
      const rcUrl = documents.rc ? await fileToDataUrl(documents.rc) : null;
      const insuranceUrl = documents.insurance ? await fileToDataUrl(documents.insurance) : null;
      const permitUrl = documents.permit ? await fileToDataUrl(documents.permit) : null;
      const photoUrl = documents.vehiclePhoto ? await fileToDataUrl(documents.vehiclePhoto) : null;
      
      const vehicleData = {
        registration_no: formData.registration_no.trim().toUpperCase(),
        category: formData.category,
        documents: [
          { document_type: 'RC', file_url: rcUrl },
          { document_type: 'INSURANCE', file_url: insuranceUrl },
        ]
      };
      
      if (permitUrl) {
        vehicleData.documents.push({ document_type: 'PERMIT', file_url: permitUrl });
      }
      if (photoUrl) {
        vehicleData.documents.push({ document_type: 'VEHICLE_PHOTO', file_url: photoUrl });
      }
      
      await fleetService.addVehicle(vehicleData);
      
      setSuccess('Vehicle added successfully!');
      resetForm();
      fetchVehicles();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const fileToDataUrl = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  };

  const resetForm = () => {
    setShowAddForm(false);
    setFormData({ registration_no: '', category: 'AUTO' });
    setDocuments({ rc: null, insurance: null, permit: null, vehiclePhoto: null });
    setFileErrors({});
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
        <button className="btn-back" onClick={() => navigate('/app/fleet/dashboard')}>
          ← Back
        </button>
        <h1>🚗 Fleet Vehicles</h1>
        <button className="btn-add" onClick={() => setShowAddForm(true)}>
          + Add Vehicle
        </button>
      </header>

      {error && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      {/* Add Vehicle Form */}
      {showAddForm && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h2>Add New Vehicle</h2>
              <button className="btn-close" onClick={resetForm}>×</button>
            </div>
            
            <form onSubmit={handleSubmit} className="add-vehicle-form">
              <div className="form-group">
                <label htmlFor="registration_no">Registration Number *</label>
                <input
                  type="text"
                  id="registration_no"
                  name="registration_no"
                  value={formData.registration_no}
                  onChange={handleInputChange}
                  placeholder="e.g., TS01AB1234"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="category">Vehicle Category *</label>
                <select
                  id="category"
                  name="category"
                  value={formData.category}
                  onChange={handleInputChange}
                >
                  {CATEGORY_OPTIONS.map(cat => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                </select>
              </div>

              <h3>Required Documents</h3>

              <div className="form-group file-group">
                <label htmlFor="rc">Registration Certificate (RC) *</label>
                <div className="file-input-wrapper">
                  <input
                    type="file"
                    id="rc"
                    name="rc"
                    onChange={handleFileChange}
                    accept=".pdf,.jpg,.jpeg,.png"
                  />
                  <span className="file-name">
                    {documents.rc ? documents.rc.name : 'Choose file'}
                  </span>
                </div>
                {fileErrors.rc && <span className="error">{fileErrors.rc}</span>}
              </div>

              <div className="form-group file-group">
                <label htmlFor="insurance">Insurance *</label>
                <div className="file-input-wrapper">
                  <input
                    type="file"
                    id="insurance"
                    name="insurance"
                    onChange={handleFileChange}
                    accept=".pdf,.jpg,.jpeg,.png"
                  />
                  <span className="file-name">
                    {documents.insurance ? documents.insurance.name : 'Choose file'}
                  </span>
                </div>
                {fileErrors.insurance && <span className="error">{fileErrors.insurance}</span>}
              </div>

              <h3>Optional Documents</h3>

              <div className="form-group file-group">
                <label htmlFor="permit">Permit</label>
                <div className="file-input-wrapper">
                  <input
                    type="file"
                    id="permit"
                    name="permit"
                    onChange={handleFileChange}
                    accept=".pdf,.jpg,.jpeg,.png"
                  />
                  <span className="file-name">
                    {documents.permit ? documents.permit.name : 'Choose file'}
                  </span>
                </div>
                {fileErrors.permit && <span className="error">{fileErrors.permit}</span>}
              </div>

              <div className="form-group file-group">
                <label htmlFor="vehiclePhoto">Vehicle Photo</label>
                <div className="file-input-wrapper">
                  <input
                    type="file"
                    id="vehiclePhoto"
                    name="vehiclePhoto"
                    onChange={handleFileChange}
                    accept=".jpg,.jpeg,.png"
                  />
                  <span className="file-name">
                    {documents.vehiclePhoto ? documents.vehiclePhoto.name : 'Choose file'}
                  </span>
                </div>
                {fileErrors.vehiclePhoto && <span className="error">{fileErrors.vehiclePhoto}</span>}
              </div>

              <div className="form-actions">
                <button type="button" className="btn-cancel" onClick={resetForm} disabled={submitting}>
                  Cancel
                </button>
                <button type="submit" className="btn-submit" disabled={submitting}>
                  {submitting ? 'Adding...' : 'Add Vehicle'}
                </button>
              </div>
            </form>
          </div>
        </div>
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
