import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { startShiftApi, endShiftApi, getDriverProfileApi } from "./api/driverTrips.api";

function DriverShiftManagement() {
  const navigate = useNavigate();
  const [shiftStatus, setShiftStatus] = useState("ENDED"); // STARTED or ENDED
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState(null);
  const [shiftStartTime, setShiftStartTime] = useState(null);

  useEffect(() => {
    fetchShiftStatus();
  }, []);

  const fetchShiftStatus = async () => {
    try {
      const profile = await getDriverProfileApi();
      // For now, we'll just check if profile exists
      // Backend would need to return shift status in the response
      setShiftStatus("ENDED");
      setLoading(false);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load shift status");
      setLoading(false);
    }
  };

  const handleStartShift = async () => {
    setActionLoading(true);
    try {
      await startShiftApi();
      setShiftStatus("STARTED");
      setShiftStartTime(new Date());
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to start shift");
    } finally {
      setActionLoading(false);
    }
  };

  const handleEndShift = async () => {
    if (!window.confirm("Are you sure you want to end your shift?")) return;

    setActionLoading(true);
    try {
      await endShiftApi();
      setShiftStatus("ENDED");
      setShiftStartTime(null);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to end shift");
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return <div style={{ maxWidth: "520px", margin: "60px auto", padding: "20px" }}>Loading shift status...</div>;
  }

  return (
    <div style={{ maxWidth: "520px", margin: "60px auto", padding: "20px" }}>
      <h2>Shift Management</h2>

      {error && <div style={{ padding: "12px", backgroundColor: "#ffebee", color: "#c62828", borderRadius: "4px", marginBottom: "16px" }}>{error}</div>}

      {/* Status Card */}
      <div style={{ border: "1px solid #ddd", borderRadius: "8px", padding: "24px", marginBottom: "24px", textAlign: "center", backgroundColor: shiftStatus === "STARTED" ? "#e8f5e9" : "#f5f5f5" }}>
        <div style={{ fontSize: "18px", fontWeight: "600", marginBottom: "8px" }}>Current Shift Status</div>
        <div
          style={{
            fontSize: "32px",
            fontWeight: "700",
            color: shiftStatus === "STARTED" ? "#27ae60" : "#666",
            marginBottom: "12px",
          }}
        >
          {shiftStatus === "STARTED" ? "🟢 ACTIVE" : "⚫ INACTIVE"}
        </div>

        {shiftStartTime && (
          <div style={{ fontSize: "14px", color: "#666" }}>
            Started at {shiftStartTime.toLocaleTimeString()}
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
        {shiftStatus === "ENDED" ? (
          <button
            onClick={handleStartShift}
            disabled={actionLoading}
            style={{
              padding: "16px",
              backgroundColor: actionLoading ? "#ccc" : "#27ae60",
              color: "white",
              border: "none",
              borderRadius: "6px",
              cursor: actionLoading ? "not-allowed" : "pointer",
              fontSize: "18px",
              fontWeight: "600",
            }}
          >
            {actionLoading ? "Starting..." : "🚀 Start Shift"}
          </button>
        ) : (
          <button
            onClick={handleEndShift}
            disabled={actionLoading}
            style={{
              padding: "16px",
              backgroundColor: actionLoading ? "#ccc" : "#f44336",
              color: "white",
              border: "none",
              borderRadius: "6px",
              cursor: actionLoading ? "not-allowed" : "pointer",
              fontSize: "18px",
              fontWeight: "600",
            }}
          >
            {actionLoading ? "Ending..." : "⏹️ End Shift"}
          </button>
        )}

        <button
          onClick={() => navigate("/app/driver")}
          style={{
            padding: "12px",
            backgroundColor: "#666",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
            fontSize: "16px",
            fontWeight: "600",
          }}
        >
          Back to Dashboard
        </button>
      </div>

      {/* Info */}
      <div style={{ marginTop: "24px", padding: "12px", backgroundColor: "#f5f5f5", borderRadius: "4px", fontSize: "14px", color: "#666" }}>
        <strong>Note:</strong> You can only receive trip offers when your shift is active. Make sure to update your location before starting your shift.
      </div>
    </div>
  );
}

export default DriverShiftManagement;
