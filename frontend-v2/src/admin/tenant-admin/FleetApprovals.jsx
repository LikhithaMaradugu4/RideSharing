import { useState, useEffect } from 'react';
import adminService from '../../services/admin.service';
import './FleetApprovals.css';

const FleetApprovals = () => {
  const [fleets, setFleets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [expandedFleet, setExpandedFleet] = useState(null);

  // Document review state
  const [reviewingDoc, setReviewingDoc] = useState(null);
  const [rejectReason, setRejectReason] = useState('');
  const [reviewLoading, setReviewLoading] = useState(false);

  useEffect(() => {
    loadPendingFleets();
  }, []);

  const loadPendingFleets = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await adminService.getPendingFleets();
      setFleets(data);
    } catch (err) {
      console.error('Failed to load pending fleets:', err);
      setError(err.message || 'Failed to load fleets');
    } finally {
      setLoading(false);
    }
  };

  const loadDocuments = async (fleetId) => {
    try {
      const docs = await adminService.getFleetDocumentsDetailed(fleetId);
      return docs;
    } catch (err) {
      console.error('Failed to load fleet documents:', err);
      // Fallback to fleet's embedded documents
      const fleet = fleets.find(f => f.fleet_id === fleetId);
      return fleet?.documents || [];
    }
  };

  const handleDocumentReview = async (fleetId, documentId, status) => {
    if (status === 'REJECTED' && !rejectReason.trim()) {
      alert('Please provide a rejection reason');
      return;
    }

    try {
      setReviewLoading(true);
      await adminService.reviewFleetDocument(fleetId, documentId, {
        status,
        rejection_reason: status === 'REJECTED' ? rejectReason : undefined
      });

      // Refresh documents
      const docs = await loadDocuments(fleetId);
      setExpandedFleet(prev => ({ ...prev, documents: docs }));

      // Refresh fleets list (status might have changed)
      loadPendingFleets();

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

  const handleExpand = async (fleet) => {
    if (expandedFleet?.fleet_id === fleet.fleet_id) {
      setExpandedFleet(null);
    } else {
      const docs = await loadDocuments(fleet.fleet_id);
      setExpandedFleet({ ...fleet, documents: docs });
    }
  };

  const handleApprove = async (fleetId) => {
    try {
      await adminService.approveFleet(fleetId);
      alert('Fleet approved successfully');
      loadPendingFleets();
      setExpandedFleet(null);
    } catch (err) {
      alert(err.message || 'Failed to approve fleet');
    }
  };

  const handleReject = async (fleetId) => {
    const reason = prompt('Enter reason for rejection:');
    if (!reason) return;

    try {
      await adminService.rejectFleet(fleetId, { reason });
      alert('Fleet rejected');
      loadPendingFleets();
      setExpandedFleet(null);
    } catch (err) {
      alert(err.message || 'Failed to reject fleet');
    }
  };

  if (loading) {
    return (
      <div className="fa-loading-state">
        <p>Loading pending fleets...</p>
      </div>
    );
  }

  return (
    <div className="fleet-approvals-container">
      <div className="fa-page-header">
        <h1>Fleet Approvals</h1>
        <div className="fa-count-badge">{fleets.length} Pending</div>
      </div>

      {error && (
        <div className="fa-error-banner">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
          {error}
        </div>
      )}

      {fleets.length === 0 ? (
        <div className="fa-empty-state">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1"><circle cx="12" cy="12" r="10"></circle><path d="M16 16s-1.5-2-4-2-4 2-4 2"></path><line x1="9" y1="9" x2="9.01" y2="9"></line><line x1="15" y1="9" x2="15.01" y2="9"></line></svg>
          <p>No pending fleets to review</p>
        </div>
      ) : (
        <div className="fa-fleets-list">
          {fleets.map((fleet) => {
            const isExpanded = expandedFleet?.fleet_id === fleet.fleet_id;

            return (
              <div
                key={fleet.fleet_id}
                className={`fa-fleet-card ${isExpanded ? 'expanded' : ''}`}
              >
                <div className="fa-fleet-header" onClick={() => handleExpand(fleet)}>
                  <div className="fa-fleet-avatar">
                    {fleet.fleet_name.charAt(0).toUpperCase()}
                  </div>

                  <div className="fa-fleet-main-info">
                    <h3>{fleet.fleet_name}</h3>
                    <div className="fa-fleet-meta">
                      <span className="fa-meta-item">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path></svg>
                        {fleet.fleet_type}
                      </span>
                      <span className="fa-meta-divider">•</span>
                      <span className={`fa-status-badge fa-status-${(fleet.status || 'pending').toLowerCase()}`}>
                        {fleet.status}
                      </span>
                    </div>
                  </div>

                  <div className={`fa-toggle-icon ${isExpanded ? 'rotated' : ''}`}>
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
                  </div>
                </div>

                {isExpanded && (
                  <div className="fa-details-body">
                    {/* Documents Section */}
                    <div className="fa-section">
                      <h4 className="fa-section-title">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                        Fleet Documents
                      </h4>

                      {expandedFleet.documents && expandedFleet.documents.length > 0 ? (
                        <div className="fa-documents-list">
                          {expandedFleet.documents.map((doc) => (
                            <div key={doc.document_id} className={`fa-document-item fa-doc-status-${(doc.verification_status || 'pending').toLowerCase()}`}>
                              <div className="fa-doc-icon">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path><polyline points="13 2 13 9 20 9"></polyline></svg>
                              </div>
                              <div className="fa-doc-info">
                                <span className="fa-doc-type">{doc.document_type}</span>
                                <span className={`fa-doc-verification-status fa-vstatus-${(doc.verification_status || 'pending').toLowerCase()}`}>
                                  {doc.verification_status || 'PENDING'}
                                </span>
                                {doc.rejection_reason && (
                                  <span className="fa-doc-rejection-reason">Reason: {doc.rejection_reason}</span>
                                )}
                              </div>
                              <div className="fa-doc-actions">
                                {doc.file_url && (
                                  <a href={doc.file_url.startsWith('http') ? doc.file_url : `/${doc.file_url}`} target="_blank" rel="noopener noreferrer" className="fa-doc-link" title="View Document">
                                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
                                  </a>
                                )}
                                {(doc.can_review !== false && doc.verification_status !== 'APPROVED') && (
                                  <>
                                    <button
                                      className="fa-doc-btn fa-doc-btn-approve"
                                      onClick={() => handleDocumentReview(fleet.fleet_id, doc.document_id, 'APPROVED')}
                                      disabled={reviewLoading}
                                      title="Approve Document"
                                    >
                                      ✓
                                    </button>
                                    <button
                                      className="fa-doc-btn fa-doc-btn-reject"
                                      onClick={() => setReviewingDoc({ fleetId: fleet.fleet_id, doc })}
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
                        <div className="fa-no-docs">No documents uploaded</div>
                      )}
                    </div>

                    {/* Bulk Actions */}
                    <div className="fa-section">
                      <h4 className="fa-section-title">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="8.5" cy="7" r="4"></circle><polyline points="17 11 19 13 23 9"></polyline></svg>
                        Approval Actions
                      </h4>

                      <div className="fa-action-buttons">
                        <button
                          className="fa-btn-reject"
                          onClick={() => handleReject(fleet.fleet_id)}
                        >
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                          Reject Fleet
                        </button>
                        <button
                          className="fa-btn-approve"
                          onClick={() => handleApprove(fleet.fleet_id)}
                        >
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="20 6 9 17 4 12"></polyline></svg>
                          Approve Fleet
                        </button>
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
        <div className="fa-modal-overlay" onClick={() => setReviewingDoc(null)}>
          <div className="fa-modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>Reject Document</h3>
            <p className="fa-modal-subtitle">
              Document: <strong>{reviewingDoc.doc.document_type}</strong>
            </p>
            <div className="fa-modal-form">
              <label>Rejection Reason *</label>
              <textarea
                value={rejectReason}
                onChange={(e) => setRejectReason(e.target.value)}
                placeholder="Please provide a clear reason for rejection..."
                rows={4}
              />
            </div>
            <div className="fa-modal-actions">
              <button
                className="fa-btn-cancel"
                onClick={() => {
                  setReviewingDoc(null);
                  setRejectReason('');
                }}
              >
                Cancel
              </button>
              <button
                className="fa-btn-reject"
                onClick={() => handleDocumentReview(reviewingDoc.fleetId, reviewingDoc.doc.document_id, 'REJECTED')}
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

export default FleetApprovals;
