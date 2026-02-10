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
    return <div className="loading">Loading pending vehicles...</div>
  }

  return (
    <div className="vehicle-approvals">
      <h1>Vehicle Approvals</h1>

      {error && <div className="error">{error}</div>}

      {vehicles.length === 0 ? (
        <p className="no-data">No pending vehicles</p>
      ) : (
        <div className="vehicles-list">
          {vehicles.map((vehicle) => (
            <div
              key={vehicle.vehicle_id}
              className={`vehicle-card ${
                expandedVehicle?.vehicle_id === vehicle.vehicle_id ? 'expanded' : ''
              }`}
            >
              <div
                className="vehicle-header"
                onClick={() => handleExpand(vehicle)}
              >
                <div className="vehicle-info">
                  <h3>{vehicle.registration_number}</h3>
                  <p>Type: {vehicle.vehicle_type}</p>
                  <p>Applied: {new Date(vehicle.created_on).toLocaleDateString()}</p>
                </div>
                <div className="toggle-icon">
                  {expandedVehicle?.vehicle_id === vehicle.vehicle_id ? <Icons.ChevronDown size={16} /> : <Icons.ChevronRight size={16} />}
                </div>
              </div>

              {expandedVehicle?.vehicle_id === vehicle.vehicle_id && (
                <div className="vehicle-details">
                  <div className="documents-section">
                    <h4>Documents</h4>
                    {expandedVehicle.documents?.length > 0 ? (
                      <ul>
                        {expandedVehicle.documents.map((doc) => (
                          <li key={doc.document_id}>
                            <strong>{doc.document_type}:</strong>{' '}
                            {doc.document_number}
                            {doc.file_url && (
                              <a
                                href={doc.file_url}
                                target="_blank"
                                rel="noopener noreferrer"
                              >
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

                  <div className="reason-section">
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

                  <div className="actions">
                    <button
                      className="btn-approve"
                      onClick={() => handleApprove(vehicle.vehicle_id)}
                    >
                      Approve
                    </button>
                    <button
                      className="btn-reject"
                      onClick={() => handleReject(vehicle.vehicle_id)}
                    >
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

export default VehicleApprovals
