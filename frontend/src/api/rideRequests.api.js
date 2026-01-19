import api from "./axios";

// Create a ride request using the shared API client (with session header)
export const createRideRequestApi = async (payload) => {
  const res = await api.post("/ride-requests", payload);
  return res.data;
};

// Confirm ride request with selected tenant and vehicle category
export const confirmRideRequestApi = async (
  rideRequestId,
  tenantId,
  vehicleCategory
) => {
  const res = await api.post(`/ride-requests/${rideRequestId}/confirm`, {
    tenant_id: tenantId,
    vehicle_category: vehicleCategory,
  });
  return res.data;
};
