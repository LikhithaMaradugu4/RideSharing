/**
 * Rider Service - API helpers for rider operations
 */
import authService from './auth.service';

const API_BASE_URL = 'http://localhost:8000/api/v2';

const buildHeaders = (token) => ({
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${token}`
});

/**
 * Get a valid token, refreshing if needed
 */
const getValidToken = async () => {
  return await authService.getValidToken();
};

const handleResponse = async (response, defaultMessage) => {
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    const message = data?.detail || defaultMessage || 'Request failed';
    const error = new Error(message);
    error.status = response.status;
    error.body = data;
    throw error;
  }
  return data;
};

const riderService = {
  /**
   * Validate pickup and drop locations are in a supported city
   */
  validateLocation: async (pickupLat, pickupLng, dropLat, dropLng) => {
    const token = await getValidToken();
    const response = await fetch(`${API_BASE_URL}/trips/validate-location`, {
      method: 'POST',
      headers: buildHeaders(token),
      body: JSON.stringify({
        pickup_lat: pickupLat,
        pickup_lng: pickupLng,
        drop_lat: dropLat,
        drop_lng: dropLng
      })
    });
    return handleResponse(response, 'Location validation failed');
  },

  /**
   * Get fare estimate for all vehicle categories
   */
  getFareEstimate: async (pickupLat, pickupLng, dropLat, dropLng, vehicleCategory) => {
    const token = await getValidToken();
    const response = await fetch(`${API_BASE_URL}/trips/estimate`, {
      method: 'POST',
      headers: buildHeaders(token),
      body: JSON.stringify({
        pickup_lat: pickupLat,
        pickup_lng: pickupLng,
        drop_lat: dropLat,
        drop_lng: dropLng,
        vehicle_category: vehicleCategory
      })
    });
    return handleResponse(response, 'Failed to get fare estimate');
  },

  /**
   * Get fare estimates for multiple vehicle categories
   */
  getAllFareEstimates: async (pickupLat, pickupLng, dropLat, dropLng) => {
    const categories = ['BIKE', 'AUTO', 'SEDAN'];
    const estimates = [];
    
    for (const category of categories) {
      try {
        const estimate = await riderService.getFareEstimate(
          pickupLat, pickupLng, dropLat, dropLng, category
        );
        estimates.push({
          category,
          ...estimate
        });
      } catch (err) {
        console.error(`Failed to get estimate for ${category}:`, err);
        // Skip this category if estimation fails
      }
    }
    
    return estimates;
  },

  /**
   * Create a new trip (book a ride)
   */
  createTrip: async (pickupLat, pickupLng, dropLat, dropLng, vehicleCategory) => {
    const token = await getValidToken();
    const response = await fetch(`${API_BASE_URL}/trips`, {
      method: 'POST',
      headers: buildHeaders(token),
      body: JSON.stringify({
        pickup_lat: pickupLat,
        pickup_lng: pickupLng,
        drop_lat: dropLat,
        drop_lng: dropLng,
        vehicle_category: vehicleCategory
      })
    });
    return handleResponse(response, 'Failed to book ride');
  },

  /**
   * Get trip status
   */
  getTripStatus: async (tripId) => {
    const token = await getValidToken();
    const response = await fetch(`${API_BASE_URL}/trips/${tripId}`, {
      method: 'GET',
      headers: buildHeaders(token)
    });
    return handleResponse(response, 'Failed to get trip status');
  },

  /**
   * Get detailed trip info for rider
   */
  getTripDetails: async (tripId) => {
    const token = await getValidToken();
    const response = await fetch(`${API_BASE_URL}/trips/${tripId}`, {
      method: 'GET',
      headers: buildHeaders(token)
    });
    return handleResponse(response, 'Failed to get trip details');
  },

  /**
   * Cancel a trip
   */
  cancelTrip: async (tripId) => {
    const token = await getValidToken();
    const response = await fetch(`${API_BASE_URL}/trips/${tripId}/cancel`, {
      method: 'POST',
      headers: buildHeaders(token)
    });
    return handleResponse(response, 'Failed to cancel trip');
  },

  /**
   * Generate pickup OTP (called when driver arrives)
   */
  generatePickupOTP: async (tripId) => {
    const token = await getValidToken();
    const response = await fetch(`${API_BASE_URL}/dispatch/rider/trips/${tripId}/generate-otp`, {
      method: 'POST',
      headers: buildHeaders(token)
    });
    return handleResponse(response, 'Failed to generate OTP');
  },

  /**
   * Get rider's active trip (if any)
   */
  getActiveTrip: async () => {
    const token = await getValidToken();
    const response = await fetch(`${API_BASE_URL}/dispatch/rider/active-trip`, {
      method: 'GET',
      headers: buildHeaders(token)
    });
    
    const data = await handleResponse(response, 'Failed to check active trip');
    // Backend returns { active_trip: {...} } or { active_trip: null }
    return data?.active_trip || null;
  }
};

export default riderService;
