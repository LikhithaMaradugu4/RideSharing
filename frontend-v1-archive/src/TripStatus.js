import { useEffect, useState, useMemo } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getTripStatusApi } from "./api/trips.api";

const FINAL_STATUSES = ["COMPLETED", "CANCELLED"];

function TripStatus() {
  const { tripId } = useParams();
  const navigate = useNavigate();

  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const statusLabel = useMemo(() => {
    switch (status) {
      case "REQUESTED":
        return "Looking for a driver";
      case "ASSIGNED":
        return "Driver assigned";
      case "ON_TRIP":
        return "On trip";
      case "COMPLETED":
        return "Trip completed";
      case "CANCELLED":
        return "Trip cancelled";
      default:
        return status || "Unknown";
    }
  }, [status]);

  useEffect(() => {
    let isMounted = true;
    let intervalId = null;

    const fetchStatus = async () => {
      if (!tripId) {
        setError("Missing trip id");
        setLoading(false);
        return true;
      }
      try {
        const data = await getTripStatusApi(tripId);
        if (!isMounted) return;
        setStatus(data.status);
        setLastUpdated(new Date());
        setError(null);
        setLoading(false);

        const isFinal = FINAL_STATUSES.includes(data.status);
        if (isFinal && intervalId) clearInterval(intervalId);
        return isFinal;
      } catch (err) {
        if (!isMounted) return;
        setError(err.response?.data?.detail || "Failed to load trip status");
        setLoading(false);
        return true;
      }
    };

    (async () => {
      const isFinal = await fetchStatus();
      if (!isFinal) {
        intervalId = setInterval(fetchStatus, 3500);
      }
    })();

    return () => {
      isMounted = false;
      if (intervalId) clearInterval(intervalId);
    };
  }, [tripId]);

  const handleBack = () => navigate("/app/ride");

  return (
    <div style={{ maxWidth: "520px", margin: "60px auto", padding: "20px", border: "1px solid #ddd", borderRadius: "8px" }}>
      <h2>Trip Status</h2>
      <p><b>Trip ID:</b> {tripId}</p>

      {loading && <div>Loading status...</div>}
      {error && <div style={{ color: "red" }}>{error}</div>}

      {!loading && !error && (
        <div style={{ marginTop: "12px" }}>
          <div style={{ fontSize: "20px", fontWeight: 600 }}>{statusLabel}</div>
          <div style={{ color: "#555", marginTop: "4px" }}>({status || "UNKNOWN"})</div>
          {lastUpdated && (
            <div style={{ fontSize: "12px", color: "#777", marginTop: "6px" }}>
              Updated {lastUpdated.toLocaleTimeString()}
            </div>
          )}
        </div>
      )}

      {FINAL_STATUSES.includes(status) && (
        <button style={{ marginTop: "18px" }} onClick={handleBack}>
          Back to rides
        </button>
      )}
    </div>
  );
}

export default TripStatus;
