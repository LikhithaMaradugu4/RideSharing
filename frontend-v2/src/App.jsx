import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import './App.css'
import ProtectedRoute from './components/ProtectedRoute'
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
import DriverFleets from './app/pages/DriverFleets'
import DriverEarnings from './app/pages/DriverEarnings'
import DriverRatings from './app/pages/DriverRatings'
import DriverApplicationStatus from './app/pages/DriverApplicationStatus'
import FleetApplicationStatus from './app/pages/FleetApplicationStatus'
import RiderDashboard from './app/pages/RiderDashboard'
import RiderTripStatus from './app/pages/RiderTripStatus'
import TripPlanning from './app/pages/TripPlanning'
import FleetDashboard from './app/pages/FleetDashboard'
import FleetVehicles from './app/pages/FleetVehicles'
import FleetDrivers from './app/pages/FleetDrivers'
import FleetAssignments from './app/pages/FleetAssignments'
import FleetTrips from './app/pages/FleetTrips'
import FleetCities from './app/pages/FleetCities'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AdminLogin />} />
        <Route path="/admin/login" element={<AdminLogin />} />
        <Route path="/login" element={<OtpLogin />} />
        <Route path="/admin/*" element={<AdminLayout />} />
        
        {/* User App Routes - Protected */}
        <Route 
          path="/app/home" 
          element={<ProtectedRoute><UserHome /></ProtectedRoute>}
        />

        <Route
          path="/app/profile"
          element={<ProtectedRoute><Profile /></ProtectedRoute>}
        />

        {/* Driver Routes */}
        <Route
          path="/apply-driver/:tenantId"
          element={<ProtectedRoute><DriverApply /></ProtectedRoute>}
        />

        <Route
          path="/driver-tenant-selection"
          element={<ProtectedRoute><TenantSelection applicationType="driver" /></ProtectedRoute>}
        />

        <Route
          path="/apply-fleet-owner/:tenantId"
          element={<ProtectedRoute><FleetOwnerApply /></ProtectedRoute>}
        />

        <Route
          path="/fleet-owner-tenant-selection"
          element={<ProtectedRoute><TenantSelection applicationType="fleet-owner" /></ProtectedRoute>}
        />

        <Route
          path="/app/driver/apply"
          element={<ProtectedRoute><Navigate to="/driver-tenant-selection" /></ProtectedRoute>}
        />

        <Route
          path="/app/driver/dashboard"
          element={<ProtectedRoute><DriverDashboard /></ProtectedRoute>}
        />

        <Route
          path="/app/driver/dispatches"
          element={<ProtectedRoute><DriverDispatches /></ProtectedRoute>}
        />

        <Route
          path="/app/driver/vehicles"
          element={<ProtectedRoute><DriverVehicles /></ProtectedRoute>}
        />

        {/* Driver availability route removed - feature discontinued */}

        <Route
          path="/app/driver/fleets"
          element={<ProtectedRoute><DriverFleets /></ProtectedRoute>}
        />

        <Route
          path="/app/driver/earnings"
          element={<ProtectedRoute><DriverEarnings /></ProtectedRoute>}
        />

        <Route
          path="/app/driver/ratings"
          element={<ProtectedRoute><DriverRatings /></ProtectedRoute>}
        />

        <Route
          path="/app/driver/application-status"
          element={<ProtectedRoute><DriverApplicationStatus /></ProtectedRoute>}
        />

        <Route
          path="/app/fleet/application-status"
          element={<ProtectedRoute><FleetApplicationStatus /></ProtectedRoute>}
        />

        {/* Rider Routes */}
        <Route
          path="/app/rider-dashboard"
          element={<ProtectedRoute><RiderDashboard /></ProtectedRoute>}
        />

        <Route
          path="/app/rider/book"
          element={<ProtectedRoute><TripPlanning /></ProtectedRoute>}
        />

        <Route
          path="/app/rider/trip/:tripId"
          element={<ProtectedRoute><RiderTripStatus /></ProtectedRoute>}
        />

        {/* Fleet Owner Routes */}
        <Route
          path="/fleet-dashboard"
          element={<ProtectedRoute><FleetDashboard /></ProtectedRoute>}
        />

        <Route
          path="/fleet-vehicles"
          element={<ProtectedRoute><FleetVehicles /></ProtectedRoute>}
        />

        <Route
          path="/fleet-drivers"
          element={<ProtectedRoute><FleetDrivers /></ProtectedRoute>}
        />

        <Route
          path="/fleet-assignments"
          element={<ProtectedRoute><FleetAssignments /></ProtectedRoute>}
        />

        <Route
          path="/fleet-trips"
          element={<ProtectedRoute><FleetTrips /></ProtectedRoute>}
        />

        <Route
          path="/fleet-cities"
          element={<ProtectedRoute><FleetCities /></ProtectedRoute>}
        />

        {/* Shorthand routes */}
        <Route
          path="/rider-dashboard"
          element={<Navigate to="/app/rider-dashboard" />}
        />
      </Routes>
    </BrowserRouter>
  )
}

export default App