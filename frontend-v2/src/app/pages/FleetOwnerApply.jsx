import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import driverService from '../../services/driver.service';
import './FleetOwnerApply.css';

function FleetOwnerApply() {
  const navigate = useNavigate();
  const { tenantId } = useParams();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [fileErrors, setFileErrors] = useState({});

  const [formData, setFormData] = useState({
    fleetName: '',
    registrationCertificate: null,
    insurance: null,
    permit: null,
    photo: null,
    notes: ''
  });

  useEffect(() => {
    if (!tenantId) {
      setError('Tenant selection is required. Please go back and select a tenant.');
    }
  }, [tenantId]);

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
    const file = files[0];

    const newErrors = validateFile(file, name);
    if (Object.keys(newErrors).length > 0) {
      setFileErrors(prev => ({ ...prev, ...newErrors }));
      return;
    }

    setFormData(prev => ({
      ...prev,
      [name]: file
    }));

    setFileErrors(prev => ({
      ...prev,
      [name]: undefined
    }));
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!tenantId) {
      setError('Tenant selection is required. Please go back and select a tenant.');
      return;
    }

    if (!formData.fleetName.trim()) {
      setError('Fleet name is required');
      return;
    }

    if (!formData.registrationCertificate) {
      setFileErrors(prev => ({ ...prev, registrationCertificate: 'Registration Certificate is required' }));
      return;
    }

    if (!formData.insurance) {
      setFileErrors(prev => ({ ...prev, insurance: 'Insurance is required' }));
      return;
    }

    if (!formData.permit) {
      setFileErrors(prev => ({ ...prev, permit: 'Permit is required' }));
      return;
    }

    if (!formData.photo) {
      setFileErrors(prev => ({ ...prev, photo: 'Fleet Photo is required' }));
      return;
    }

    try {
      setSubmitting(true);
      setError(null);

      const token = localStorage.getItem('jwt_token');

      // Convert files to data URLs for transmission
      const registrationCertUrl = await fileToDataUrl(formData.registrationCertificate);
      const insuranceUrl = await fileToDataUrl(formData.insurance);
      const permitUrl = await fileToDataUrl(formData.permit);
      const photoUrl = await fileToDataUrl(formData.photo);

      // Build JSON request matching FleetApplyRequest schema
      const requestData = {
        tenant_id: parseInt(tenantId),
        fleet_name: formData.fleetName,
        fleet_type: 'BUSINESS',
        documents: [
          {
            document_type: 'REGISTRATION_CERTIFICATE',
            file_url: registrationCertUrl
          },
          {
            document_type: 'INSURANCE',
            file_url: insuranceUrl
          },
          {
            document_type: 'PERMIT',
            file_url: permitUrl
          },
          {
            document_type: 'FLEET_PHOTO',
            file_url: photoUrl
          }
        ]
      };

      const response = await fetch('http://localhost:8000/api/v2/fleet/apply', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(requestData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to apply for fleet owner');
      }

      const result = await response.json();
      
      // Success
      navigate('/app/fleet-owner/dashboard', {
        state: { 
          message: 'Fleet application submitted successfully. It is now under review.',
          fleetId: result.fleet_id
        }
      });
    } catch (err) {
      setError(err.message || 'An error occurred. Please try again.');
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  // Helper function to convert File to data URL
  const fileToDataUrl = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  };

  return (
    <div className="fleet-apply-container">
      <div className="fleet-apply-card">
        <h1>Apply as Fleet Owner</h1>
        <p className="subtitle">Build your fleet and start operating</p>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit} className="fleet-apply-form">
          {/* Fleet Name */}
          <div className="form-group">
            <label htmlFor="fleetName">Fleet Name *</label>
            <input
              type="text"
              id="fleetName"
              name="fleetName"
              value={formData.fleetName}
              onChange={handleInputChange}
              placeholder="Enter your fleet name"
              required
            />
          </div>

          {/* File Upload Section */}
          <div className="file-upload-section">
            <h3>Required Documents</h3>

            {/* Registration Certificate */}
            <div className="form-group file-group">
              <label htmlFor="registrationCertificate">Registration Certificate *</label>
              <div className="file-input-wrapper">
                <input
                  type="file"
                  id="registrationCertificate"
                  name="registrationCertificate"
                  onChange={handleFileChange}
                  accept=".pdf,.jpg,.jpeg,.png"
                />
                <span className="file-name">
                  {formData.registrationCertificate
                    ? formData.registrationCertificate.name
                    : 'Choose file'}
                </span>
              </div>
              {fileErrors.registrationCertificate && (
                <span className="error">{fileErrors.registrationCertificate}</span>
              )}
            </div>

            {/* Insurance */}
            <div className="form-group file-group">
              <label htmlFor="insurance">Insurance Document *</label>
              <div className="file-input-wrapper">
                <input
                  type="file"
                  id="insurance"
                  name="insurance"
                  onChange={handleFileChange}
                  accept=".pdf,.jpg,.jpeg,.png"
                />
                <span className="file-name">
                  {formData.insurance ? formData.insurance.name : 'Choose file'}
                </span>
              </div>
              {fileErrors.insurance && (
                <span className="error">{fileErrors.insurance}</span>
              )}
            </div>

            {/* Permit */}
            <div className="form-group file-group">
              <label htmlFor="permit">Business Permit *</label>
              <div className="file-input-wrapper">
                <input
                  type="file"
                  id="permit"
                  name="permit"
                  onChange={handleFileChange}
                  accept=".pdf,.jpg,.jpeg,.png"
                />
                <span className="file-name">
                  {formData.permit ? formData.permit.name : 'Choose file'}
                </span>
              </div>
              {fileErrors.permit && (
                <span className="error">{fileErrors.permit}</span>
              )}
            </div>

            {/* Fleet Photo */}
            <div className="form-group file-group">
              <label htmlFor="photo">Fleet Photo *</label>
              <div className="file-input-wrapper">
                <input
                  type="file"
                  id="photo"
                  name="photo"
                  onChange={handleFileChange}
                  accept=".jpg,.jpeg,.png"
                />
                <span className="file-name">
                  {formData.photo ? formData.photo.name : 'Choose file'}
                </span>
              </div>
              {fileErrors.photo && (
                <span className="error">{fileErrors.photo}</span>
              )}
            </div>
          </div>

          {/* Notes */}
          <div className="form-group">
            <label htmlFor="notes">Additional Notes</label>
            <textarea
              id="notes"
              name="notes"
              value={formData.notes}
              onChange={handleInputChange}
              placeholder="Any additional information about your fleet..."
              rows="4"
            />
          </div>

          {/* Form Actions */}
          <div className="form-actions">
            <button
              type="button"
              className="btn-cancel"
              onClick={() => navigate('/')}
              disabled={submitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn-submit"
              disabled={submitting}
            >
              {submitting ? 'Submitting...' : 'Submit Application'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default FleetOwnerApply;
