import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { submitDriverApplicationApi, getAvailableTenantsApi } from "./api/driverTrips.api";

function DriverApplicationForm() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    tenantId: "",
    driverType: "INDEPENDENT",
  });
  const [tenants, setTenants] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [loadingTenants, setLoadingTenants] = useState(true);

  // Fetch available tenants on component mount
  useEffect(() => {
    const fetchTenants = async () => {
      try {
        const data = await getAvailableTenantsApi();
        setTenants(data);
      } catch (err) {
        setError(err.response?.data?.detail || "Failed to load tenants");
      } finally {
        setLoadingTenants(false);
      }
    };

    fetchTenants();
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      if (!formData.tenantId) {
        setError("Please select a tenant");
        setLoading(false);
        return;
      }

      await submitDriverApplicationApi(parseInt(formData.tenantId), formData.driverType);
      setSuccess(true);
      setTimeout(() => {
        navigate("/app/driver/profile");
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to submit application");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: "520px", margin: "60px auto", padding: "20px", border: "1px solid #ddd", borderRadius: "8px" }}>
      <h2>Apply as Driver</h2>

      {error && <div style={{ padding: "12px", backgroundColor: "#ffebee", color: "#c62828", borderRadius: "4px", marginBottom: "16px" }}>{error}</div>}
      {success && <div style={{ padding: "12px", backgroundColor: "#e8f5e9", color: "#2e7d32", borderRadius: "4px", marginBottom: "16px" }}>Application submitted successfully! Redirecting...</div>}

      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
        {/* Tenant Selection */}
        <div>
          <label style={{ display: "block", fontWeight: "600", marginBottom: "6px" }}>Select Tenant</label>
          {loadingTenants ? (
            <div style={{ padding: "10px", color: "#666" }}>Loading tenants...</div>
          ) : (
            <select
              name="tenantId"
              value={formData.tenantId}
              onChange={handleInputChange}
              style={{
                width: "100%",
                padding: "10px",
                border: "1px solid #ccc",
                borderRadius: "4px",
                fontSize: "16px",
                fontFamily: "inherit",
              }}
            >
              <option value="">-- Choose Tenant --</option>
              {tenants.map((tenant) => (
                <option key={tenant.tenant_id} value={tenant.tenant_id}>
                  {tenant.name}
                </option>
              ))}
            </select>
          )}
        </div>

        {/* Driver Type */}
        <div>
          <label style={{ display: "block", fontWeight: "600", marginBottom: "6px" }}>Driver Type</label>
          <div style={{ display: "flex", gap: "16px" }}>
            <label style={{ display: "flex", alignItems: "center", gap: "6px" }}>
              <input
                type="radio"
                name="driverType"
                value="INDEPENDENT"
                checked={formData.driverType === "INDEPENDENT"}
                onChange={handleInputChange}
              />
              Independent
            </label>
            <label style={{ display: "flex", alignItems: "center", gap: "6px" }}>
              <input
                type="radio"
                name="driverType"
                value="FLEET"
                checked={formData.driverType === "FLEET"}
                onChange={handleInputChange}
              />
              Fleet
            </label>
          </div>
        </div>

        {/* Info Text */}
        <div style={{ fontSize: "14px", color: "#666", backgroundColor: "#f5f5f5", padding: "12px", borderRadius: "4px" }}>
          <strong>Note:</strong> You'll be able to add vehicle details and documents after application approval.
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading || loadingTenants}
          style={{
            padding: "12px",
            backgroundColor: loading || loadingTenants ? "#ccc" : "#27ae60",
            color: "white",
            border: "none",
            borderRadius: "4px",
            fontSize: "16px",
            fontWeight: "600",
            cursor: loading || loadingTenants ? "not-allowed" : "pointer",
          }}
        >
          {loading ? "Submitting..." : "Submit Application"}
        </button>

        {/* Back Button */}
        <button
          type="button"
          onClick={() => navigate(-1)}
          style={{
            padding: "10px",
            backgroundColor: "#666",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
            fontSize: "14px",
          }}
        >
          Back
        </button>
      </form>
    </div>
  );
}

export default DriverApplicationForm;
