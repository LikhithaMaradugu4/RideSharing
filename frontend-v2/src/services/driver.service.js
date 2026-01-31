/**
 * Driver Service - Driver-facing API helpers for the phase-2 backend.
 */
import authService from './auth.service';

const API_BASE_URL = 'http://localhost:8000/api/v2';

const buildHeaders = (token, contentType = 'application/json') => {
  const baseHeaders = {};
  if (contentType) {
    baseHeaders['Content-Type'] = contentType;
  }
  if (token) {
    baseHeaders['Authorization'] = `Bearer ${token}`;
  }
  return baseHeaders;
};

/**
 * Get a valid token, refreshing if needed
 */
const getValidToken = async (token) => {
  // If token was passed, check if we need to refresh
  if (token) {
    return await authService.getValidToken();
  }
  return null;
};

const parseJson = async (response) => {
  const text = await response.text();
  if (!text) {
    return null;
  }
  try {
    return JSON.parse(text);
  } catch (error) {
    console.error('Failed to parse JSON response', error);
    throw new Error('Invalid response from server');
  }
};

const handleResponse = async (response, defaultMessage) => {
  const data = await parseJson(response);
  if (!response.ok) {
    const message = data?.detail || defaultMessage || 'Request failed';
    const error = new Error(message);
    error.status = response.status;
    error.body = data;
    throw error;
  }
  return data;
};

const driverService = {
  /**
   * Fetch active tenants for driver onboarding.
   */
  getTenants: async () => {
    const response = await fetch(`${API_BASE_URL}/driver/tenants`, {
      method: 'GET',
      headers: buildHeaders(null)
    });

    const data = await handleResponse(response, 'Failed to fetch tenants');
    return data?.tenants ?? [];
  },

  /**
   * Submit driver application with document uploads (multipart/form-data).
   */
  applyWithDocuments: async (token, formData) => {
    const response = await fetch(`${API_BASE_URL}/driver/apply-with-documents`, {
      method: 'POST',
      headers: buildHeaders(token, null),
      body: formData
    });

    return handleResponse(response, 'Failed to submit driver application');
  },

  /**
   * Retrieve the authenticated driver's profile.
   */
  getMyProfile: async (token) => {
    try {
      const validToken = await getValidToken(token);
      const response = await fetch(`${API_BASE_URL}/driver/me`, {
        method: 'GET',
        headers: buildHeaders(validToken)
      });

      const data = await handleResponse(response, 'Failed to fetch driver profile');
      return data;
    } catch (error) {
      if (error.status === 404) {
        return null;
      }
      throw error;
    }
  },

  /**
   * Shift management helpers.
   */
  startShift: async (token) => {
    const validToken = await getValidToken(token);
    const response = await fetch(`${API_BASE_URL}/driver/availability/online`, {
      method: 'POST',
      headers: buildHeaders(validToken)
    });

    return handleResponse(response, 'Failed to start shift');
  },

  endShift: async (token) => {
    const validToken = await getValidToken(token);
    const response = await fetch(`${API_BASE_URL}/driver/availability/offline`, {
      method: 'POST',
      headers: buildHeaders(validToken)
    });

    return handleResponse(response, 'Failed to end shift');
  },

  getActiveShift: async (token) => {
    try {
      const validToken = await getValidToken(token);
      const response = await fetch(`${API_BASE_URL}/driver/shift/active`, {
        method: 'GET',
        headers: buildHeaders(validToken)
      });

      return await handleResponse(response, 'Failed to fetch active shift');
    } catch (error) {
      if (error.status === 404) {
        return null;
      }
      throw error;
    }
  },

  /**
   * Check if driver meets all prerequisites to go online.
   * Returns detailed checklist useful for diagnosing issues.
   */
  checkShiftReadiness: async (token) => {
    const validToken = await getValidToken(token);
    const response = await fetch(`${API_BASE_URL}/driver/shift/readiness`, {
      method: 'GET',
      headers: buildHeaders(validToken)
    });

    return handleResponse(response, 'Failed to check shift readiness');
  },

  /**
   * Dispatch handling.
   */
  getPendingDispatches: async (token) => {
    const validToken = await getValidToken(token);
    const response = await fetch(`${API_BASE_URL}/dispatch/driver/dispatches/pending`, {
      method: 'GET',
      headers: buildHeaders(validToken)
    });

    const data = await handleResponse(response, 'Failed to fetch pending dispatches');
    return data?.pending_dispatches ?? [];
  },

  acceptDispatch: async (token, attemptId) => {
    const validToken = await getValidToken(token);
    const response = await fetch(`${API_BASE_URL}/dispatch/${attemptId}/accept`, {
      method: 'POST',
      headers: buildHeaders(validToken)
    });

    return handleResponse(response, 'Failed to accept dispatch');
  },

  rejectDispatch: async (token, attemptId) => {
    const validToken = await getValidToken(token);
    const response = await fetch(`${API_BASE_URL}/dispatch/${attemptId}/reject`, {
      method: 'POST',
      headers: buildHeaders(validToken)
    });

    return handleResponse(response, 'Failed to reject dispatch');
  },

  /**
   * Vehicle management.
   */
  getVehicles: async (token) => {
    const validToken = await getValidToken(token);
    const response = await fetch(`${API_BASE_URL}/vehicles`, {
      method: 'GET',
      headers: buildHeaders(validToken)
    });

    return handleResponse(response, 'Failed to fetch vehicles');
  },

  getMyVehicles: async (token) => driverService.getVehicles(token),

  /**
   * Get approved vehicles for independent drivers (for vehicle selection).
   */
  getApprovedVehicles: async (token) => {
    const validToken = await getValidToken(token);
    const response = await fetch(`${API_BASE_URL}/vehicles/driver/approved`, {
      method: 'GET',
      headers: buildHeaders(validToken)
    });

    return handleResponse(response, 'Failed to fetch approved vehicles');
  },

  /**
   * Select a vehicle for shift (independent drivers only).
   * @param {string} token - JWT token
   * @param {number} vehicleId - Vehicle ID to select
   * @param {boolean} endShiftIfActive - If true, auto-end any active shift before switching
   */
  selectVehicle: async (token, vehicleId, endShiftIfActive = false) => {
    const validToken = await getValidToken(token);
    const response = await fetch(`${API_BASE_URL}/vehicles/driver/select`, {
      method: 'POST',
      headers: buildHeaders(validToken),
      body: JSON.stringify({ 
        vehicle_id: vehicleId,
        end_shift_if_active: endShiftIfActive
      })
    });

    return handleResponse(response, 'Failed to select vehicle');
  },

  createVehicle: async (token, vehicleData) => {
    const response = await fetch(`${API_BASE_URL}/vehicles`, {
      method: 'POST',
      headers: buildHeaders(token),
      body: JSON.stringify(vehicleData)
    });

    return handleResponse(response, 'Failed to create vehicle');
  },

  addVehicleSpec: async (token, vehicleId, specData) => {
    const response = await fetch(`${API_BASE_URL}/vehicles/${vehicleId}/spec`, {
      method: 'POST',
      headers: buildHeaders(token),
      body: JSON.stringify(specData)
    });

    return handleResponse(response, 'Failed to save vehicle specification');
  },

  uploadVehicleDocument: async (token, vehicleId, documentData) => {
    const response = await fetch(`${API_BASE_URL}/vehicles/${vehicleId}/documents`, {
      method: 'POST',
      headers: buildHeaders(token),
      body: JSON.stringify(documentData)
    });

    return handleResponse(response, 'Failed to upload vehicle document');
  },

  uploadVehiclePhotos: async (token, vehicleId, photoUrls) => {
    const payload = Array.isArray(photoUrls) ? photoUrls : [];
    const response = await fetch(`${API_BASE_URL}/vehicles/${vehicleId}/photos`, {
      method: 'POST',
      headers: buildHeaders(token),
      body: JSON.stringify({ photo_urls: payload })
    });

    return handleResponse(response, 'Failed to upload vehicle photos');
  },

  /**
   * Fleet discovery & invites.
   */
  discoverFleets: async (token, params = {}) => {
    const query = new URLSearchParams();
    if (params.cityId) {
      query.append('city_id', String(params.cityId));
    }
    if (params.tenantId) {
      query.append('tenant_id', String(params.tenantId));
    }

    const url = query.toString() ? `${API_BASE_URL}/fleets/discover?${query.toString()}` : `${API_BASE_URL}/fleets/discover`;

    const response = await fetch(url, {
      method: 'GET',
      headers: buildHeaders(token)
    });

    const data = await handleResponse(response, 'Failed to discover fleets');
    return data?.fleets ?? [];
  },

  getFleetInvites: async (token) => {
    const response = await fetch(`${API_BASE_URL}/driver/fleet-invites`, {
      method: 'GET',
      headers: buildHeaders(token)
    });

    const data = await handleResponse(response, 'Failed to fetch fleet invites');
    return data?.invites ?? [];
  },

  acceptFleetInvite: async (token, fleetId) => {
    const response = await fetch(`${API_BASE_URL}/driver/fleet-invites/${fleetId}/accept`, {
      method: 'POST',
      headers: buildHeaders(token)
    });

    return handleResponse(response, 'Failed to accept fleet invite');
  },

  rejectFleetInvite: async (token, fleetId) => {
    const response = await fetch(`${API_BASE_URL}/driver/fleet-invites/${fleetId}/reject`, {
      method: 'POST',
      headers: buildHeaders(token)
    });

    return handleResponse(response, 'Failed to reject fleet invite');
  },

  /**
   * Driver work availability.
   */
  getWorkAvailability: async (token) => {
    const response = await fetch(`${API_BASE_URL}/driver/work-availability`, {
      method: 'GET',
      headers: buildHeaders(token)
    });

    const data = await handleResponse(response, 'Failed to fetch work availability');
    return data?.records ?? [];
  },

  updateWorkAvailability: async (token, availabilityData) => {
    const payload = {
      date: availabilityData.date,
      is_available: availabilityData.is_available,
      note: availabilityData.note ?? null
    };

    const response = await fetch(`${API_BASE_URL}/driver/work-availability`, {
      method: 'POST',
      headers: buildHeaders(token),
      body: JSON.stringify(payload)
    });

    return handleResponse(response, 'Failed to update work availability');
  },

  setWorkAvailability: async (token, availabilityData) => driverService.updateWorkAvailability(token, availabilityData),

  deleteWorkAvailability: async (token, date) => driverService.updateWorkAvailability(token, {
    date,
    is_available: false,
    note: null
  }),

  // =====================================================
  // Trip Lifecycle Methods (Driver-facing)
  // =====================================================

  /**
   * Get driver's active trip (if any).
   * Returns trip in ASSIGNED, ARRIVED, or PICKED_UP status.
   */
  getActiveTrip: async (token) => {
    const validToken = await getValidToken(token);
    const response = await fetch(`${API_BASE_URL}/dispatch/driver/trips/active`, {
      method: 'GET',
      headers: buildHeaders(validToken)
    });

    const data = await handleResponse(response, 'Failed to fetch active trip');
    return data?.active_trip || null;
  },

  /**
   * Mark driver as arrived at pickup location.
   * Transitions trip from ASSIGNED to ARRIVED.
   */
  markArrived: async (token, tripId) => {
    const validToken = await getValidToken(token);
    const response = await fetch(`${API_BASE_URL}/dispatch/driver/trips/${tripId}/arrive`, {
      method: 'POST',
      headers: buildHeaders(validToken)
    });

    return handleResponse(response, 'Failed to mark arrival');
  },

  /**
   * Verify pickup OTP entered by driver.
   * OTP is shared by rider with driver verbally.
   */
  verifyPickupOTP: async (token, tripId, otp) => {
    const validToken = await getValidToken(token);
    const response = await fetch(`${API_BASE_URL}/dispatch/driver/trips/${tripId}/verify-otp`, {
      method: 'POST',
      headers: buildHeaders(validToken),
      body: JSON.stringify({ otp })
    });

    return handleResponse(response, 'Failed to verify OTP');
  },

  /**
   * Confirm rider pickup.
   * Transitions trip from ARRIVED to PICKED_UP.
   * Requires OTP verification first.
   */
  confirmPickup: async (token, tripId) => {
    const validToken = await getValidToken(token);
    const response = await fetch(`${API_BASE_URL}/dispatch/driver/trips/${tripId}/pickup`, {
      method: 'POST',
      headers: buildHeaders(validToken)
    });

    return handleResponse(response, 'Failed to confirm pickup');
  },

  /**
   * Complete the trip.
   * Transitions trip from PICKED_UP to COMPLETED.
   * Sets driver shift back to ONLINE.
   */
  completeTrip: async (token, tripId) => {
    const validToken = await getValidToken(token);
    const response = await fetch(`${API_BASE_URL}/dispatch/driver/trips/${tripId}/complete`, {
      method: 'POST',
      headers: buildHeaders(validToken)
    });

    return handleResponse(response, 'Failed to complete trip');
  }
};

export default driverService;
