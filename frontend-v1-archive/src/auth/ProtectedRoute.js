import { Navigate } from "react-router-dom";
import { useAuth } from "./AuthContext";

const ProtectedRoute = ({ children, roles = null, requireActive = false }) => {
  const { isAuthenticated, user, authChecked } = useAuth();

  // ⏳ Wait until auth state is restored
  if (!authChecked) {
    return <div>Loading...</div>;
  }

  // 🔒 Not logged in
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // 🔒 Role-based restriction
  if (roles && !roles.includes(user.role)) {
    return <div>Access Denied</div>;
  }

  // 🔒 Capability-based restriction
  if (requireActive && user.status !== "ACTIVE") {
    return <div>Account not active</div>;
  }

  return children;
};

export default ProtectedRoute;
