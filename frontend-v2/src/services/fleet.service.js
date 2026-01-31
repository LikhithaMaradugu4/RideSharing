/**
 * Fleet Service - Fleet Owner API helpers
 */
import authService from './auth.service';

const API_BASE_URL = 'http://localhost:8000/api/v2';

const getValidToken = async () => {
  return await authService.getValidToken();
};

const buildHeaders = (token, contentType = 'application/json') => {
  const headers = {};
  if (contentType) {
    headers['Content-Type'] = contentType;
  }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
};

const handleResponse = async (response, defaultMessage) => {
  const text = await response.text();
  let data = null;
  if (text) {
    try {
      data = JSON.parse(text);
    } catch (e) {
      console.error('Failed to parse JSON:', e);
    }
  }
  
  if (!response.ok) {
    const message = data?.detail || defaultMessage || 'Request failed';
    const error = new Error(message);
    error.status = response.status;
    error.body = data;
    throw error;
  }
  return data;
};

const fleetService = {
  // ==================== Fleet Application ====================
  
  /**
   * Apply for fleet owner status
   */
  applyFleet: async (data) => {
    const token = await getValidToken();
    const response = await fetch(`${API_BASE_URL}/fleet/apply`, {
      method: 'POST',
      headers: buildHeaders(token),
      body: JSON.stringify(data)
    });
    return handleResponse(response, 'Failed to apply for fleet');
  },

  /**
   * Get my fleet details
   */
  getMyFleet: async () => {
    const token = await getValidToken();
    const response = await fetch(`${API_BASE_URL}/fleet/my`, {
      method: 'GET',
      headers: buildHeaders(token)
    });
    return handleResponse(response, 'Failed to get fleet details');
  },

  // ==================== Driver Management ====================

  /**
   * Search for a driver by phone number
   */
  searchDriverByPhone: async (phone) => {
    const token = await getValidToken();
    const response = await fetch(`${API_BASE_URL}/fleet/drivers/search?phone=${encodeURIComponent(phone)}`, {
      method: 'GET',
      headers: buildHeaders(token)
    });
    return handleResponse(response, 'Failed to search driver');
  },

  /**
   * Invite a driver to join the fleet
   */
  inviteDriver: async (driverId) => {
    const token = await getValidToken();
    const response = await fetch(`${API_BASE_URL}/fleet/drivers/invite`, {
      method: 'POST',
      headers: buildHeaders(token),
      body: JSON.stringify({ driver_id: driverId })
    });
    return handleResponse(response, 'Failed to invite driver');
  },

  /**
   * List pending invites sent by fleet owner
   */
  listPendingInvites: async () => {
    const token = await getValidToken();
    const response = await fetch(`${API_BASE_URL}/fleet/invites/pending`, {
      method: 'GET',
      headers: buildHeaders(token)
    });
    return handleResponse(response, 'Failed to get pending invites');
  },

  /**
   * List drivers in the fleet
   */
  listDrivers: async () => {
    const token = await getValidToken();
    const response = await fetch(`${API_BASE_URL}/fleet/drivers`, {
      method: 'GET',
      headers: buildHeaders(token)
    });
    return handleResponse(response, 'Failed to list drivers');
  },

  /**
   * Remove a driver from the fleet
   */
  removeDriver: async (driverId) => {
    const token = await getValidToken();
    const response = await fetch(`${API_BASE_URL}/fleet/drivers/${driverId}/remove`, {
      method: 'POST',
      headers: buildHeaders(token)
    });
    return handleResponse(response, 'Failed to remove driver');
  },

  // ==================== Vehicle Management ====================

  /**
   * List vehicles in the fleet
   */
  listVehicles: async () => {
    const token = await getValidToken();
    const response = await fetch(`${API_BASE_URL}/fleet/vehicles`, {
      method: 'GET',
      headers: buildHeaders(token)
    });
    return handleResponse(response, 'Failed to list vehicles');
  },

  /**
   * Add a vehicle to the fleet (uses common vehicle endpoint)
   */
  addVehicle: async (data) => {
    const token = await getValidToken();
    const response = await fetch(`${API_BASE_URL}/vehicles`, {
      method: 'POST',
      headers: buildHeaders(token),
      body: JSON.stringify(data)
    });
    return handleResponse(response, 'Failed to add vehicle');
  },

  // ==================== Assignments ====================

  /**
   * Create driver-vehicle assignment
   */
  createAssignment: async (driverId, vehicleId) => {
    const token = await getValidToken();
    const response = await fetch(`${API_BASE_URL}/fleet/assignments`, {
      method: 'POST',
      headers: buildHeaders(token),
      body: JSON.stringify({ driver_id: driverId, vehicle_id: vehicleId })
    });
    return handleResponse(response, 'Failed to create assignment');
  },

  /**
   * End a driver-vehicle assignment
   */
  endAssignment: async (assignmentId) => {
    const token = await getValidToken();
    const response = await fetch(`${API_BASE_URL}/fleet/assignments/${assignmentId}/end`, {
      method: 'POST',
      headers: buildHeaders(token)
    });
    return handleResponse(response, 'Failed to end assignment');
  },

  /**
   * List active assignments
   */
  listActiveAssignments: async () => {
    const token = await getValidToken();
    const response = await fetch(`${API_BASE_URL}/fleet/assignments/active`, {
      method: 'GET',
      headers: buildHeaders(token)
    });
    return handleResponse(response, 'Failed to list assignments');
  },

  // ==================== Driver Shifts ====================

  /**
   * Start shift for a driver
   */
  startDriverShift: async (driverId) => {
    const token = await getValidToken();
    const response = await fetch(`${API_BASE_URL}/driver-shift/start`, {
      method: 'POST',
      headers: buildHeaders(token),
      body: JSON.stringify({ driver_id: driverId })
    });
    return handleResponse(response, 'Failed to start shift');
  },

  /**
   * End shift for a driver
   */
  endDriverShift: async (driverId) => {
    const token = await getValidToken();
    const response = await fetch(`${API_BASE_URL}/driver-shift/end`, {
      method: 'POST',
      headers: buildHeaders(token),
      body: JSON.stringify({ driver_id: driverId })
    });
    return handleResponse(response, 'Failed to end shift');
  },

  /**
   * Get driver availability list
   */
  getDriversAvailability: async (startDate, endDate) => {
    const token = await getValidToken();
    let url = `${API_BASE_URL}/fleet/drivers/availability`;
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    if (params.toString()) url += '?' + params.toString();
    
    const response = await fetch(url, {
      method: 'GET',
      headers: buildHeaders(token)
    });
    return handleResponse(response, 'Failed to get driver availability');
  },

  // ==================== Trip History ====================

  /**
   * List fleet trips (historical)
   */
  listTrips: async (skip = 0, limit = 50) => {
    const token = await getValidToken();
    const response = await fetch(`${API_BASE_URL}/fleet/trips?skip=${skip}&limit=${limit}`, {
      method: 'GET',
      headers: buildHeaders(token)
    });
    return handleResponse(response, 'Failed to list trips');
  },

  // ==================== Cities ====================

  /**
   * List fleet cities
   */
  listCities: async () => {
    const token = await getValidToken();
    const response = await fetch(`${API_BASE_URL}/fleet/cities`, {
      method: 'GET',
      headers: buildHeaders(token)
    });
    return handleResponse(response, 'Failed to list cities');
  },

  /**
   * Add a city to fleet
   */
  addCity: async (cityId) => {
    const token = await getValidToken();
    const response = await fetch(`${API_BASE_URL}/fleet/cities`, {
      method: 'POST',
      headers: buildHeaders(token),
      body: JSON.stringify({ city_id: cityId })
    });
    return handleResponse(response, 'Failed to add city');
  },

  /**
   * Remove a city from fleet
   */
  removeCity: async (cityId) => {
    const token = await getValidToken();
    const response = await fetch(`${API_BASE_URL}/fleet/cities/${cityId}`, {
      method: 'DELETE',
      headers: buildHeaders(token)
    });
    return handleResponse(response, 'Failed to remove city');
  }
};

export default fleetService;
