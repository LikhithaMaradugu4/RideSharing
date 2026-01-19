import { useEffect, useState } from "react";
import { useParams, useNavigate, useSearchParams } from "react-router-dom";
import { confirmRideRequestApi } from "./api/rideRequests.api";

function ConfirmRide() {
  const { rideRequestId } = useParams();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const tenantId = searchParams.get("tenant_id");
  const vehicleCategory = searchParams.get("vehicle_category") || "AUTO";

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    // Basic guard (frontend-only)
    if (!tenantId) {
      setError("Tenant not selected");
    }
  }, [tenantId]);

  const handleConfirm = async () => {
    setLoading(true);
    setError(null);

    try {
      const result = await confirmRideRequestApi(
        Number(rideRequestId),
        Number(tenantId),
        vehicleCategory
      );
      setSuccess(true);

      // Navigate to trip status screen with returned trip_id
      const tripId = result?.trip_id;
      setTimeout(() => {
        if (tripId) {
          navigate(`/app/trip/${tripId}/status`);
        } else {
          navigate("/app/ride");
        }
      }, 800);

    } catch (err) {
      setError(
        err.response?.data?.detail || "Failed to confirm ride"
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: "500px", margin: "60px auto" }}>
      <h2>Confirm Ride</h2>

      <p><b>Ride Request ID:</b> {rideRequestId}</p>
      <p><b>Tenant ID:</b> {tenantId}</p>
      <p><b>Vehicle Category:</b> {vehicleCategory}</p>

      {error && <div style={{ color: "red" }}>{error}</div>}
      {success && (
        <div style={{ color: "green" }}>
          Ride confirmed! Finding driver...
        </div>
      )}

      {!success && (
        <button
          onClick={handleConfirm}
          disabled={loading || !tenantId}
        >
          {loading ? "Confirming..." : "Confirm Ride"}
        </button>
      )}
    </div>
  );
}

export default ConfirmRide;
