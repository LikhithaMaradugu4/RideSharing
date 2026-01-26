import { useState, useEffect } from 'react'
import adminService from '../../services/admin.service'
import './DriverApprovals.css'

const DriverApprovals = () => {
  const [drivers, setDrivers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [expandedDriver, setExpandedDriver] = useState(null)
  const [approvalData, setApprovalData] = useState({})

  useEffect(() => {
    loadPendingDrivers()
  }, [])

  const loadPendingDrivers = async () => {
    try {
      setLoading(true)
      setError('')
      const data = await adminService.getPendingDrivers()
      setDrivers(data)
      // Initialize approval data
      const init = {}
      data.forEach((d) => {
        init[d.driver_id] = { categories: [], reason: '' }
      })
      setApprovalData(init)
    } catch (err) {
      console.error('Failed to load pending drivers:', err)
      setError(err.message || 'Failed to load drivers')
    } finally {
      setLoading(false)
    }
  }

  const loadDocuments = async (driverId) => {
    try {
      const docs = await adminService.getDriverDocuments(driverId)
      return docs
    } catch (err) {
      console.error('Failed to load documents:', err)
      return []
    }
  }

  const handleExpand = async (driver) => {
    if (expandedDriver?.driver_id === driver.driver_id) {
      setExpandedDriver(null)
    } else {
      const docs = await loadDocuments(driver.driver_id)
      setExpandedDriver({ ...driver, documents: docs })
    }
  }

  const handleCategoryToggle = (driverId, category) => {
    setApprovalData((prev) => ({
      ...prev,
      [driverId]: {
        ...prev[driverId],
        categories: prev[driverId].categories.includes(category)
          ? prev[driverId].categories.filter((c) => c !== category)
          : [...prev[driverId].categories, category],
      },
    }))
  }

  const handleApprove = async (driverId) => {
    if (approvalData[driverId].categories.length === 0) {
      alert('Please select at least one vehicle category')
      return
    }

    try {
      await adminService.approveDriver(driverId, {
        allowed_vehicle_categories: approvalData[driverId].categories,
      })
      alert('Driver approved successfully')
      loadPendingDrivers()
      setExpandedDriver(null)
    } catch (err) {
      alert(err.message || 'Failed to approve driver')
    }
  }

  const handleReject = async (driverId) => {
    const reason = approvalData[driverId].reason || 'No reason provided'
    try {
      await adminService.rejectDriver(driverId, { reason })
      alert('Driver rejected')
      loadPendingDrivers()
      setExpandedDriver(null)
    } catch (err) {
      alert(err.message || 'Failed to reject driver')
    }
  }

  if (loading) {
    return <div className="loading">Loading pending drivers...</div>
  }

  const vehicleCategories = ['BIKE', 'AUTO', 'CAR', 'SEDAN']

  return (
    <div className="driver-approvals">
      <h1>Driver Approvals</h1>

      {error && <div className="error">{error}</div>}

      {drivers.length === 0 ? (
        <p className="no-data">No pending drivers</p>
      ) : (
        <div className="drivers-list">
          {drivers.map((driver) => (
            <div
              key={driver.driver_id}
              className={`driver-card ${
                expandedDriver?.driver_id === driver.driver_id ? 'expanded' : ''
              }`}
            >
              <div className="driver-header" onClick={() => handleExpand(driver)}>
                <div className="driver-info">
                  <h3>{driver.full_name}</h3>
                  <p>Phone: {driver.phone}</p>
                  <p>Applied: {new Date(driver.application_date).toLocaleDateString()}</p>
                </div>
                <div className="toggle-icon">
                  {expandedDriver?.driver_id === driver.driver_id ? '▼' : '▶'}
                </div>
              </div>

              {expandedDriver?.driver_id === driver.driver_id && (
                <div className="driver-details">
                  <div className="documents-section">
                    <h4>Documents</h4>
                    {expandedDriver.documents && expandedDriver.documents.length > 0 ? (
                      <ul>
                        {expandedDriver.documents.map((doc) => (
                          <li key={doc.document_id}>
                            <strong>{doc.document_type}:</strong> {doc.document_number}
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

                  <div className="categories-section">
                    <h4>Allowed Vehicle Categories</h4>
                    <div className="categories-grid">
                      {vehicleCategories.map((category) => (
                        <label key={category} className="category-checkbox">
                          <input
                            type="checkbox"
                            checked={approvalData[driver.driver_id]?.categories.includes(
                              category
                            ) || false}
                            onChange={() => handleCategoryToggle(driver.driver_id, category)}
                          />
                          {category}
                        </label>
                      ))}
                    </div>
                  </div>

                  <div className="reason-section">
                    <label>Rejection Reason (if applicable):</label>
                    <textarea
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
                      placeholder="Enter reason for rejection"
                    />
                  </div>

                  <div className="actions">
                    <button
                      className="btn-approve"
                      onClick={() => handleApprove(driver.driver_id)}
                    >
                      Approve
                    </button>
                    <button
                      className="btn-reject"
                      onClick={() => handleReject(driver.driver_id)}
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

export default DriverApprovals
