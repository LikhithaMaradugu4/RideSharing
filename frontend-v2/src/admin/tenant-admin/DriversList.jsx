import { useState, useEffect } from 'react'
import adminService from '../../services/admin.service'
import './DriversList.css'

const DriversList = () => {
  const [drivers, setDrivers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [expandedDriver, setExpandedDriver] = useState(null)

  useEffect(() => {
    loadApprovedDrivers()
  }, [])

  const loadApprovedDrivers = async () => {
    try {
      setLoading(true)
      setError('')
      const data = await adminService.getAllDrivers()
      const approved = data.filter((d) => d.approval_status === 'APPROVED')
      setDrivers(approved)
    } catch (err) {
      console.error('Failed to load drivers:', err)
      setError(err.message || 'Failed to load drivers')
    } finally {
      setLoading(false)
    }
  }

  const handleExpand = (driver) => {
    if (expandedDriver?.driver_id === driver.driver_id) {
      setExpandedDriver(null)
    } else {
      setExpandedDriver(driver)
    }
  }

  if (loading) {
    return <div className="loading">Loading drivers...</div>
  }

  return (
    <div className="drivers-list-view">
      <h1>Approved Drivers</h1>

      {error && <div className="error">{error}</div>}

      {drivers.length === 0 ? (
        <p className="no-data">No approved drivers</p>
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
                </div>
                <div className="toggle-icon">
                  {expandedDriver?.driver_id === driver.driver_id ? '▼' : '▶'}
                </div>
              </div>

              {expandedDriver?.driver_id === driver.driver_id && (
                <div className="driver-details">
                  <p>
                    <strong>Approval Status:</strong> {driver.approval_status}
                  </p>
                  <p>
                    <strong>Vehicle Categories:</strong>{' '}
                    {driver.allowed_vehicle_categories?.join(', ') || 'None'}
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default DriversList
