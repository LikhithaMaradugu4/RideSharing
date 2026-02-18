import { useState, useEffect } from 'react';
import adminService from '../../services/admin.service';
import './DriverApprovals.css';

const DriverApprovals = () => {
  const [drivers, setDrivers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [expandedDriver, setExpandedDriver] = useState(null);
  const [approvalData, setApprovalData] = useState({});
  
  // Document review state
  const [reviewingDoc, setReviewingDoc] = useState(null);
  const [rejectReason, setRejectReason] = useState('');
  const [reviewLoading, setReviewLoading] = useState(false);

  useEffect(() => {
    loadPendingDrivers();
  }, []);

  const loadPendingDrivers = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await adminService.getPendingDrivers();
      setDrivers(data);
      // Initialize approval data
      const init = {};
      data.forEach((d) => {
        init[d.driver_id] = { categories: [], reason: '' };
      });
      setApprovalData(init);
    } catch (err) {
      console.error('Failed to load pending drivers:', err);
      setError(err.message || 'Failed to load drivers');
    } finally {
      setLoading(false);
    }
  };

  const loadDocuments = async (driverId) => {
    try {
      // Use detailed endpoint for document review capability
      const docs = await adminService.getDriverDocumentsDetailed(driverId);
      return docs;
    } catch (err) {
      console.error('Failed to load documents:', err);
      // Fallback to basic endpoint
      try {
        const basicDocs = await adminService.getDriverDocuments(driverId);
        return basicDocs;
      } catch {
        return [];
      }
    }
  };

  // Handle document review (approve/reject)
  const handleDocumentReview = async (driverId, documentId, status) => {
    if (status === 'REJECTED' && !rejectReason.trim()) {
      alert('Please provide a rejection reason');
      return;
    }

    try {
      setReviewLoading(true);
      await adminService.reviewDriverDocument(driverId, documentId, {
        status,
        rejection_reason: status === 'REJECTED' ? rejectReason : undefined
      });
      
      // Refresh documents
      const docs = await loadDocuments(driverId);
      setExpandedDriver(prev => ({ ...prev, documents: docs }));
      
      // Refresh drivers list (status might have changed)
      loadPendingDrivers();
      
      // Reset modal
      setReviewingDoc(null);
      setRejectReason('');
      
      alert(`Document ${status.toLowerCase()} successfully`);
    } catch (err) {
      alert(err.message || 'Failed to review document');
    } finally {
      setReviewLoading(false);
    }
  };

  const handleExpand = async (driver) => {
    if (expandedDriver?.driver_id === driver.driver_id) {
      setExpandedDriver(null);
    } else {
      const docs = await loadDocuments(driver.driver_id);
      setExpandedDriver({ ...driver, documents: docs });
    }
  };

  const handleCategoryToggle = (driverId, category) => {
    setApprovalData((prev) => ({
      ...prev,
      [driverId]: {
        ...prev[driverId],
        categories: prev[driverId].categories.includes(category)
          ? prev[driverId].categories.filter((c) => c !== category)
          : [...prev[driverId].categories, category],
      },
    }));
  };

  const handleApprove = async (driverId) => {
    if (approvalData[driverId].categories.length === 0) {
      alert('Please select at least one vehicle category');
      return;
    }

    try {
      await adminService.approveDriver(driverId, {
        allowed_vehicle_categories: approvalData[driverId].categories,
      });
      alert('Driver approved successfully');
      loadPendingDrivers();
      setExpandedDriver(null);
    } catch (err) {
      alert(err.message || 'Failed to approve driver');
    }
  };

  const handleReject = async (driverId) => {
    const reason = approvalData[driverId].reason || 'No reason provided';
    try {
      await adminService.rejectDriver(driverId, { reason });
      alert('Driver rejected');
      loadPendingDrivers();
      setExpandedDriver(null);
    } catch (err) {
      alert(err.message || 'Failed to reject driver');
    }
  };

  if (loading) {
    return (
      <div className="loading-state">
        <p>Loading pending drivers...</p>
      </div>
    );
  }

  const vehicleCategories = ['BIKE', 'AUTO', 'CAR', 'SEDAN'];

  return (
    <div className="driver-approvals-container">
      <div className="page-header">
        <h1>Driver Approvals</h1>
        <div className="count-badge">{drivers.length} Pending</div>
      </div>

      {error && (
        <div className="error-banner">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
          {error}
        </div>
      )}

      {drivers.length === 0 ? (
        <div className="empty-state">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1"><circle cx="12" cy="12" r="10"></circle><path d="M16 16s-1.5-2-4-2-4 2-4 2"></path><line x1="9" y1="9" x2="9.01" y2="9"></line><line x1="15" y1="9" x2="15.01" y2="9"></line></svg>
          <p>No pending drivers to review</p>
        </div>
      ) : (
        <div className="drivers-list">
          {drivers.map((driver) => {
            const isExpanded = expandedDriver?.driver_id === driver.driver_id;
            
            return (
              <div
                key={driver.driver_id}
                className={`driver-card ${isExpanded ? 'expanded' : ''}`}
              >
                <div className="driver-header" onClick={() => handleExpand(driver)}>
                  <div className="driver-avatar-placeholder">
                    {driver.full_name.charAt(0).toUpperCase()}
                  </div>
                  
                  <div className="driver-main-info">
                    <h3>{driver.full_name}</h3>
                    <div className="driver-meta">
                      <span className="meta-item">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
                        {driver.phone}
                      </span>
                      <span className="meta-divider">•</span>
                      <span className="meta-item">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
                        Applied: {new Date(driver.application_date).toLocaleDateString()}
                      </span>
                    </div>
                  </div>

                  <div className={`toggle-icon ${isExpanded ? 'rotated' : ''}`}>
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
                  </div>
                </div>

                {isExpanded && (
                  <div className="driver-details-body">
                    <div className="details-grid">
                      {/* Left Column: Documents */}
                      <div className="details-column">
                        <h4 className="section-title">
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                          Documents
                        </h4>
                        
                        {expandedDriver.documents && expandedDriver.documents.length > 0 ? (
                          <div className="documents-list">
                            {expandedDriver.documents.map((doc) => (
                              <div key={doc.document_id} className={`document-item doc-status-${(doc.verification_status || 'pending').toLowerCase()}`}>
                                <div className="doc-icon">
                                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path><polyline points="13 2 13 9 20 9"></polyline></svg>
                                </div>
                                <div className="doc-info">
                                  <span className="doc-type">{doc.document_type}</span>
                                  <span className={`doc-verification-status status-${(doc.verification_status || 'pending').toLowerCase()}`}>
                                    {doc.verification_status || 'PENDING'}
                                  </span>
                                  {doc.rejection_reason && (
                                    <span className="doc-rejection-reason">Reason: {doc.rejection_reason}</span>
                                  )}
                                </div>
                                <div className="doc-actions">
                                  {doc.file_url && (
                                    <a href={doc.file_url.startsWith('http') ? doc.file_url : `/${doc.file_url}`} target="_blank" rel="noopener noreferrer" className="doc-link" title="View Document">
                                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
                                    </a>
                                  )}
                                  {(doc.can_review !== false && doc.verification_status !== 'APPROVED') && (
                                    <>
                                      <button 
                                        className="doc-btn doc-btn-approve"
                                        onClick={() => handleDocumentReview(driver.driver_id, doc.document_id, 'APPROVED')}
                                        disabled={reviewLoading}
                                        title="Approve Document"
                                      >
                                        ✓
                                      </button>
                                      <button 
                                        className="doc-btn doc-btn-reject"
                                        onClick={() => setReviewingDoc({ driverId: driver.driver_id, doc })}
                                        disabled={reviewLoading}
                                        title="Reject Document"
                                      >
                                        ✕
                                      </button>
                                    </>
                                  )}
                                </div>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <div className="no-docs-msg">No documents uploaded</div>
                        )}
                      </div>

                      {/* Right Column: Actions */}
                      <div className="details-column">
                        <h4 className="section-title">
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="8.5" cy="7" r="4"></circle><polyline points="17 11 19 13 23 9"></polyline></svg>
                          Approval Actions
                        </h4>

                        <div className="action-group">
                          <label className="input-label">Allowed Vehicle Categories</label>
                          <div className="categories-grid">
                            {vehicleCategories.map((category) => {
                              const isSelected = approvalData[driver.driver_id]?.categories.includes(category);
                              return (
                                <div 
                                  key={category} 
                                  className={`category-tile ${isSelected ? 'selected' : ''}`}
                                  onClick={() => handleCategoryToggle(driver.driver_id, category)}
                                >
                                  <div className={`checkbox-custom ${isSelected ? 'checked' : ''}`}>
                                    {isSelected && <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="4"><polyline points="20 6 9 17 4 12"></polyline></svg>}
                                  </div>
                                  {category}
                                </div>
                              );
                            })}
                          </div>
                        </div>

                        <div className="action-group">
                          <label className="input-label">Rejection Reason <span className="optional">(Only required for rejection)</span></label>
                          <textarea
                            className="reason-textarea"
                            value={approvalData[driver.driver_id]?.reason || ''}
                            onChange={(e) =>
                              setApprovalData((prev) => ({
                                ...prev,
                                [driver.driver_id]: {
                                  ...prev[driver.driver_id],
                                  reason: e.target.value,
                                },
                              }))
                            }
                            placeholder="Enter reason for rejection..."
                          />
                        </div>

                        <div className="action-buttons">
                          <button
                            className="btn-reject"
                            onClick={() => handleReject(driver.driver_id)}
                          >
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                            Reject
                          </button>
                          <button
                            className="btn-approve"
                            onClick={() => handleApprove(driver.driver_id)}
                          >
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="20 6 9 17 4 12"></polyline></svg>
                            Approve Driver
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Document Rejection Modal */}
      {reviewingDoc && (
        <div className="modal-overlay" onClick={() => setReviewingDoc(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>Reject Document</h3>
            <p className="modal-subtitle">
              Document: <strong>{reviewingDoc.doc.document_type}</strong>
            </p>
            <div className="modal-form">
              <label>Rejection Reason *</label>
              <textarea
                value={rejectReason}
                onChange={(e) => setRejectReason(e.target.value)}
                placeholder="Please provide a clear reason for rejection..."
                rows={4}
              />
            </div>
            <div className="modal-actions">
              <button 
                className="btn-cancel" 
                onClick={() => {
                  setReviewingDoc(null);
                  setRejectReason('');
                }}
              >
                Cancel
              </button>
              <button 
                className="btn-reject"
                onClick={() => handleDocumentReview(reviewingDoc.driverId, reviewingDoc.doc.document_id, 'REJECTED')}
                disabled={reviewLoading || !rejectReason.trim()}
              >
                {reviewLoading ? 'Rejecting...' : 'Reject Document'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DriverApprovals;