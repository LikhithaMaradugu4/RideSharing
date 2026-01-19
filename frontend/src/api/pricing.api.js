import api from "./axios";

export const estimatePricingApi = async (rideRequestId) => {
  const res = await api.post("/pricing/estimate", {
    ride_request_id: rideRequestId,
  });
  return res.data;
};
