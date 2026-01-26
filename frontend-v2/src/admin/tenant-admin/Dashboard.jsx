import { useState, useEffect } from 'react'
import adminService from '../../services/admin.service'
import './Dashboard.css'

const Dashboard = () => {
  const [stats, setStats] = useState({
    pendingDrivers: 0,
    pendingFleets: 0,
    approvedDrivers: 0,
    approvedFleets: 0,
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    try {
      setLoading(true)
      setError('')

      const [pendingDrivers, pendingFleets, allDrivers, allFleets] = await Promise.all([
        adminService.getPendingDrivers(),
        adminService.getPendingFleets(),
        adminService.getAllDrivers(),
        adminService.getAllFleets(),
      ])

      const approvedDrivers = allDrivers.filter(
        (d) => d.approval_status === 'APPROVED'
      ).length

      const approvedFleets = allFleets.filter(
        (f) => f.approval_status === 'APPROVED'
      ).length

      setStats({
        pendingDrivers: pendingDrivers.length,
        pendingFleets: pendingFleets.length,
        approvedDrivers,
        approvedFleets,
      })
    } catch (err) {
      console.error('Failed to load stats:', err)
      setError(err.message || 'Failed to load dashboard stats')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="dashboard-loading">Loading...</div>
  }

  return (
    <div className="tenant-dashboard">
      <h1>Tenant Admin Dashboard</h1>

      {error && <div className="dashboard-error">{error}</div>}

      <div className="stats-grid">
        <div className="stat-card pending">
          <h3>Pending Drivers</h3>
          <p className="stat-number">{stats.pendingDrivers}</p>
        </div>

        <div className="stat-card pending">
          <h3>Pending Fleets</h3>
          <p className="stat-number">{stats.pendingFleets}</p>
        </div>

        <div className="stat-card approved">
          <h3>Approved Drivers</h3>
          <p className="stat-number">{stats.approvedDrivers}</p>
        </div>

        <div className="stat-card approved">
          <h3>Approved Fleets</h3>
          <p className="stat-number">{stats.approvedFleets}</p>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
