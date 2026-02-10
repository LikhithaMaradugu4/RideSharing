import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import fleetService from '../../services/fleet.service';
import Icons from '../../components/Icons';
import './FleetOwnerApply.css';

function FleetOwnerApply() {
  const navigate = useNavigate();
  const { tenantId } = useParams();
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [fileErrors, setFileErrors] = useState({});

  const [formData, setFormData] = useState({
    fleetName: '',
    aadhaar: null,
    pan: null,
    gstCertificate: null,
    companyRegistration: null
  });

  useEffect(() => {
    if (!tenantId) {
      setError('Tenant selection is required. Please go back and select a tenant.');
    }
    
    // Check if user already has a fleet
    checkExistingFleet();
  }, [tenantId]);

  const checkExistingFleet = async () => {
    try {
      const fleet = await fleetService.checkFleetExists();
      if (fleet) {
        // Fleet already exists - redirect based on status
        if (fleet.approval_status === 'APPROVED') {
          navigate('/fleet-dashboard');
        } else {
          setSubmitted(true);
        }
      }
    } catch (err) {
      // No fleet exists - continue with application
    }
  };

  const validateFile = (file, fieldName, maxSizeMB = 5) => {
    const errors = {};

    if (!file) {
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

    if (file) {
      const newErrors = validateFile(file, name);
      if (Object.keys(newErrors).length > 0) {
        setFileErrors(prev => ({ ...prev, ...newErrors }));
        return;
      }
    }

    setFormData(prev => ({
      ...prev,
      [name]: file || null
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
    setError(null);

    if (!tenantId) {
      setError('Tenant selection is required. Please go back and select a tenant.');
      return;
    }

    if (!formData.fleetName.trim()) {
      setError('Fleet name is required');
      return;
    }

    // Validate at least one identity document
    if (!formData.aadhaar && !formData.pan) {
      setError('At least one of Aadhaar or PAN is required');
      return;
    }

    try {
      setSubmitting(true);

      // Build FormData for multipart upload
      const uploadData = new FormData();
      uploadData.append('tenant_id', tenantId);
      uploadData.append('fleet_name', formData.fleetName.trim());
      
      if (formData.aadhaar) {
        uploadData.append('aadhaar', formData.aadhaar);
      }
      if (formData.pan) {
        uploadData.append('pan', formData.pan);
      }
      if (formData.gstCertificate) {
        uploadData.append('gst_certificate', formData.gstCertificate);
      }
      if (formData.companyRegistration) {
        uploadData.append('company_registration', formData.companyRegistration);
      }

      await fleetService.applyWithDocuments(uploadData);
      
      // Success - show confirmation
      setSubmitted(true);
    } catch (err) {
      // Show backend error as-is
      setError(err.message || 'An error occurred. Please try again.');
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  // Show success/pending state
  if (submitted) {
    return (
      <div className="fleet-apply-container">
        <div className="fleet-apply-card success-card">
          <span className="success-icon"><Icons.Hourglass size={64} /></span>
          <h1>Application Under Review</h1>
          <p>Your fleet application has been submitted and is currently under review.</p>
          <p className="note">This usually takes 1-2 business days. We'll notify you once approved.</p>
          <button 
            className="btn-primary"
            onClick={() => navigate('/rider-dashboard')}
          >
            Go to Dashboard
          </button>
        </div>
      </div>
    );
  }

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
            <p className="section-note">At least one of Aadhaar or PAN is required</p>

            {/* Aadhaar */}
            <div className="form-group file-group">
              <label htmlFor="aadhaar">Aadhaar Card</label>
              <div className="file-input-wrapper">
                <input
                  type="file"
                  id="aadhaar"
                  name="aadhaar"
                  onChange={handleFileChange}
                  accept=".pdf,.jpg,.jpeg,.png"
                />
                <span className="file-name">
                  {formData.aadhaar ? formData.aadhaar.name : 'Choose file'}
                </span>
              </div>
              {fileErrors.aadhaar && (
                <span className="error">{fileErrors.aadhaar}</span>
              )}
            </div>

            {/* PAN */}
            <div className="form-group file-group">
              <label htmlFor="pan">PAN Card</label>
              <div className="file-input-wrapper">
                <input
                  type="file"
                  id="pan"
                  name="pan"
                  onChange={handleFileChange}
                  accept=".pdf,.jpg,.jpeg,.png"
                />
                <span className="file-name">
                  {formData.pan ? formData.pan.name : 'Choose file'}
                </span>
              </div>
              {fileErrors.pan && (
                <span className="error">{fileErrors.pan}</span>
              )}
            </div>

            <h3>Optional Documents</h3>

            {/* GST Certificate */}
            <div className="form-group file-group">
              <label htmlFor="gstCertificate">GST Certificate</label>
              <div className="file-input-wrapper">
                <input
                  type="file"
                  id="gstCertificate"
                  name="gstCertificate"
                  onChange={handleFileChange}
                  accept=".pdf,.jpg,.jpeg,.png"
                />
                <span className="file-name">
                  {formData.gstCertificate ? formData.gstCertificate.name : 'Choose file'}
                </span>
              </div>
              {fileErrors.gstCertificate && (
                <span className="error">{fileErrors.gstCertificate}</span>
              )}
            </div>

            {/* Company Registration */}
            <div className="form-group file-group">
              <label htmlFor="companyRegistration">Company Registration</label>
              <div className="file-input-wrapper">
                <input
                  type="file"
                  id="companyRegistration"
                  name="companyRegistration"
                  onChange={handleFileChange}
                  accept=".pdf,.jpg,.jpeg,.png"
                />
                <span className="file-name">
                  {formData.companyRegistration ? formData.companyRegistration.name : 'Choose file'}
                </span>
              </div>
              {fileErrors.companyRegistration && (
                <span className="error">{fileErrors.companyRegistration}</span>
              )}
            </div>
          </div>

          {/* Form Actions */}
          <div className="form-actions">
            <button
              type="button"
              className="btn-cancel"
              onClick={() => navigate('/rider-dashboard')}
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
