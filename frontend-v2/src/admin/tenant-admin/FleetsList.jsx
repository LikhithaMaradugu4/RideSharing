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
    return (
      <div className="loading-state">
        <div className="spinner"></div>
        <p>Loading approved fleets...</p>
      </div>
    )
  }

  return (
    <div className="fleets-list-view">
      <div className="page-header">
        <h1>Approved Fleets</h1>
        <div className="count-badge">{fleets.length} Partners</div>
      </div>

      {error && (
        <div className="error-banner">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
          {error}
        </div>
      )}

      {fleets.length === 0 ? (
        <div className="empty-state">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path></svg>
          <p>No approved fleets found.</p>
        </div>
      ) : (
        <div className="fleets-list">
          {fleets.map((fleet) => {
            const isExpanded = expandedFleet?.fleet_id === fleet.fleet_id;
            const isActive = fleet.status === 'ACTIVE';

            return (
              <div
                key={fleet.fleet_id}
                className={`fleet-card ${isExpanded ? 'expanded' : ''}`}
              >
                <div className="fleet-header" onClick={() => handleExpand(fleet)}>
                  <div className="fleet-avatar">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 21h18"/><path d="M5 21V7l8-4 8 4v14"/><path d="M9 10a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v11H9z"/></svg>
                  </div>

                  <div className="fleet-info">
                    <div className="fleet-name-row">
                      <h3>{fleet.fleet_name}</h3>
                      <span className={`status-indicator ${isActive ? 'active' : 'inactive'}`}>
                        {isActive ? 'Active' : fleet.status}
                      </span>
                    </div>
                    
                    <div className="fleet-meta">
                      <span className="type-text">
                         {fleet.fleet_type} Fleet
                      </span>
                    </div>
                  </div>

                  <div className={`toggle-icon ${isExpanded ? 'rotated' : ''}`}>
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
                  </div>
                </div>

                {isExpanded && (
                  <div className="fleet-details">
                    <div className="details-content">
                      <div className="detail-row">
                        <span className="label">Operational Status:</span>
                        <span className={`status-text ${isActive ? 'green' : 'grey'}`}>
                           {fleet.status}
                        </span>
                      </div>

                      <div className="detail-row">
                         <span className="label">Approval:</span>
                         <span className="value-with-icon">
                            <svg className="check-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"><polyline points="20 6 9 17 4 12"></polyline></svg>
                            {fleet.approval_status}
                         </span>
                      </div>

                      <div className="detail-row full-width">
                        <span className="label">Fleet ID:</span>
                        <span className="value code-font">{fleet.fleet_id}</span>
                      </div>
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

export default FleetsList