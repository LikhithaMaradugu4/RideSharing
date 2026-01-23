import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./auth/AuthContext";
import ProtectedRoute from "./auth/ProtectedRoute";

import Login from "./Login";
import RiderDashboard from "./RiderDashboard";
import DriverDashboard from "./DriverDashboard";
import DriverOffers from "./DriverOffers";
import DriverTripDetail from "./DriverTripDetail";
import DriverProfile from "./DriverProfile";
import DriverApplicationForm from "./DriverApplicationForm";
import DriverShiftManagement from "./DriverShiftManagement";
import TenantDashboard from "./TenantDashboard";
import CreateRide from "./CreateRide";
import PricingComparison from "./PricingComparison";
import ConfirmRide from "./ConfirmRide";
import TripStatus from "./TripStatus";

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public */}
          <Route path="/login" element={<Login />} />

          {/* All app routes MUST be protected */}
          <Route
            path="/app"
            element={
              <ProtectedRoute>
                <Navigate to="/app/ride" replace />
              </ProtectedRoute>
            }
          />

          {/* Rider (ACTIVE capability) */}
          <Route
            path="/app/ride"
            element={
              <ProtectedRoute requireActive>
                <RiderDashboard />
              </ProtectedRoute>
            }
          />

          {/* Driver (ROLE = DRIVER) */}
          <Route
            path="/app/driver"
            element={
              <ProtectedRoute roles={["DRIVER"]}>
                <DriverDashboard />
              </ProtectedRoute>
            }
          />

          <Route
            path="/app/driver/offers"
            element={
              <ProtectedRoute roles={["DRIVER"]}>
                <DriverOffers />
              </ProtectedRoute>
            }
          />

          <Route
            path="/app/driver/trip/:tripId"
            element={
              <ProtectedRoute roles={["DRIVER"]}>
                <DriverTripDetail />
              </ProtectedRoute>
            }
          />

          <Route
            path="/app/driver/profile"
            element={
              <ProtectedRoute roles={["DRIVER"]}>
                <DriverProfile />
              </ProtectedRoute>
            }
          />

          <Route
            path="/app/driver/apply"
            element={
              <ProtectedRoute roles={["DRIVER"]}>
                <DriverApplicationForm />
              </ProtectedRoute>
            }
          />

          <Route
            path="/app/driver/shift"
            element={
              <ProtectedRoute roles={["DRIVER"]}>
                <DriverShiftManagement />
              </ProtectedRoute>
            }
          />

          {/* Tenant Admin (ROLE = TENANT_ADMIN) */}
          <Route
            path="/app/tenant"
            element={
              <ProtectedRoute roles={["TENANT_ADMIN"]}>
                <TenantDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/app/ride/create"
            element={
              <ProtectedRoute requireActive>
                <CreateRide />
              </ProtectedRoute>
            }
          />

          <Route
            path="/app/ride/:rideRequestId/pricing"
            element={
              <ProtectedRoute requireActive>
                <PricingComparison />
              </ProtectedRoute>
            }
          />

          <Route
            path="/app/ride/:rideRequestId/confirm"
            element={
              <ProtectedRoute requireActive>
                <ConfirmRide />
              </ProtectedRoute>
            }
          />

          <Route
            path="/app/trip/:tripId/status"
            element={
              <ProtectedRoute requireActive>
                <TripStatus />
              </ProtectedRoute>
            }
          />

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
