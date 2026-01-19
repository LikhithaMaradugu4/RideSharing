import { useEffect, useState, useMemo } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getTripDetailsApi, startTripApi, completeTripApi } from "./api/driverTrips.api";

const FINAL_STATUSES = ["COMPLETED", "CANCELLED"];

function DriverTripDetail() {
  const { tripId } = useParams();
  const navigate = useNavigate();

  const [trip, setTrip] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [actionLoading, setActionLoading] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const statusLabel = useMemo(() => {
    switch (trip?.status) {
      case "ASSIGNED":
        return "Driver assigned";
      case "PICKED_UP":
        return "Rider picked up";
      case "ON_TRIP":
        return "On trip";
      case "COMPLETED":
        return "Trip completed";
      case "CANCELLED":
        return "Trip cancelled";
      default:
        return trip?.status || "Unknown";
    }
  }, [trip?.status]);

  useEffect(() => {
    let isMounted = true;
    let intervalId = null;

    const fetchTripDetails = async () => {
      if (!tripId) {
        setError("Missing trip id");
        setLoading(false);
        return true;
      }
      try {
        const data = await getTripDetailsApi(tripId);
        if (!isMounted) return;
        setTrip(data);
        setLastUpdated(new Date());
        setError(null);
        setLoading(false);

        const isFinal = FINAL_STATUSES.includes(data.status);
        if (isFinal && intervalId) clearInterval(intervalId);
        return isFinal;
      } catch (err) {
        if (!isMounted) return;
        setError(err.response?.data?.detail || "Failed to load trip details");
        setLoading(false);
        return true;
      }
    };

    (async () => {
      const isFinal = await fetchTripDetails();
      if (!isFinal) {
        intervalId = setInterval(fetchTripDetails, 3000);
      }
    })();

    return () => {
      isMounted = false;
      if (intervalId) clearInterval(intervalId);
    };
  }, [tripId]);

  const handleStartTrip = async () => {
    setActionLoading("start");
    try {
      await startTripApi(tripId);
      // Refresh trip details
      const data = await getTripDetailsApi(tripId);
      setTrip(data);
      setActionLoading(null);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to start trip");
      setActionLoading(null);
    }
  };

  const handleCompleteTrip = async () => {
    setActionLoading("complete");
    try {
      await completeTripApi(tripId);
      // Refresh trip details
      const data = await getTripDetailsApi(tripId);
      setTrip(data);
      setActionLoading(null);
      // Optionally navigate to payment summary after completion
      // navigate(`/app/trip/${tripId}/payment`);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to complete trip");
      setActionLoading(null);
    }
  };

  const handleCancelTrip = () => {
    if (window.confirm("Are you sure you want to cancel this trip?")) {
      // TODO: Implement cancel trip API call when available
      setError("Cancel functionality not yet implemented");
    }
  };

  const handleBack = () => navigate("/app/driver");

  return (
    <div style={{ maxWidth: "520px", margin: "60px auto", padding: "20px", border: "1px solid #ddd", borderRadius: "8px" }}>
      <h2>Trip Details</h2>
      <p>
        <b>Trip ID:</b> {tripId}
      </p>

      {loading && <div>Loading trip details...</div>}
      {error && <div style={{ color: "red", marginBottom: "16px" }}>{error}</div>}

      {!loading && !error && trip && (
        <div style={{ marginTop: "16px" }}>
          {/* Trip Status */}
          <div style={{ marginBottom: "20px", padding: "16px", backgroundColor: "#f9f9f9", borderRadius: "8px" }}>
            <div style={{ fontSize: "20px", fontWeight: 600 }}>{statusLabel}</div>
            <div style={{ color: "#555", marginTop: "4px" }}>({trip.status || "UNKNOWN"})</div>
            {lastUpdated && (
              <div style={{ fontSize: "12px", color: "#777", marginTop: "6px" }}>
                Updated {lastUpdated.toLocaleTimeString()}
              </div>
            )}
          </div>

          {/* Rider Information */}
          {trip.rider_name && (
            <div style={{ marginBottom: "16px", padding: "12px", backgroundColor: "#f0f8ff", borderRadius: "6px" }}>
              <strong>👤 Rider Information</strong>
              <div style={{ marginTop: "8px", fontSize: "14px" }}>
                <div>Name: {trip.rider_name}</div>
                {trip.rider_phone && <div>Phone: {trip.rider_phone}</div>}
                {trip.rider_rating && <div>Rating: {trip.rider_rating} ⭐</div>}
              </div>
            </div>
          )}

          {/* Pickup Location */}
          {(trip.pickup_lat || trip.pickup_location) && (
            <div style={{ marginBottom: "16px" }}>
              <strong>📍 Pickup Location</strong>
              <div style={{ fontSize: "14px", color: "#555", marginTop: "6px" }}>
                {trip.pickup_location || `${trip.pickup_lat?.toFixed(4)}, ${trip.pickup_lng?.toFixed(4)}`}
              </div>
            </div>
          )}

          {/* Drop Location */}
          {(trip.drop_lat || trip.drop_location) && (
            <div style={{ marginBottom: "16px" }}>
              <strong>📍 Drop Location</strong>
              <div style={{ fontSize: "14px", color: "#555", marginTop: "6px" }}>
                {trip.drop_location || `${trip.drop_lat?.toFixed(4)}, ${trip.drop_lng?.toFixed(4)}`}
              </div>
            </div>
          )}

          {/* Fare Breakdown */}
          {trip.fare_amount && (
            <div style={{ marginBottom: "16px", padding: "12px", backgroundColor: "#f0fff0", borderRadius: "6px" }}>
              <strong>💰 Fare Information</strong>
              <div style={{ marginTop: "8px", fontSize: "14px" }}>
                <div>
                  Total Fare: <strong style={{ fontSize: "18px", color: "#27ae60" }}>${trip.fare_amount.toFixed(2)}</strong>
                </div>
                {trip.distance && <div>Distance: {trip.distance.toFixed(2)} km</div>}
                {trip.duration && <div>Duration: {Math.round(trip.duration)} minutes</div>}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div style={{ marginTop: "24px", display: "flex", gap: "10px", flexDirection: "column" }}>
            {trip.status === "ASSIGNED" && (
              <button
                onClick={handleStartTrip}
                disabled={actionLoading === "start"}
                style={{
                  padding: "12px",
                  backgroundColor: actionLoading === "start" ? "#ccc" : "#2196F3",
                  color: "white",
                  border: "none",
                  borderRadius: "6px",
                  cursor: actionLoading === "start" ? "not-allowed" : "pointer",
                  fontSize: "16px",
                  fontWeight: "600",
                }}
              >
                {actionLoading === "start" ? "Starting..." : "Start Trip"}
              </button>
            )}

            {(trip.status === "ON_TRIP" || trip.status === "PICKED_UP") && (
              <button
                onClick={handleCompleteTrip}
                disabled={actionLoading === "complete"}
                style={{
                  padding: "12px",
                  backgroundColor: actionLoading === "complete" ? "#ccc" : "#27ae60",
                  color: "white",
                  border: "none",
                  borderRadius: "6px",
                  cursor: actionLoading === "complete" ? "not-allowed" : "pointer",
                  fontSize: "16px",
                  fontWeight: "600",
                }}
              >
                {actionLoading === "complete" ? "Completing..." : "Complete Trip"}
              </button>
            )}

            {!FINAL_STATUSES.includes(trip.status) && (
              <button
                onClick={handleCancelTrip}
                style={{
                  padding: "12px",
                  backgroundColor: "#f44336",
                  color: "white",
                  border: "none",
                  borderRadius: "6px",
                  cursor: "pointer",
                  fontSize: "16px",
                  fontWeight: "600",
                }}
              >
                Cancel Trip
              </button>
            )}

            <button
              onClick={handleBack}
              style={{
                padding: "12px",
                backgroundColor: "#666",
                color: "white",
                border: "none",
                borderRadius: "6px",
                cursor: "pointer",
                fontSize: "16px",
              }}
            >
              Back to Dashboard
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default DriverTripDetail;
