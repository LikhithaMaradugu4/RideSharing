import { useState, useEffect } from 'react'
import adminService from '../../services/admin.service'
import './FleetsList.css'

const FleetsList = () => {
  const [fleets, setFleets] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [expandedFleet, setExpandedFleet] = useState(null)

  useEffect(() => {
    loadApprovedFleets()
  }, [])

  const loadApprovedFleets = async () => {
    try {
      setLoading(true)
      setError('')
      const data = await adminService.getAllFleets()
      const approved = data.filter((f) => f.approval_status === 'APPROVED')
      setFleets(approved)
    } catch (err) {
      console.error('Failed to load fleets:', err)
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

  if (loading) {
    return <div className="loading">Loading fleets...</div>
  }

  return (
    <div className="fleets-list-view">
      <h1>Approved Fleets</h1>

      {error && <div className="error">{error}</div>}

      {fleets.length === 0 ? (
        <p className="no-data">No approved fleets</p>
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
                </div>
                <div className="toggle-icon">
                  {expandedFleet?.fleet_id === fleet.fleet_id ? '▼' : '▶'}
                </div>
              </div>

              {expandedFleet?.fleet_id === fleet.fleet_id && (
                <div className="fleet-details">
                  <p>
                    <strong>Status:</strong> {fleet.status}
                  </p>
                  <p>
                    <strong>Approval Status:</strong> {fleet.approval_status}
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

export default FleetsList
