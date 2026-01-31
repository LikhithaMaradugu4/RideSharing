import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import './App.css'
import AdminLayout from './admin/layout/AdminLayout'
import AdminLogin from './admin/auth/AdminLogin'
import OtpLogin from './app/pages/OtpLogin'
import UserHome from './app/pages/UserHome'
import Profile from './app/pages/Profile'
import DriverApply from './app/pages/DriverApply'
import FleetOwnerApply from './app/pages/FleetOwnerApply'
import TenantSelection from './app/TenantSelection'
import DriverDashboard from './app/pages/DriverDashboard'
import DriverDispatches from './app/pages/DriverDispatches'
import DriverVehicles from './app/pages/DriverVehicles'
import DriverAvailability from './app/pages/DriverAvailability'
import DriverFleets from './app/pages/DriverFleets'
import RiderDashboard from './app/pages/RiderDashboard'
import RiderTripStatus from './app/pages/RiderTripStatus'
import TripPlanning from './app/pages/TripPlanning'
import adminService from './services/admin.service'

function App() {
  const [adminData, setAdminData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchAdminData = async () => {
      try {
        const data = await adminService.getCurrentAdmin()
        setAdminData(data)
      } catch (error) {
        console.error('Failed to fetch admin data:', error)
        setAdminData(null)
      } finally {
        setLoading(false)
      }
    }

    fetchAdminData()
  }, [])

  if (loading) {
    return <div>Loading...</div>
  }

  const refetchAdminData = async () => {
    try {
      const data = await adminService.getCurrentAdmin()
      setAdminData(data)
    } catch (error) {
      console.error('Failed to refetch admin data:', error)
    }
  }

  /**
   * Check if user is authenticated as normal user (OTP-authenticated)
   * This checks for JWT token, not admin authentication
   */
  const isUserAuthenticated = () => {
    const token = localStorage.getItem('jwt_token')
    return !!token
  }

  /**
   * Decode JWT payload (unsafe decode; for role check only)
   */
  const getJwtPayload = () => {
    const token = localStorage.getItem('jwt_token')
    if (!token) return null
    try {
      const parts = token.split('.')
      if (parts.length !== 3) return null
      const payload = JSON.parse(atob(parts[1]))
      return payload
    } catch {
      return null
    }
  }

  /**
   * Admin tokens must not access user flow
   */
  const isUserAdmin = () => {
    const payload = getJwtPayload()
    const role = (payload?.role || '').toUpperCase()
    return role === 'ADMIN' || role === 'PLATFORM_ADMIN'
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AdminLogin onLoginSuccess={refetchAdminData} />} />
        <Route path="/admin/login" element={<AdminLogin onLoginSuccess={refetchAdminData} />} />
        {/* OTP Login for normal users */}
        <Route path="/login" element={<OtpLogin />} />
        <Route 
          path="/admin/*" 
          element={adminData ? <AdminLayout adminData={adminData} /> : <Navigate to="/admin/login" />}
        />
        
        {/* User App Routes - OTP-authenticated normal users only */}
        <Route 
          path="/app/home" 
          element={
            isUserAuthenticated()
              ? (isUserAdmin() ? <Navigate to="/admin/login" /> : <UserHome />)
              : <Navigate to="/login" />
          }
        />

        {/* Shared Profile Page */}
        <Route
          path="/app/profile"
          element={
            isUserAuthenticated()
              ? (isUserAdmin() ? <Navigate to="/admin/login" /> : <Profile />)
              : <Navigate to="/login" />
          }
        />

        {/* Driver Pages */}
        <Route
          path="/apply-driver/:tenantId"
          element={
            isUserAuthenticated()
              ? (isUserAdmin() ? <Navigate to="/admin/login" /> : <DriverApply />)
              : <Navigate to="/login" />
          }
        />

        <Route
          path="/driver-tenant-selection"
          element={
            isUserAuthenticated()
              ? (isUserAdmin() ? <Navigate to="/admin/login" /> : <TenantSelection applicationType="driver" />)
              : <Navigate to="/login" />
          }
        />

        <Route
          path="/apply-fleet-owner/:tenantId"
          element={
            isUserAuthenticated()
              ? (isUserAdmin() ? <Navigate to="/admin/login" /> : <FleetOwnerApply />)
              : <Navigate to="/login" />
          }
        />

        <Route
          path="/fleet-owner-tenant-selection"
          element={
            isUserAuthenticated()
              ? (isUserAdmin() ? <Navigate to="/admin/login" /> : <TenantSelection applicationType="fleet-owner" />)
              : <Navigate to="/login" />
          }
        />

        <Route
          path="/app/driver/apply"
          element={
            isUserAuthenticated()
              ? (isUserAdmin() ? <Navigate to="/admin/login" /> : <Navigate to="/driver-tenant-selection" />)
              : <Navigate to="/login" />
          }
        />

        <Route
          path="/app/driver/dashboard"
          element={
            isUserAuthenticated()
              ? (isUserAdmin() ? <Navigate to="/admin/login" /> : <DriverDashboard />)
              : <Navigate to="/login" />
          }
        />

        <Route
          path="/app/driver/dispatches"
          element={
            isUserAuthenticated()
              ? (isUserAdmin() ? <Navigate to="/admin/login" /> : <DriverDispatches />)
              : <Navigate to="/login" />
          }
        />

        <Route
          path="/app/driver/vehicles"
          element={
            isUserAuthenticated()
              ? (isUserAdmin() ? <Navigate to="/admin/login" /> : <DriverVehicles />)
              : <Navigate to="/login" />
          }
        />

        <Route
          path="/app/driver/availability"
          element={
            isUserAuthenticated()
              ? (isUserAdmin() ? <Navigate to="/admin/login" /> : <DriverAvailability />)
              : <Navigate to="/login" />
          }
        />

        <Route
          path="/app/driver/fleets"
          element={
            isUserAuthenticated()
              ? (isUserAdmin() ? <Navigate to="/admin/login" /> : <DriverFleets />)
              : <Navigate to="/login" />
          }
        />

        {/* Rider Routes */}
        <Route
          path="/app/rider-dashboard"
          element={
            isUserAuthenticated()
              ? (isUserAdmin() ? <Navigate to="/admin/login" /> : <RiderDashboard />)
              : <Navigate to="/login" />
          }
        />

        <Route
          path="/app/rider/book"
          element={
            isUserAuthenticated()
              ? (isUserAdmin() ? <Navigate to="/admin/login" /> : <TripPlanning />)
              : <Navigate to="/login" />
          }
        />

        <Route
          path="/app/rider/trip/:tripId"
          element={
            isUserAuthenticated()
              ? (isUserAdmin() ? <Navigate to="/admin/login" /> : <RiderTripStatus />)
              : <Navigate to="/login" />
          }
        />
      </Routes>
    </BrowserRouter>
  )
}


export default App