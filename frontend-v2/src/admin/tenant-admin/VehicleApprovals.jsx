import { useState, useEffect } from 'react'
import adminService from '../../services/admin.service'
import Icons from '../../components/Icons'
import './VehicleApprovals.css'

const VehicleApprovals = () => {
  const [vehicles, setVehicles] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [expandedVehicle, setExpandedVehicle] = useState(null)
  const [rejectionReasons, setRejectionReasons] = useState({})

  useEffect(() => {
    loadPendingVehicles()
  }, [])

  const loadPendingVehicles = async () => {
    try {
      setLoading(true)
      setError('')
      const data = await adminService.getPendingVehicles()
      setVehicles(data)

      const init = {}
      data.forEach((v) => {
        init[v.vehicle_id] = ''
      })
      setRejectionReasons(init)
    } catch (err) {
      console.error('Failed to load pending vehicles:', err)
      setError(err.message || 'Failed to load vehicles')
    } finally {
      setLoading(false)
    }
  }

  const loadDocuments = async (vehicleId) => {
    try {
      return await adminService.getVehicleDocuments(vehicleId)
    } catch (err) {
      console.error('Failed to load vehicle documents:', err)
      return []
    }
  }

  const handleExpand = async (vehicle) => {
    if (expandedVehicle?.vehicle_id === vehicle.vehicle_id) {
      setExpandedVehicle(null)
    } else {
      const docs = await loadDocuments(vehicle.vehicle_id)
      setExpandedVehicle({ ...vehicle, documents: docs })
    }
  }

  const handleApprove = async (vehicleId) => {
    try {
      await adminService.approveOrRejectVehicle(vehicleId, {
        approval_status: 'APPROVED',
      })
      alert('Vehicle approved successfully')
      loadPendingVehicles()
      setExpandedVehicle(null)
    } catch (err) {
      alert(err.message || 'Failed to approve vehicle')
    }
  }

  const handleReject = async (vehicleId) => {
    const reason = rejectionReasons[vehicleId] || 'No reason provided'
    try {
      await adminService.approveOrRejectVehicle(vehicleId, {
        approval_status: 'REJECTED',
        rejection_reason: reason,
      })
      alert('Vehicle rejected')
      loadPendingVehicles()
      setExpandedVehicle(null)
    } catch (err) {
      alert(err.message || 'Failed to reject vehicle')
    }
  }

  if (loading) {
    return (
      <div className="vehicle-approvals-container">
        <div className="loading-state">
          <p>Loading pending vehicles...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="vehicle-approvals-container">
      <div className="page-header">
        <h1>Vehicle Approvals</h1>
        <span className="count-badge">{vehicles.length} Pending</span>
      </div>

      {error && (
        <div className="error-banner">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
          {error}
        </div>
      )}

      {vehicles.length === 0 ? (
        <div className="empty-state">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <rect x="1" y="3" width="15" height="13"></rect>
            <polygon points="16 8 20 8 23 11 23 16 16 16 16 8"></polygon>
            <circle cx="5.5" cy="18.5" r="2.5"></circle>
            <circle cx="18.5" cy="18.5" r="2.5"></circle>
          </svg>
          <p>No pending vehicle approvals</p>
        </div>
      ) : (
        <div className="vehicles-list">
          {vehicles.map((vehicle) => {
            const isExpanded = expandedVehicle?.vehicle_id === vehicle.vehicle_id

            return (
              <div
                key={vehicle.vehicle_id}
                className={`vehicle-card ${isExpanded ? 'expanded' : ''}`}
              >
                <div className="vehicle-header" onClick={() => handleExpand(vehicle)}>
                  <div className="vehicle-avatar-placeholder">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <rect x="1" y="3" width="15" height="13"></rect>
                      <polygon points="16 8 20 8 23 11 23 16 16 16 16 8"></polygon>
                      <circle cx="5.5" cy="18.5" r="2.5"></circle>
                      <circle cx="18.5" cy="18.5" r="2.5"></circle>
                    </svg>
                  </div>

                  <div className="vehicle-main-info">
                    <h3>{vehicle.registration_number}</h3>
                    <div className="vehicle-meta">
                      <span className="vehicle-type-badge">{vehicle.vehicle_type}</span>
                      <span className="meta-divider">•</span>
                      <span className="meta-item">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                          <line x1="16" y1="2" x2="16" y2="6"></line>
                          <line x1="8" y1="2" x2="8" y2="6"></line>
                          <line x1="3" y1="10" x2="21" y2="10"></line>
                        </svg>
                        {new Date(vehicle.created_on).toLocaleDateString()}
                      </span>
                    </div>
                  </div>

                  <div className={`toggle-icon ${isExpanded ? 'rotated' : ''}`}>
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <polyline points="6 9 12 15 18 9"></polyline>
                    </svg>
                  </div>
                </div>

                {isExpanded && (
                  <div className="vehicle-details-body">
                    <div className="details-grid">
                      <div className="details-column">
                        <h4 className="section-title">
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <circle cx="12" cy="12" r="10"></circle>
                            <line x1="12" y1="16" x2="12" y2="12"></line>
                            <line x1="12" y1="8" x2="12.01" y2="8"></line>
                          </svg>
                          Vehicle Info
                        </h4>
                        <div className="info-list">
                          <div className="info-item">
                            <span className="label">Registration</span>
                            <span className="value">{vehicle.registration_number}</span>
                          </div>
                          <div className="info-item">
                            <span className="label">Type</span>
                            <span className="value">{vehicle.vehicle_type}</span>
                          </div>
                          <div className="info-item">
                            <span className="label">Vehicle ID</span>
                            <span className="value" style={{ fontFamily: 'monospace', fontSize: '12px' }}>
                              {vehicle.vehicle_id}
                            </span>
                          </div>
                        </div>
                      </div>

                      <div className="details-column">
                        <h4 className="section-title">
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                            <polyline points="14 2 14 8 20 8"></polyline>
                          </svg>
                          Documents
                        </h4>
                        <div className="documents-list">
                          {expandedVehicle.documents?.length > 0 ? (
                            expandedVehicle.documents.map((doc) => (
                              <div key={doc.document_id} className="document-item">
                                <div className="doc-icon">
                                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                                    <polyline points="14 2 14 8 20 8"></polyline>
                                  </svg>
                                </div>
                                <div className="doc-info">
                                  <p className="doc-type">{doc.document_type}</p>
                                  <p className="doc-number">{doc.document_number}</p>
                                </div>
                                {doc.file_url && (
                                  <a
                                    href={doc.file_url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="doc-link"
                                  >
                                    View
                                  </a>
                                )}
                              </div>
                            ))
                          ) : (
                            <p className="no-documents">No documents uploaded</p>
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="rejection-section">
                      <label>Rejection Reason (if applicable):</label>
                      <textarea
                        value={rejectionReasons[vehicle.vehicle_id] || ''}
                        onChange={(e) =>
                          setRejectionReasons((prev) => ({
                            ...prev,
                            [vehicle.vehicle_id]: e.target.value,
                          }))
                        }
                        placeholder="Enter reason for rejection"
                      />
                    </div>

                    <div className="actions-row">
                      <button
                        className="btn-reject"
                        onClick={() => handleReject(vehicle.vehicle_id)}
                      >
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="16" height="16">
                          <circle cx="12" cy="12" r="10"></circle>
                          <line x1="15" y1="9" x2="9" y2="15"></line>
                          <line x1="9" y1="9" x2="15" y2="15"></line>
                        </svg>
                        Reject
                      </button>
                      <button
                        className="btn-approve"
                        onClick={() => handleApprove(vehicle.vehicle_id)}
                      >
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="16" height="16">
                          <polyline points="20 6 9 17 4 12"></polyline>
                        </svg>
                        Approve
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

export default VehicleApprovals
