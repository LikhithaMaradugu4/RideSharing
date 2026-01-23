import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getDriverProfileApi, updateLocationApi } from "./api/driverTrips.api";

function DriverProfile() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [updatingLocation, setUpdatingLocation] = useState(false);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const data = await getDriverProfileApi();
      setProfile(data);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load profile");
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateLocation = async () => {
    setUpdatingLocation(true);
    try {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          async (position) => {
            const { latitude, longitude } = position.coords;
            await updateLocationApi(latitude, longitude);
            setError(null);
            alert("Location updated successfully!");
          },
          (err) => {
            setError("Unable to get location. Please enable location services.");
            setUpdatingLocation(false);
          }
        );
      } else {
        setError("Geolocation not supported by your browser");
        setUpdatingLocation(false);
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to update location");
      setUpdatingLocation(false);
    }
  };

  const handleApply = () => {
    navigate("/app/driver/apply");
  };

  if (loading) {
    return <div style={{ maxWidth: "520px", margin: "60px auto", padding: "20px" }}>Loading profile...</div>;
  }

  return (
    <div style={{ maxWidth: "520px", margin: "20px auto", padding: "20px" }}>
      <h2>Driver Profile</h2>

      {error && <div style={{ padding: "12px", backgroundColor: "#ffebee", color: "#c62828", borderRadius: "4px", marginBottom: "16px" }}>{error}</div>}

      {profile ? (
        <div>
          {/* Profile Card */}
          <div style={{ border: "1px solid #ddd", borderRadius: "8px", padding: "16px", marginBottom: "16px" }}>
            <div style={{ marginBottom: "12px" }}>
              <strong>Driver ID:</strong> {profile.driver_id}
            </div>
            <div style={{ marginBottom: "12px" }}>
              <strong>Tenant ID:</strong> {profile.tenant_id}
            </div>
            <div style={{ marginBottom: "12px" }}>
              <strong>Driver Type:</strong> {profile.driver_type}
            </div>
            <div style={{ marginBottom: "12px" }}>
              <strong>Status:</strong>
              <span
                style={{
                  marginLeft: "8px",
                  padding: "4px 12px",
                  borderRadius: "4px",
                  backgroundColor: profile.approval_status === "APPROVED" ? "#e8f5e9" : "#fff3e0",
                  color: profile.approval_status === "APPROVED" ? "#2e7d32" : "#e65100",
                  fontWeight: "600",
                }}
              >
                {profile.approval_status}
              </span>
            </div>
            {profile.rating && (
              <div style={{ marginBottom: "12px" }}>
                <strong>Rating:</strong> {profile.rating.toFixed(2)} ⭐
              </div>
            )}
          </div>

          {/* Actions */}
          {profile.approval_status === "APPROVED" && (
            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              <button
                onClick={handleUpdateLocation}
                disabled={updatingLocation}
                style={{
                  padding: "12px",
                  backgroundColor: updatingLocation ? "#ccc" : "#2196F3",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: updatingLocation ? "not-allowed" : "pointer",
                  fontSize: "16px",
                  fontWeight: "600",
                }}
              >
                {updatingLocation ? "Updating Location..." : "📍 Update Location"}
              </button>

              <button
                onClick={() => navigate("/app/driver")}
                style={{
                  padding: "12px",
                  backgroundColor: "#27ae60",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: "pointer",
                  fontSize: "16px",
                  fontWeight: "600",
                }}
              >
                Go to Dashboard
              </button>
            </div>
          )}

          {profile.approval_status !== "APPROVED" && (
            <div>
              <p style={{ color: "#666", marginBottom: "16px" }}>Your application is pending approval. Check back soon!</p>
              <button
                onClick={() => navigate("/app/driver")}
                style={{
                  width: "100%",
                  padding: "12px",
                  backgroundColor: "#666",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: "pointer",
                  fontSize: "16px",
                }}
              >
                Back to Dashboard
              </button>
            </div>
          )}
        </div>
      ) : (
        <div style={{ backgroundColor: "#f5f5f5", padding: "20px", borderRadius: "8px", textAlign: "center" }}>
          <p>No profile found. Apply as a driver to get started.</p>
          <button
            onClick={handleApply}
            style={{
              marginTop: "12px",
              padding: "12px 24px",
              backgroundColor: "#27ae60",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
              fontSize: "16px",
              fontWeight: "600",
            }}
          >
            Apply Now
          </button>
        </div>
      )}
    </div>
  );
}

export default DriverProfile;
