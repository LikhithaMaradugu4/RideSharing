import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createRideRequestApi } from "./api/rideRequests.api";

function CreateRide() {
  const navigate = useNavigate();

  const [pickupLat, setPickupLat] = useState("");
  const [pickupLng, setPickupLng] = useState("");
  const [dropLat, setDropLat] = useState("");
  const [dropLng, setDropLng] = useState("");
  const [cityId, setCityId] = useState("");


  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const data = await createRideRequestApi({
        pickup_lat: Number(pickupLat),
        pickup_lng: Number(pickupLng),
        drop_lat: Number(dropLat),
        drop_lng: Number(dropLng),
        city_id: Number(cityId),
      });

      // data.request_id = ride_request_id - navigate to pricing comparison
      navigate(`/app/ride/${data.request_id}/pricing`);
    } catch (err) {
      let message = "Failed to create ride request";

      if (err.response?.data) {
        const data = err.response.data;
        if (typeof data === "string") {
          message = data;
        } else if (data.detail) {
          // detail might be a list or string
          message = Array.isArray(data.detail)
            ? data.detail.map((d) => d.msg || JSON.stringify(d)).join(", ")
            : data.detail;
        } else {
          message = JSON.stringify(data);
        }
      }

      setError(message);

    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: "500px", margin: "50px auto" }}>
      <h2>Create Ride Request</h2>

      <form onSubmit={handleSubmit}>
        <h4>Pickup Location</h4>
        <input
          type="number"
          step="any"
          placeholder="Pickup Latitude"
          value={pickupLat}
          onChange={(e) => setPickupLat(e.target.value)}
          required
        />
        <br />
        <input
          type="number"
          step="any"
          placeholder="Pickup Longitude"
          value={pickupLng}
          onChange={(e) => setPickupLng(e.target.value)}
          required
        />

        <h4>Drop Location</h4>
        <input
          type="number"
          step="any"
          placeholder="Drop Latitude"
          value={dropLat}
          onChange={(e) => setDropLat(e.target.value)}
          required
        />
        <br />
        <input
          type="number"
          step="any"
          placeholder="Drop Longitude"
          value={dropLng}
          onChange={(e) => setDropLng(e.target.value)}
          required
        />
        <h4>City</h4>
        <input
          type="number"
          placeholder="City ID"
          value={cityId}
          onChange={(e) => setCityId(e.target.value)}
          required
        />


        <br /><br />

        {error && <div style={{ color: "red" }}>{error}</div>}

        <button type="submit" disabled={loading}>
          {loading ? "Creating..." : "Create Ride"}
        </button>
      </form>
    </div>
  );
}

export default CreateRide;
