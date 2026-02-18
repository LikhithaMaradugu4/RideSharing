/**
 * FleetApplicationStatus.jsx
 * 
 * Fleet Application Status Page with Document Management
 * 
 * Features:
 * - Show fleet application status
 * - Display all documents with their verification status
 * - Allow re-upload of rejected documents
 * - Manual resubmit button when all rejected docs are fixed
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import fleetService from '../../services/fleet.service';
import authService from '../../services/auth.service';
import Icons from '../../components/Icons';
import './FleetApplicationStatus.css';

const FleetApplicationStatus = () => {
  const navigate = useNavigate();
  
  // State
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [application, setApplication] = useState(null);
  const [uploadingDocType, setUploadingDocType] = useState(null);
  const [resubmitting, setResubmitting] = useState(false);

  // Load application data
  const loadApplication = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const token = await authService.getValidToken();
      if (!token) {
        navigate('/login');
        return;
      }

      const data = await fleetService.getMyApplication(token);
      setApplication(data);
      
    } catch (err) {
      console.error('Error loading fleet application:', err);
      if (err.status === 404) {
        setError('No fleet application found. Please apply first.');
      } else {
        setError(err.message || 'Failed to load application data');
      }
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  useEffect(() => {
    loadApplication();
  }, [loadApplication]);

  // Handle document reupload
  const handleReupload = async (documentType, file) => {
    if (!file) return;
    
    try {
      setUploadingDocType(documentType);
      setError(null);
      setSuccessMessage(null);
      
      const token = await authService.getValidToken();
      await fleetService.reuploadDocument(token, documentType, file);
      
      setSuccessMessage(`${documentType.replace(/_/g, ' ')} uploaded successfully`);
      await loadApplication();
      
    } catch (err) {
      console.error('Error uploading document:', err);
      setError(err.message || 'Failed to upload document');
    } finally {
      setUploadingDocType(null);
    }
  };

  // Handle application resubmit
  const handleResubmit = async () => {
    try {
      setResubmitting(true);
      setError(null);
      setSuccessMessage(null);
      
      const token = await authService.getValidToken();
      await fleetService.resubmitApplication(token);
      
      navigate('/app/home');
      
    } catch (err) {
      console.error('Error resubmitting application:', err);
      setError(err.message || 'Failed to resubmit application');
    } finally {
      setResubmitting(false);
    }
  };

  // Get status badge class
  const getStatusClass = (status) => {
    switch (status) {
      case 'APPROVED': return 'status-approved';
      case 'REJECTED': return 'status-rejected';
      case 'PARTIALLY_REJECTED': return 'status-partial';
      case 'PENDING': return 'status-pending';
      default: return 'status-pending';
    }
  };

  // Format document type for display
  const formatDocType = (type) => {
    return type.replace(/_/g, ' ').toLowerCase().replace(/\b\w/g, l => l.toUpperCase());
  };

  if (loading) {
    return (
      <div className="fleet-application-status-page">
        <div className="loading">Loading fleet application data...</div>
      </div>
    );
  }

  if (!application) {
    return (
      <div className="fleet-application-status-page">
        <div className="no-application">
          <h2>No Fleet Application Found</h2>
          <p>You haven't submitted a fleet owner application yet.</p>
          <button onClick={() => navigate('/fleet-owner-tenant-selection')} className="btn-primary">
            Apply Now
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="fleet-application-status-page">
      <h1>Fleet Application Status</h1>

      {/* Messages */}
      {error && <div className="alert alert-error">{error}</div>}
      {successMessage && <div className="alert alert-success">{successMessage}</div>}

      {/* Application Overview */}
      <div className="application-overview">
        <div className="overview-header">
          <h2>Fleet Application</h2>
          <span className={`status-badge ${getStatusClass(application.approval_status)}`}>
            {application.approval_status}
          </span>
        </div>
        
        <div className="overview-details">
          <div className="detail-item">
            <label>Fleet ID:</label>
            <span>{application.fleet_id}</span>
          </div>
          <div className="detail-item">
            <label>Fleet Name:</label>
            <span>{application.fleet_name}</span>
          </div>
          <div className="detail-item">
            <label>Tenant ID:</label>
            <span>{application.tenant_id}</span>
          </div>
        </div>

        {/* Status Message */}
        {application.approval_status === 'PARTIALLY_REJECTED' && (
          <div className="status-message warning">
            <strong><Icons.Warning size={16} style={{verticalAlign: 'middle', marginRight: '4px'}} /> Some documents were rejected.</strong> Please re-upload the rejected documents below and resubmit your application.
          </div>
        )}
        
        {application.approval_status === 'REJECTED' && (
          <div className="status-message error">
            <strong><Icons.XCircle size={16} style={{verticalAlign: 'middle', marginRight: '4px'}} /> Application Rejected.</strong> Please review the rejected documents and contact support if needed.
          </div>
        )}
        
        {application.approval_status === 'PENDING' && (
          <div className="status-message info">
            <strong><Icons.Hourglass size={16} style={{verticalAlign: 'middle', marginRight: '4px'}} /> Under Review.</strong> Your fleet application is being reviewed by the admin.
          </div>
        )}
        
        {application.approval_status === 'APPROVED' && (
          <div className="status-message success">
            <strong><Icons.CheckCircle size={16} style={{verticalAlign: 'middle', marginRight: '4px'}} /> Approved!</strong> Your fleet is ready. You can manage operations from the fleet dashboard.
          </div>
        )}
      </div>

      {/* Documents Section */}
      <div className="documents-section">
        <h3>Documents</h3>
        
        <div className="documents-list">
          {application.documents.map((doc) => (
            <div key={doc.document_id} className={`document-card ${getStatusClass(doc.verification_status)}`}>
              <div className="document-header">
                <span className="doc-type">{formatDocType(doc.document_type)}</span>
                <span className={`doc-status ${getStatusClass(doc.verification_status)}`}>
                  {doc.verification_status}
                </span>
              </div>
              
              <div className="document-body">
                {doc.file_url && (
                  <a 
                    href={`/${doc.file_url}`} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="view-link"
                  >
                    <Icons.Document size={14} style={{verticalAlign: 'middle', marginRight: '4px'}} /> View Document
                  </a>
                )}
                
                {doc.rejection_reason && (
                  <div className="rejection-reason">
                    <strong>Reason:</strong> {doc.rejection_reason}
                  </div>
                )}
                
                {doc.can_reupload && (
                  <div className="reupload-section">
                    <label className="reupload-label">
                      <input
                        type="file"
                        accept="image/*,.pdf"
                        onChange={(e) => handleReupload(doc.document_type, e.target.files[0])}
                        disabled={uploadingDocType === doc.document_type}
                      />
                      <span className="btn-reupload">
                        {uploadingDocType === doc.document_type ? 'Uploading...' : <><Icons.Upload size={14} style={{verticalAlign: 'middle', marginRight: '4px'}} /> Re-upload</>}
                      </span>
                    </label>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Resubmit Button */}
      {application.can_resubmit && (
        <div className="resubmit-section">
          <button
            className="btn-resubmit"
            onClick={handleResubmit}
            disabled={resubmitting}
          >
            {resubmitting ? 'Resubmitting...' : <><Icons.Rocket size={16} style={{verticalAlign: 'middle', marginRight: '4px'}} /> Resubmit Application</>}
          </button>
          <p className="resubmit-hint">
            All rejected documents have been fixed. Click to resubmit for review.
          </p>
        </div>
      )}

      {/* Back Button */}
      <div className="actions">
        <button onClick={() => navigate('/app/home')} className="btn-secondary">
          ← Back to Home
        </button>
      </div>
    </div>
  );
};

export default FleetApplicationStatus;
