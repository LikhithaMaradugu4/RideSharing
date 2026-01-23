import api from "./axios";

// ============ TENANT MANAGEMENT ============
// Fetch available tenants for driver application
export const getAvailableTenantsApi = async () => {
  const res = await api.get("/drivers/tenants");
  return res.data;
};

// ============ TRIP MANAGEMENT ============
// Fetch available trip offers for driver
export const getDriverTripOffersApi = async () => {
  const res = await api.get("/drivers/trips/offers");
  return res.data;
};

// Accept a trip offer
export const acceptTripApi = async (tripId) => {
  const res = await api.post(`/drivers/trips/${tripId}/accept`);
  return res.data;
};

// Start a trip
export const startTripApi = async (tripId) => {
  const res = await api.post(`/drivers/trips/${tripId}/start`);
  return res.data;
};

// Complete a trip
export const completeTripApi = async (tripId) => {
  const res = await api.post(`/drivers/trips/${tripId}/complete`);
  return res.data;
};

// Get trip details
export const getTripDetailsApi = async (tripId) => {
  const res = await api.get(`/trips/${tripId}`);
  return res.data;
};

// ============ DRIVER PROFILE & APPLICATION ============
// Get driver profile
export const getDriverProfileApi = async () => {
  const res = await api.get("/drivers/me");
  return res.data;
};

// Submit driver application to tenant
export const submitDriverApplicationApi = async (tenantId, driverType) => {
  const res = await api.post("/drivers/apply", {
    tenant_id: tenantId,
    driver_type: driverType,
  });
  return res.data;
};

// ============ SHIFT MANAGEMENT ============
// Start driver shift
export const startShiftApi = async () => {
  const res = await api.post("/drivers/shift/start");
  return res.data;
};

// End driver shift
export const endShiftApi = async () => {
  const res = await api.post("/drivers/shift/end");
  return res.data;
};

// ============ LOCATION UPDATES ============
// Update driver location
export const updateLocationApi = async (latitude, longitude) => {
  const res = await api.post("/drivers/location", {
    latitude,
    longitude,
  });
  return res.data;
};
