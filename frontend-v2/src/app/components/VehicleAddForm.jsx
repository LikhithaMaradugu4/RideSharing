import React, { useState } from 'react';
import './VehicleAddForm.css';

const CATEGORY_OPTIONS = ['AUTO', 'BIKE', 'SEDAN', 'SUV', 'LUXURY'];
const FUEL_OPTIONS = ['PETROL', 'DIESEL', 'CNG', 'EV'];
const CURRENT_YEAR = new Date().getFullYear();

/**
 * Shared Vehicle Add Form Component
 * Used by both DriverVehicles and FleetVehicles
 * Uses file-based document upload (consistent with Driver/Fleet owner applications)
 * 
 * Props:
 * - onSubmit: async function(vehicleData, specData, documentFiles) - called when form is submitted
 * - onCancel: function() - called when cancel button is clicked
 * - isSubmitting: boolean - controls disabled state of buttons
 * - mode: 'driver' | 'fleet' - determines some UI differences
 * - includeSpec: boolean - whether to include vehicle specifications step (default: true for driver, false for fleet)
 */
export default function VehicleAddForm({
  onSubmit,
  onCancel,
  isSubmitting = false,
  mode = 'driver',
  includeSpec = null
}) {
  // Determine if we should include spec step
  const showSpec = includeSpec !== null ? includeSpec : mode === 'driver';
  const totalSteps = showSpec ? 4 : 2;

  const [step, setStep] = useState(1);
  const [error, setError] = useState('');

  // Step 1: Basic Info
  const [basicInfo, setBasicInfo] = useState({
    registration_no: '',
    category: 'AUTO'
  });

  // Step 2 (if showSpec): Vehicle Specifications
  const [specInfo, setSpecInfo] = useState({
    manufacturer: '',
    model_name: '',
    manufacture_year: '',
    fuel_type: 'PETROL',
    seating_capacity: ''
  });

  // Documents Step: File uploads
  const [documents, setDocuments] = useState({
    rc: null,
    insurance: null,
    permit: null,
    fitness: null
  });
  const [fileErrors, setFileErrors] = useState({});

  // Photos Step: File uploads
  const [photos, setPhotos] = useState([null]);

  // File validation
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

  const handleBasicInfoChange = (e) => {
    const { name, value } = e.target;
    setBasicInfo(prev => ({ ...prev, [name]: value }));
    setError('');
  };

  const handleSpecChange = (e) => {
    const { name, value } = e.target;
    setSpecInfo(prev => ({ ...prev, [name]: value }));
    setError('');
  };

  const handleDocumentChange = (e) => {
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

  const handlePhotoChange = (index, file) => {
    if (file) {
      const errors = validateFile(file, `photo_${index}`);
      if (Object.keys(errors).length > 0) {
        setFileErrors(prev => ({ ...prev, [`photo_${index}`]: errors[`photo_${index}`] }));
        return;
      }
    }

    setPhotos(prev => {
      const next = [...prev];
      next[index] = file || null;
      return next;
    });
    setFileErrors(prev => ({ ...prev, [`photo_${index}`]: undefined }));
  };

  const addPhotoField = () => {
    setPhotos(prev => [...prev, null]);
  };

  const removePhotoField = (index) => {
    if (photos.length > 1) {
      setPhotos(prev => prev.filter((_, idx) => idx !== index));
    }
  };

  // Convert file to data URL for API submission
  const fileToDataUrl = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  };

  // Validation for each step
  const validateStep = (stepNum) => {
    if (stepNum === 1) {
      return basicInfo.registration_no.trim().length > 0 && basicInfo.category;
    }

    if (showSpec && stepNum === 2) {
      const year = Number(specInfo.manufacture_year);
      const seats = Number(specInfo.seating_capacity);
      return (
        specInfo.manufacturer.trim().length > 0 &&
        specInfo.model_name.trim().length > 0 &&
        !isNaN(year) && year >= 2000 && year <= CURRENT_YEAR &&
        !isNaN(seats) && seats > 0
      );
    }

    // Documents step
    const docsStep = showSpec ? 3 : 2;
    if (stepNum === docsStep) {
      return documents.rc && documents.insurance;
    }

    // Photos step
    const photosStep = showSpec ? 4 : 3;
    if (stepNum === photosStep) {
      return photos.some(p => p !== null);
    }

    return false;
  };

  const getStepNumber = (name) => {
    if (name === 'basic') return 1;
    if (name === 'spec') return showSpec ? 2 : -1;
    if (name === 'docs') return showSpec ? 3 : 2;
    if (name === 'photos') return showSpec ? 4 : 3;
    return -1;
  };

  const handleNext = () => {
    if (validateStep(step)) {
      setStep(step + 1);
      setError('');
    }
  };

  const handlePrevious = () => {
    if (step > 1) {
      setStep(step - 1);
      setError('');
    }
  };

  const handleSubmit = async () => {
    if (!validateStep(step)) {
      setError('Please complete all required fields');
      return;
    }

    try {
      // Build documents array with data URLs
      const documentsList = [];

      if (documents.rc) {
        const rcUrl = await fileToDataUrl(documents.rc);
        documentsList.push({ document_type: 'RC', file_url: rcUrl });
      }

      if (documents.insurance) {
        const insuranceUrl = await fileToDataUrl(documents.insurance);
        documentsList.push({ document_type: 'INSURANCE', file_url: insuranceUrl });
      }

      if (documents.permit) {
        const permitUrl = await fileToDataUrl(documents.permit);
        documentsList.push({ document_type: 'PERMIT', file_url: permitUrl });
      }

      if (documents.fitness) {
        const fitnessUrl = await fileToDataUrl(documents.fitness);
        documentsList.push({ document_type: 'FITNESS', file_url: fitnessUrl });
      }

      // Add photos
      for (const photo of photos) {
        if (photo) {
          const photoUrl = await fileToDataUrl(photo);
          documentsList.push({ document_type: 'VEHICLE_PHOTO', file_url: photoUrl });
        }
      }

      const vehicleData = {
        registration_no: basicInfo.registration_no.trim().toUpperCase(),
        category: basicInfo.category,
        documents: documentsList
      };

      const specData = showSpec ? {
        manufacturer: specInfo.manufacturer.trim(),
        model_name: specInfo.model_name.trim(),
        manufacture_year: Number(specInfo.manufacture_year),
        fuel_type: specInfo.fuel_type,
        seating_capacity: Number(specInfo.seating_capacity)
      } : null;

      await onSubmit(vehicleData, specData, {
        documents,
        photos
      });
    } catch (err) {
      setError(err.message || 'Failed to submit vehicle');
    }
  };

  const currentStepValid = validateStep(step);

  // Determine step labels based on mode
  const getStepLabels = () => {
    if (showSpec) {
      return ['Vehicle', 'Specification', 'Documents', 'Photos'];
    }
    return ['Vehicle', 'Documents', 'Photos'];
  };

  const stepLabels = getStepLabels();

  return (
    <div className="vehicle-add-form">
      <h2>Add New Vehicle</h2>

      {/* Step Indicator */}
      <div className="step-indicator">
        {stepLabels.map((label, index) => {
          const stepNum = index + 1;
          return (
            <div
              key={stepNum}
              className={`step ${step === stepNum ? 'active' : ''} ${step > stepNum ? 'completed' : ''}`}
            >
              <span className="step-number">{stepNum}</span>
              <span className="step-label">{label}</span>
            </div>
          );
        })}
      </div>

      {error && <div className="form-error">{error}</div>}

      <div className="step-content">
        {/* Step 1: Basic Vehicle Details */}
        {step === 1 && (
          <div className="form-section">
            <h3>Vehicle Details</h3>
            <p className="section-info">Provide the registration number and category for this vehicle.</p>

            <div className="form-group">
              <label>Registration Number *</label>
              <input
                type="text"
                name="registration_no"
                value={basicInfo.registration_no}
                onChange={handleBasicInfoChange}
                placeholder="e.g., TS01AB1234"
                maxLength="20"
              />
            </div>

            <div className="form-group">
              <label>Vehicle Category *</label>
              <select
                name="category"
                value={basicInfo.category}
                onChange={handleBasicInfoChange}
              >
                {CATEGORY_OPTIONS.map(option => (
                  <option key={option} value={option}>{option}</option>
                ))}
              </select>
            </div>
          </div>
        )}

        {/* Step 2: Specifications (only if showSpec) */}
        {showSpec && step === 2 && (
          <div className="form-section">
            <h3>Vehicle Specification</h3>
            <p className="section-info">This information is required for compliance and pricing.</p>

            <div className="form-row">
              <div className="form-group">
                <label>Manufacturer *</label>
                <input
                  type="text"
                  name="manufacturer"
                  value={specInfo.manufacturer}
                  onChange={handleSpecChange}
                  placeholder="e.g., Toyota"
                />
              </div>
              <div className="form-group">
                <label>Model Name *</label>
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
                <label>Manufacture Year *</label>
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
                <label>Fuel Type *</label>
                <select
                  name="fuel_type"
                  value={specInfo.fuel_type}
                  onChange={handleSpecChange}
                >
                  {FUEL_OPTIONS.map(option => (
                    <option key={option} value={option}>{option}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="form-group">
              <label>Seating Capacity *</label>
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

        {/* Documents Step */}
        {step === getStepNumber('docs') && (
          <div className="form-section">
            <h3>Required Documents</h3>
            <p className="section-info">Upload clear copies of vehicle documents. Accepted formats: JPG, PNG, PDF (max 5MB each)</p>

            <div className="form-group file-group">
              <label>Registration Certificate (RC) *</label>
              <div className="file-input-wrapper">
                <input
                  type="file"
                  name="rc"
                  onChange={handleDocumentChange}
                  accept=".pdf,.jpg,.jpeg,.png"
                />
                <span className="file-name">
                  {documents.rc ? documents.rc.name : 'Choose file'}
                </span>
              </div>
              {fileErrors.rc && <span className="file-error">{fileErrors.rc}</span>}
            </div>

            <div className="form-group file-group">
              <label>Insurance *</label>
              <div className="file-input-wrapper">
                <input
                  type="file"
                  name="insurance"
                  onChange={handleDocumentChange}
                  accept=".pdf,.jpg,.jpeg,.png"
                />
                <span className="file-name">
                  {documents.insurance ? documents.insurance.name : 'Choose file'}
                </span>
              </div>
              {fileErrors.insurance && <span className="file-error">{fileErrors.insurance}</span>}
            </div>

            <h4>Optional Documents</h4>

            <div className="form-group file-group">
              <label>Permit</label>
              <div className="file-input-wrapper">
                <input
                  type="file"
                  name="permit"
                  onChange={handleDocumentChange}
                  accept=".pdf,.jpg,.jpeg,.png"
                />
                <span className="file-name">
                  {documents.permit ? documents.permit.name : 'Choose file'}
                </span>
              </div>
              {fileErrors.permit && <span className="file-error">{fileErrors.permit}</span>}
            </div>

            <div className="form-group file-group">
              <label>Fitness Certificate</label>
              <div className="file-input-wrapper">
                <input
                  type="file"
                  name="fitness"
                  onChange={handleDocumentChange}
                  accept=".pdf,.jpg,.jpeg,.png"
                />
                <span className="file-name">
                  {documents.fitness ? documents.fitness.name : 'Choose file'}
                </span>
              </div>
              {fileErrors.fitness && <span className="file-error">{fileErrors.fitness}</span>}
            </div>
          </div>
        )}

        {/* Photos Step */}
        {step === getStepNumber('photos') && (
          <div className="form-section">
            <h3>Vehicle Photos</h3>
            <p className="section-info">Add at least one photo of your vehicle. Multiple angles help speed up verification.</p>

            {photos.map((photo, index) => (
              <div className="photo-input-row" key={`photo-${index}`}>
                <div className="form-group file-group">
                  <label>Photo {index + 1} {index === 0 ? '*' : ''}</label>
                  <div className="file-input-wrapper">
                    <input
                      type="file"
                      onChange={(e) => handlePhotoChange(index, e.target.files[0])}
                      accept=".jpg,.jpeg,.png"
                    />
                    <span className="file-name">
                      {photo ? photo.name : 'Choose file'}
                    </span>
                  </div>
                  {fileErrors[`photo_${index}`] && (
                    <span className="file-error">{fileErrors[`photo_${index}`]}</span>
                  )}
                </div>
                {photos.length > 1 && (
                  <button
                    type="button"
                    className="btn-remove-photo"
                    onClick={() => removePhotoField(index)}
                  >
                    Remove
                  </button>
                )}
              </div>
            ))}

            <button
              type="button"
              className="btn-add-photo"
              onClick={addPhotoField}
            >
              + Add another photo
            </button>
          </div>
        )}
      </div>

      {/* Step Actions */}
      <div className="step-actions">
        <button
          type="button"
          className="btn-cancel"
          onClick={onCancel}
          disabled={isSubmitting}
        >
          Cancel
        </button>

        {step > 1 && (
          <button
            type="button"
            className="btn-secondary"
            onClick={handlePrevious}
            disabled={isSubmitting}
          >
            Previous
          </button>
        )}

        {step < (showSpec ? 4 : 3) ? (
          <button
            type="button"
            className="btn-primary"
            onClick={handleNext}
            disabled={!currentStepValid || isSubmitting}
          >
            Next
          </button>
        ) : (
          <button
            type="button"
            className="btn-primary btn-submit"
            onClick={handleSubmit}
            disabled={!currentStepValid || isSubmitting}
          >
            {isSubmitting ? 'Submitting...' : 'Submit Vehicle'}
          </button>
        )}
      </div>
    </div>
  );
}
