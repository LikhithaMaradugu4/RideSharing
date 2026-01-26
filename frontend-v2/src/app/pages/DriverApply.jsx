import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import driverService from '../../services/driver.service';
import './DriverApply.css';

function DriverApply() {
  const navigate = useNavigate();
  const { tenantId } = useParams();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [driverProfile, setDriverProfile] = useState(null);
  
  const [formData, setFormData] = useState({
    drivingLicense: null,
    aadhaar: null,
    pan: null,
    driverPhoto: null,
    notes: ''
  });

  const [fileErrors, setFileErrors] = useState({});

  useEffect(() => {
    checkDriverStatus();
  }, []);

  const checkDriverStatus = async () => {
    try {
      setLoading(true);
      setError(null);

      const token = localStorage.getItem('jwt_token');
      if (!token) {
        setError('Authentication token not found. Please log in again.');
        navigate('/login');
        return;
      }

      const profile = await driverService.getMyProfile(token);
      
      if (profile) {
        setDriverProfile(profile);
        
        if (profile.approval_status === 'PENDING') {
          // Application is under review
          setError('Your driver application is under review.');
        } else if (profile.approval_status === 'APPROVED') {
          // Already approved, redirect to dashboard
          navigate('/app/driver/dashboard');
        }
      }
    } catch (err) {
      // No driver profile exists, allow application
      setDriverProfile(null);
    } finally {
      setLoading(false);
    }
  };

  const validateFile = (file, fieldName, maxSizeMB = 5) => {
    const errors = {};

    if (!file) {
      errors[fieldName] = 'File is required';
      return errors;
    }

    const maxSize = maxSizeMB * 1024 * 1024;
    if (file.size > maxSize) {
      errors[fieldName] = `File size must be less than ${maxSizeMB}MB`;
      return errors;
    }

    const allowedTypes = ['image/jpeg', 'image/png', 'application/pdf'];
    if (!allowedTypes.includes(file.type)) {
      errors[fieldName] = 'Only JPG, PNG, or PDF files are allowed';
      return errors;
    }

    return errors;
  };

  const handleFileChange = (e) => {
    const { name, files } = e.target;
    const file = files ? files[0] : null;

    setFileErrors(prev => {
      const updated = { ...prev };
      delete updated[name];
      return updated;
    });

    if (file) {
      const errors = validateFile(file, name);
      if (Object.keys(errors).length > 0) {
        setFileErrors(prev => ({ ...prev, ...errors }));
        return;
      }
    }

    setFormData(prev => ({
      ...prev,
      [name]: file
    }));
  };

  const handleTextChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validate tenant selection
    if (!tenantId) {
      setError('Tenant selection is required. Please go back and select a tenant.');
      return;
    }

    // Validation
    if (!formData.drivingLicense) {
      setFileErrors(prev => ({ ...prev, drivingLicense: 'Driving License is required' }));
      return;
    }

    if (!formData.driverPhoto) {
      setFileErrors(prev => ({ ...prev, driverPhoto: 'Driver Photo is required' }));
      return;
    }

    if (!formData.aadhaar && !formData.pan) {
      setFileErrors(prev => ({ ...prev, aadhaar: 'At least one of Aadhaar or PAN is required' }));
      return;
    }

    try {
      setSubmitting(true);
      setError(null);

      const token = localStorage.getItem('jwt_token');

      // Build FormData for multipart/form-data
      const multipartData = new FormData();
      multipartData.append('tenant_id', tenantId);
      multipartData.append('driver_type', 'INDEPENDENT');
      multipartData.append('driving_license', formData.drivingLicense);
      multipartData.append('driver_photo', formData.driverPhoto);
      
      if (formData.aadhaar) {
        multipartData.append('aadhaar', formData.aadhaar);
      }
      
      if (formData.pan) {
        multipartData.append('pan', formData.pan);
      }

      if (formData.notes.trim()) {
        multipartData.append('notes', formData.notes);
      }

      const result = await driverService.applyWithDocuments(token, multipartData);

      // Success - show message and redirect
      setError(null);
      setTimeout(() => {
        navigate('/app/home');
      }, 2000);
    } catch (err) {
      setError(err.message || 'Failed to submit application. Please try again.');
      console.error('Error:', err);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return <div className="driver-apply-container"><p>Loading...</p></div>;
  }

  // If application is under review, show message and disable form
  if (driverProfile && driverProfile.approval_status === 'PENDING') {
    return (
      <div className="driver-apply-container">
        <div className="apply-card">
          <h1>Driver Application</h1>
          <div className="info-message">
            <p>Your driver application is under review. You will be notified once a decision has been made.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="driver-apply-container">
      <div className="apply-card">
        <h1>Apply for Driver Capability</h1>
        <p className="subtitle">Complete the form below to apply as a driver</p>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit} className="apply-form">
          {/* Driving License */}
          <div className="form-group">
            <label htmlFor="drivingLicense">Driving License * (JPG/PNG/PDF, max 5MB)</label>
            <input
              type="file"
              id="drivingLicense"
              name="drivingLicense"
              onChange={handleFileChange}
              accept=".jpg,.jpeg,.png,.pdf"
              disabled={submitting}
            />
            {fileErrors.drivingLicense && <p className="error-text">{fileErrors.drivingLicense}</p>}
            {formData.drivingLicense && <p className="success-text">✓ {formData.drivingLicense.name}</p>}
          </div>

          {/* Driver Photo */}
          <div className="form-group">
            <label htmlFor="driverPhoto">Driver Photo * (JPG/PNG, max 5MB)</label>
            <input
              type="file"
              id="driverPhoto"
              name="driverPhoto"
              onChange={handleFileChange}
              accept=".jpg,.jpeg,.png"
              disabled={submitting}
            />
            {fileErrors.driverPhoto && <p className="error-text">{fileErrors.driverPhoto}</p>}
            {formData.driverPhoto && <p className="success-text">✓ {formData.driverPhoto.name}</p>}
          </div>

          {/* Aadhaar or PAN */}
          <div className="form-note">
            <p>Upload at least one: Aadhaar OR PAN</p>
          </div>

          <div className="form-group">
            <label htmlFor="aadhaar">Aadhaar (JPG/PNG/PDF, max 5MB)</label>
            <input
              type="file"
              id="aadhaar"
              name="aadhaar"
              onChange={handleFileChange}
              accept=".jpg,.jpeg,.png,.pdf"
              disabled={submitting}
            />
            {fileErrors.aadhaar && <p className="error-text">{fileErrors.aadhaar}</p>}
            {formData.aadhaar && <p className="success-text">✓ {formData.aadhaar.name}</p>}
          </div>

          <div className="form-group">
            <label htmlFor="pan">PAN (JPG/PNG/PDF, max 5MB)</label>
            <input
              type="file"
              id="pan"
              name="pan"
              onChange={handleFileChange}
              accept=".jpg,.jpeg,.png,.pdf"
              disabled={submitting}
            />
            {fileErrors.pan && <p className="error-text">{fileErrors.pan}</p>}
            {formData.pan && <p className="success-text">✓ {formData.pan.name}</p>}
          </div>

          {/* Notes */}
          <div className="form-group">
            <label htmlFor="notes">Additional Notes (Optional)</label>
            <textarea
              id="notes"
              name="notes"
              value={formData.notes}
              onChange={handleTextChange}
              placeholder="Any additional information you'd like to share..."
              rows="4"
              disabled={submitting}
            ></textarea>
          </div>

          <button type="submit" className="btn btn-primary" disabled={submitting}>
            {submitting ? 'Submitting...' : 'Submit Application'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default DriverApply;
