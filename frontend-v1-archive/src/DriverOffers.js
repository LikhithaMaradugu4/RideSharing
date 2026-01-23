import { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { getDriverTripOffersApi, acceptTripApi } from "./api/driverTrips.api";

function DriverOffers() {
  const navigate = useNavigate();
  const [offers, setOffers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [accepting, setAccepting] = useState(null);

  const fetchOffers = useCallback(async () => {
    try {
      const data = await getDriverTripOffersApi();
      setOffers(data || []);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load offers");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    let isMounted = true;
    let intervalId = null;

    // Fetch immediately on mount
    (async () => {
      await fetchOffers();
      if (isMounted) {
        // Poll every 5 seconds
        intervalId = setInterval(async () => {
          if (isMounted) {
            await fetchOffers();
          }
        }, 5000);
      }
    })();

    return () => {
      isMounted = false;
      if (intervalId) clearInterval(intervalId);
    };
  }, [fetchOffers]);

  const handleAcceptTrip = async (tripId) => {
    setAccepting(tripId);
    try {
      await acceptTripApi(tripId);
      // Navigate to trip details after successful acceptance
      navigate(`/app/driver/trip/${tripId}`);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to accept trip");
      setAccepting(null);
    }
  };

  return (
    <div style={{ maxWidth: "520px", margin: "20px auto", padding: "20px" }}>
      <h2>Available Trip Offers</h2>

      {loading && <div>Loading offers...</div>}
      {error && <div style={{ color: "red", marginBottom: "16px" }}>{error}</div>}

      {!loading && offers.length === 0 && (
        <div style={{ padding: "20px", backgroundColor: "#f0f0f0", borderRadius: "8px" }}>
          No offers available. Check back soon!
        </div>
      )}

      {!loading && offers.length > 0 && (
        <div>
          {offers.map((offer, index) => (
            <div
              key={offer.trip_id || index}
              style={{
                border: "1px solid #ddd",
                borderRadius: "8px",
                padding: "16px",
                marginBottom: "12px",
                backgroundColor: "#fafafa",
              }}
            >
              <div style={{ marginBottom: "12px" }}>
                <strong>Trip #{offer.trip_id}</strong>
              </div>

              {/* Pickup Location */}
              <div style={{ marginBottom: "8px" }}>
                <strong>📍 Pickup:</strong>
                <div style={{ fontSize: "14px", color: "#555" }}>
                  {offer.pickup_lat && offer.pickup_lng
                    ? `${offer.pickup_lat.toFixed(4)}, ${offer.pickup_lng.toFixed(4)}`
                    : "Location not specified"}
                </div>
              </div>

              {/* Drop Location */}
              <div style={{ marginBottom: "8px" }}>
                <strong>📍 Drop:</strong>
                <div style={{ fontSize: "14px", color: "#555" }}>
                  {offer.drop_lat && offer.drop_lng
                    ? `${offer.drop_lat.toFixed(4)}, ${offer.drop_lng.toFixed(4)}`
                    : "Location not specified"}
                </div>
              </div>

              {/* Fare Amount */}
              <div style={{ marginBottom: "12px" }}>
                <strong>💰 Estimated Fare:</strong>
                <div style={{ fontSize: "18px", color: "#27ae60", fontWeight: "600" }}>
                  ${offer.fare_amount ? offer.fare_amount.toFixed(2) : "N/A"}
                </div>
              </div>

              {/* Vehicle Category */}
              {offer.vehicle_category && (
                <div style={{ marginBottom: "12px", fontSize: "14px", color: "#666" }}>
                  <strong>Vehicle:</strong> {offer.vehicle_category}
                </div>
              )}

              {/* Rider Info (if available) */}
              {offer.rider_name && (
                <div style={{ marginBottom: "12px", fontSize: "14px", color: "#666" }}>
                  <strong>Rider:</strong> {offer.rider_name}
                  {offer.rider_phone && ` • ${offer.rider_phone}`}
                </div>
              )}

              {/* Accept Button */}
              <button
                onClick={() => handleAcceptTrip(offer.trip_id)}
                disabled={accepting === offer.trip_id}
                style={{
                  width: "100%",
                  padding: "10px",
                  backgroundColor: accepting === offer.trip_id ? "#ccc" : "#27ae60",
                  color: "white",
                  border: "none",
                  borderRadius: "6px",
                  cursor: accepting === offer.trip_id ? "not-allowed" : "pointer",
                  fontSize: "16px",
                  fontWeight: "600",
                }}
              >
                {accepting === offer.trip_id ? "Accepting..." : "Accept Trip"}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default DriverOffers;
