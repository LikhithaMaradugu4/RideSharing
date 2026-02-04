import { useState, useEffect } from 'react'
import { Routes, Route, Navigate, useNavigate } from 'react-router-dom'
import AdminSidebar from './AdminSidebar'
import AdminHeader from './AdminHeader'
import TenantsList from '../platform-admin/TenantsList'
import TenantCreate from '../platform-admin/TenantCreate'
import TenantDetails from '../platform-admin/TenantDetails'
import TenantAdmins from '../platform-admin/TenantAdmins'
import TenantDocuments from '../platform-admin/TenantDocuments'
import Dashboard from '../tenant-admin/Dashboard'
import DriverApprovals from '../tenant-admin/DriverApprovals'
import FleetApprovals from '../tenant-admin/FleetApprovals'
import DriversList from '../tenant-admin/DriversList'
import FleetsList from '../tenant-admin/FleetsList'
import adminService from '../../services/admin.service'
import './AdminLayout.css'
import VehicleApprovals from '../tenant-admin/VehicleApprovals'

const AdminLayout = () => {
  const [adminData, setAdminData] = useState(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    const fetchAdmin = async () => {
      try {
        const data = await adminService.getCurrentAdmin()
        setAdminData(data)
      } catch (error) {
        console.error('Admin auth failed:', error)
        navigate('/admin/login')
      } finally {
        setLoading(false)
      }
    }

    fetchAdmin()
  }, [navigate])

  if (loading) {
    return <div>Loading admin...</div>
  }

  if (!adminData) {
    return <Navigate to="/admin/login" />
  }

  return (
    <div className="admin-layout">
      <AdminSidebar adminData={adminData} />
      <div className="admin-main">
        <AdminHeader adminData={adminData} />
        <div className="admin-content">
          <Routes>
            {adminData.admin_type === 'PLATFORM' && (
              <>
                <Route path="platform/tenants" element={<TenantsList />} />
                <Route path="platform/tenants/create" element={<TenantCreate />} />
                <Route path="platform/tenants/:tenantId" element={<TenantDetails />} />
                <Route path="platform/tenants/:tenantId/admins" element={<TenantAdmins />} />
                <Route path="platform/tenants/:tenantId/documents" element={<TenantDocuments />} />
              </>
            )}
            {adminData.admin_type === 'TENANT' && (
              <>
                <Route path="tenant/dashboard" element={<Dashboard />} />
                <Route path="tenant/driver-approvals" element={<DriverApprovals />} />
                <Route path="tenant/fleet-approvals" element={<FleetApprovals />} />
                <Route path="tenant/drivers" element={<DriversList />} />
                <Route path="tenant/fleets" element={<FleetsList />} />
                <Route path="tenant/vehicles" element={<VehicleApprovals/>}/>
              </>
        
            )}
          </Routes>
        </div>
      </div>
    </div>
  )
}

export default AdminLayout
