import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { estimatePricingApi } from "./api/pricing.api";

function PricingComparison() {
  const { rideRequestId } = useParams();
  const navigate = useNavigate();

  const [options, setOptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPricing = async () => {
      try {
        const data = await estimatePricingApi(Number(rideRequestId));
        setOptions(data);
      } catch (err) {
        setError(
          err.response?.data?.detail || "Failed to fetch pricing"
        );
      } finally {
        setLoading(false);
      }
    };

    fetchPricing();
  }, [rideRequestId]);

  const handleSelect = (tenantId, vehicleCategory) => {
    navigate(
      `/app/ride/${rideRequestId}/confirm?tenant_id=${tenantId}&vehicle_category=${vehicleCategory}`
    );
  };

  if (loading) return <div>Loading pricing...</div>;
  if (error) return <div style={{ color: "red" }}>{error}</div>;

  return (
    <div style={{ maxWidth: "600px", margin: "50px auto" }}>
      <h2>Select a Ride Option</h2>

      {options.map((opt) => (
        <div
          key={`${opt.tenant_id}-${opt.vehicle_category}`}
          style={{
            border: "1px solid #ccc",
            padding: "12px",
            marginBottom: "10px",
          }}
        >
          <h4>{opt.tenant_name}</h4>
          <p>Vehicle: {opt.vehicle_category}</p>
          <p>Estimated Fare: ₹{opt.estimated_fare}</p>

          <button onClick={() => handleSelect(opt.tenant_id, opt.vehicle_category)}>
            Select
          </button>
        </div>
      ))}
    </div>
  );
}

export default PricingComparison;
