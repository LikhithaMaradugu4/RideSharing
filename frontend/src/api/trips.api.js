import api from "./axios";

// Fetch trip status by ID
export const getTripStatusApi = async (tripId) => {
  const res = await api.get(`/trips/${tripId}`);
  return res.data;
};
