import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getTripDetailsApi } from "./api/driverTrips.api";
import DriverOffers from "./DriverOffers";
import DriverTripDetail from "./DriverTripDetail";

function DriverDashboard() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState("offers");
  const [activeTrip, setActiveTrip] = useState(null);
  const [loadingTrip, setLoadingTrip] = useState(false);
  const [error, setError] = useState(null);

  // Check for active trip on mount
  useEffect(() => {
    const checkActiveTrip = async () => {
      try {
        setLoadingTrip(true);
        // TODO: This would require a backend endpoint to get driver's active trip
        // For now, we'll rely on manual navigation or localStorage
        const savedActiveTrip = localStorage.getItem("driverActiveTrip");
        if (savedActiveTrip) {
          const tripId = JSON.parse(savedActiveTrip);
          const tripData = await getTripDetailsApi(tripId);
          
          // Check if trip is still active (not completed/cancelled)
          if (!["COMPLETED", "CANCELLED"].includes(tripData.status)) {
            setActiveTrip(tripData);
            setActiveTab("current");
          } else {
            localStorage.removeItem("driverActiveTrip");
          }
        }
      } catch (err) {
        console.error("Error checking active trip:", err);
        localStorage.removeItem("driverActiveTrip");
      } finally {
        setLoadingTrip(false);
      }
    };

    checkActiveTrip();
  }, []);

  const tabButtonStyle = (isActive) => ({
    padding: "10px 20px",
    border: "none",
    backgroundColor: isActive ? "#2196F3" : "#ddd",
    color: isActive ? "white" : "black",
    cursor: "pointer",
    fontSize: "16px",
    fontWeight: "600",
    borderRadius: "4px 4px 0 0",
    marginRight: "8px",
  });

  const quickLinkButtonStyle = {
    flex: 1,
    padding: "12px",
    border: "1px solid #ddd",
    backgroundColor: "#f9f9f9",
    borderRadius: "6px",
    cursor: "pointer",
    textAlign: "center",
    fontSize: "14px",
    fontWeight: "600",
    transition: "all 0.3s ease",
  };

  return (
    <div style={{ minHeight: "100vh", backgroundColor: "#f5f5f5" }}>
      {/* Header */}
      <div style={{ backgroundColor: "white", padding: "20px", borderBottom: "1px solid #ddd" }}>
        <h1>Driver Dashboard</h1>
        
        {/* Quick Links */}
        <div style={{ display: "flex", gap: "8px", marginTop: "16px", flexWrap: "wrap" }}>
          <button
            onClick={() => navigate("/app/driver/profile")}
            onMouseOver={(e) => e.target.style.backgroundColor = "#e3f2fd"}
            onMouseOut={(e) => e.target.style.backgroundColor = "#f9f9f9"}
            style={{ ...quickLinkButtonStyle }}
          >
            👤 My Profile
          </button>
          <button
            onClick={() => navigate("/app/driver/shift")}
            onMouseOver={(e) => e.target.style.backgroundColor = "#e3f2fd"}
            onMouseOut={(e) => e.target.style.backgroundColor = "#f9f9f9"}
            style={{ ...quickLinkButtonStyle }}
          >
            ⏱️ Shift Management
          </button>
          <button
            onClick={() => navigate("/app/driver/apply")}
            onMouseOver={(e) => e.target.style.backgroundColor = "#e3f2fd"}
            onMouseOut={(e) => e.target.style.backgroundColor = "#f9f9f9"}
            style={{ ...quickLinkButtonStyle }}
          >
            📝 Apply to Tenant
          </button>
        </div>
      </div>

      {error && (
        <div
          style={{
            margin: "20px",
            padding: "12px",
            backgroundColor: "#ffebee",
            color: "#c62828",
            borderRadius: "4px",
          }}
        >
          {error}
        </div>
      )}

      {/* Tab Navigation */}
      <div style={{ padding: "16px 20px", backgroundColor: "white", borderBottom: "1px solid #ddd" }}>
        <div style={{ display: "flex", gap: "4px" }}>
          <button
            onClick={() => setActiveTab("offers")}
            style={tabButtonStyle(activeTab === "offers")}
          >
            Available Offers
          </button>

          {activeTrip && (
            <button
              onClick={() => setActiveTab("current")}
              style={tabButtonStyle(activeTab === "current")}
            >
              Current Trip ⚡
            </button>
          )}

          <button
            onClick={() => setActiveTab("history")}
            style={tabButtonStyle(activeTab === "history")}
          >
            History
          </button>
        </div>
      </div>

      {/* Tab Content */}
      <div style={{ padding: "20px" }}>
        {activeTab === "offers" && <DriverOffers />}

        {activeTab === "current" && (
          <div style={{ maxWidth: "520px", margin: "0 auto" }}>
            {loadingTrip ? (
              <div>Loading active trip...</div>
            ) : activeTrip ? (
              <DriverTripDetail key={activeTrip.trip_id} />
            ) : (
              <div
                style={{
                  padding: "20px",
                  backgroundColor: "#f0f0f0",
                  borderRadius: "8px",
                  textAlign: "center",
                }}
              >
                <p>No active trip. Check available offers!</p>
                <button
                  onClick={() => setActiveTab("offers")}
                  style={{
                    padding: "10px 20px",
                    backgroundColor: "#2196F3",
                    color: "white",
                    border: "none",
                    borderRadius: "4px",
                    cursor: "pointer",
                    fontSize: "16px",
                  }}
                >
                  View Offers
                </button>
              </div>
            )}
          </div>
        )}

        {activeTab === "history" && (
          <div style={{ maxWidth: "520px", margin: "0 auto", padding: "20px" }}>
            <p>Trip history feature coming soon...</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default DriverDashboard;
