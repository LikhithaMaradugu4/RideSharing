import { useState, useEffect } from 'react'
import adminService from '../../services/admin.service'
import './FleetApprovals.css'

const FleetApprovals = () => {
  const [fleets, setFleets] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [expandedFleet, setExpandedFleet] = useState(null)

  useEffect(() => {
    loadPendingFleets()
  }, [])

  const loadPendingFleets = async () => {
    try {
      setLoading(true)
      setError('')
      const data = await adminService.getPendingFleets()
      setFleets(data)
    } catch (err) {
      console.error('Failed to load pending fleets:', err)
      setError(err.message || 'Failed to load fleets')
    } finally {
      setLoading(false)
    }
  }

  const handleExpand = (fleet) => {
    if (expandedFleet?.fleet_id === fleet.fleet_id) {
      setExpandedFleet(null)
    } else {
      setExpandedFleet(fleet)
    }
  }

  const handleApprove = async (fleetId) => {
    try {
      await adminService.approveFleet(fleetId)
      alert('Fleet approved successfully')
      loadPendingFleets()
      setExpandedFleet(null)
    } catch (err) {
      alert(err.message || 'Failed to approve fleet')
    }
  }

  const handleReject = async (fleetId) => {
    const reason = prompt('Enter reason for rejection:')
    if (!reason) return

    try {
      await adminService.rejectFleet(fleetId, { reason })
      alert('Fleet rejected')
      loadPendingFleets()
      setExpandedFleet(null)
    } catch (err) {
      alert(err.message || 'Failed to reject fleet')
    }
  }

  if (loading) {
    return <div className="loading">Loading pending fleets...</div>
  }

  return (
    <div className="fleet-approvals">
      <h1>Fleet Approvals</h1>

      {error && <div className="error">{error}</div>}

      {fleets.length === 0 ? (
        <p className="no-data">No pending fleets</p>
      ) : (
        <div className="fleets-list">
          {fleets.map((fleet) => (
            <div
              key={fleet.fleet_id}
              className={`fleet-card ${
                expandedFleet?.fleet_id === fleet.fleet_id ? 'expanded' : ''
              }`}
            >
              <div className="fleet-header" onClick={() => handleExpand(fleet)}>
                <div className="fleet-info">
                  <h3>{fleet.fleet_name}</h3>
                  <p>Type: {fleet.fleet_type}</p>
                  <p>Status: {fleet.status}</p>
                </div>
                <div className="toggle-icon">
                  {expandedFleet?.fleet_id === fleet.fleet_id ? '▼' : '▶'}
                </div>
              </div>

              {expandedFleet?.fleet_id === fleet.fleet_id && (
                <div className="fleet-details">
                  <div className="documents-section">
                    <h4>Fleet Documents</h4>
                    {fleet.documents && fleet.documents.length > 0 ? (
                      <ul>
                        {fleet.documents.map((doc) => (
                          <li key={doc.document_id}>
                            <strong>{doc.document_type}</strong>
                            <span className="status">{doc.verification_status}</span>
                            {doc.file_url && (
                              <a href={doc.file_url} target="_blank" rel="noopener noreferrer">
                                View
                              </a>
                            )}
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p>No documents uploaded</p>
                    )}
                  </div>

                  <div className="actions">
                    <button className="btn-approve" onClick={() => handleApprove(fleet.fleet_id)}>
                      Approve
                    </button>
                    <button className="btn-reject" onClick={() => handleReject(fleet.fleet_id)}>
                      Reject
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default FleetApprovals
