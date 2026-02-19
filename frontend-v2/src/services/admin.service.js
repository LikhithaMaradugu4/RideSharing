import tokenStorage from './tokenStorage';

//const API_BASE_URL = 'http://192.168.1.241:8000/api/admin';
//const PLATFORM_BASE_URL = 'http://192.168.1.241:8000/api/v2/platform-admin';
//const USER_AUTH_BASE_URL = 'http://192.168.1.241:8000/auth';
//const PLATFORM_SESSION_KEY = 'platform_session_id';

const API_BASE_URL = 'http://192.168.1.43:8000/api/admin';
const PLATFORM_BASE_URL = 'http://192.168.1.43:8000/api/v2/platform-admin';
const USER_AUTH_BASE_URL = 'http://192.168.1.43:8000/auth';
const PLATFORM_SESSION_KEY = 'platform_session_id';

// Safety guard: Prevent admin API calls outside /admin routes
const isAdminPath = () => window.location.pathname.startsWith('/admin');

const adminService = {
  // Authentication
  login: async (email, password) => {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ email, password })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }
    
    return response.json();
  },

  // Platform (Phase-1) Session Authentication for v2 Platform Admin endpoints
  platformLogin: async (email, password) => {
    const response = await fetch(`${USER_AUTH_BASE_URL}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Platform login failed');
    }

    const data = await response.json();
    // Store session_id for X-Session-Id header usage
    if (data.session_id) {
      try {
        tokenStorage.set(PLATFORM_SESSION_KEY, data.session_id);
      } catch {}
    }
    return data;
  },

  getPlatformSessionId: () => {
    try {
      return tokenStorage.get(PLATFORM_SESSION_KEY);
    } catch {
      return null;
    }
  },

  clearPlatformSession: () => {
    try {
      tokenStorage.remove(PLATFORM_SESSION_KEY);
    } catch {}
  },

  getCurrentAdmin: async () => {
    // Safety guard: Only allow admin API calls on /admin routes
    if (!isAdminPath()) {
      console.warn('[adminService] getCurrentAdmin blocked: Not on /admin route');
      return null;
    }

    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      credentials: 'include'
    });
    
    if (!response.ok) {
      throw new Error('Not authenticated');
    }
    
    return response.json();
  },

  logout: async () => {
    const response = await fetch(`${API_BASE_URL}/auth/logout`, {
      method: 'POST',
      credentials: 'include'
    });
    
    if (!response.ok) {
      throw new Error('Logout failed');
    }
    
    return response.json();
  },

  // Tenant Management
  // Platform Admin - Tenants (v2)
  platformListTenants: async () => {
    const sessionId = adminService.getPlatformSessionId();
    const response = await fetch(`${PLATFORM_BASE_URL}/tenants`, {
      headers: sessionId ? { 'X-Session-Id': sessionId } : {},
      credentials: 'include'
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch tenants');
    }
    const data = await response.json();
    return data.tenants || [];
  },

  platformCreateTenant: async (tenantData) => {
    const sessionId = adminService.getPlatformSessionId();
    const response = await fetch(`${PLATFORM_BASE_URL}/tenants`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...(sessionId ? { 'X-Session-Id': sessionId } : {}) },
      credentials: 'include',
      body: JSON.stringify(tenantData)
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create tenant');
    }
    return response.json();
  },

  platformGetTenantDetails: async (tenantId) => {
    const sessionId = adminService.getPlatformSessionId();
    const response = await fetch(`${PLATFORM_BASE_URL}/tenants/${tenantId}`, {
      headers: sessionId ? { 'X-Session-Id': sessionId } : {},
      credentials: 'include'
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch tenant details');
    }
    return response.json();
  },

  platformUpdateTenantStatus: async (tenantId, status) => {
    const sessionId = adminService.getPlatformSessionId();
    const response = await fetch(`${PLATFORM_BASE_URL}/tenants/${tenantId}/status`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json', ...(sessionId ? { 'X-Session-Id': sessionId } : {}) },
      credentials: 'include',
      body: JSON.stringify({ status })
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update status');
    }
    return response.json();
  },

  platformAssignTenantAdmin: async (tenantId, { user_id, is_primary }) => {
    const sessionId = adminService.getPlatformSessionId();
    const response = await fetch(`${PLATFORM_BASE_URL}/tenants/${tenantId}/admins`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...(sessionId ? { 'X-Session-Id': sessionId } : {}) },
      credentials: 'include',
      body: JSON.stringify({ user_id, is_primary: !!is_primary })
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to assign tenant admin');
    }
    return response.json();
  },

  platformListTenantDocuments: async (tenantId) => {
    const sessionId = adminService.getPlatformSessionId();
    const response = await fetch(`${PLATFORM_BASE_URL}/tenants/${tenantId}/documents`, {
      headers: sessionId ? { 'X-Session-Id': sessionId } : {},
      credentials: 'include'
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch documents');
    }
    const data = await response.json();
    return data.documents || [];
  },

  platformUploadTenantDocument: async (tenantId, payload) => {
    const sessionId = adminService.getPlatformSessionId();
    const response = await fetch(`${PLATFORM_BASE_URL}/tenants/${tenantId}/documents`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...(sessionId ? { 'X-Session-Id': sessionId } : {}) },
      credentials: 'include',
      body: JSON.stringify(payload)
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to upload document');
    }
    return response.json();
  },

  platformGetTenantDocument: async (tenantId, documentId) => {
    const sessionId = adminService.getPlatformSessionId();
    const response = await fetch(`${PLATFORM_BASE_URL}/tenants/${tenantId}/documents/${documentId}`, {
      headers: sessionId ? { 'X-Session-Id': sessionId } : {},
      credentials: 'include'
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch document');
    }
    return response.json();
  },

  // Tenant Admin Management
  createTenantAdmin: async (tenantId, adminData) => {
    const response = await fetch(`${API_BASE_URL}/tenants/${tenantId}/admins`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(adminData)
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create tenant admin');
    }
    
    return response.json();
  },

  getTenantAdmin: async (tenantId) => {
    const response = await fetch(`${API_BASE_URL}/tenants/${tenantId}/admins`, {
      credentials: 'include'
    });
    
    if (!response.ok) {
      if (response.status === 404) {
        return null;
      }
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch tenant admin');
    }
    
    return response.json();
  },

  // Tenant Documents
  listTenantDocuments: async (tenantId) => {
    const response = await fetch(`${API_BASE_URL}/tenants/${tenantId}/documents`, {
      credentials: 'include'
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch documents');
    }
    
    return response.json();
  },

  uploadTenantDocument: async (tenantId, documentType, file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(
      `${API_BASE_URL}/tenants/${tenantId}/documents?document_type=${encodeURIComponent(documentType)}`,
      {
        method: 'POST',
        credentials: 'include',
        body: formData
      }
    );
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to upload document');
    }
    
    return response.json();
  },

  downloadTenantDocument: async (tenantId, documentId) => {
    const response = await fetch(
      `${API_BASE_URL}/tenants/${tenantId}/documents/${documentId}/download`,
      {
        credentials: 'include'
      }
    );
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to download document');
    }
    
    const blob = await response.blob();
    const contentDisposition = response.headers.get('content-disposition');
    let filename = 'download';
    
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
      if (filenameMatch) {
        filename = filenameMatch[1];
      }
    }
    
    return { blob, filename };
  },

  deleteTenantDocument: async (tenantId, documentId) => {
    const response = await fetch(
      `${API_BASE_URL}/tenants/${tenantId}/documents/${documentId}`,
      {
        method: 'DELETE',
        credentials: 'include'
      }
    );
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to delete document');
    }
    
    return true;
  },

  // Driver Management (Tenant Admin)
  getPendingDrivers: async () => {
    const response = await fetch(`${API_BASE_URL}/drivers/pending`, {
      credentials: 'include'
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch pending drivers');
    }
    
    const data = await response.json();
    return Array.isArray(data) ? data : data.drivers || [];
  },

  getAllDrivers: async () => {
    const response = await fetch(`${API_BASE_URL}/drivers`, {
      credentials: 'include'
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch drivers');
    }
    
    const data = await response.json();
    return Array.isArray(data) ? data : data.drivers || [];
  },

  approveDriver: async (driverId, data) => {
    const response = await fetch(`${API_BASE_URL}/drivers/${driverId}/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(data)
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to approve driver');
    }
    
    return response.json();
  },

  rejectDriver: async (driverId, data) => {
    const response = await fetch(`${API_BASE_URL}/drivers/${driverId}/reject`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(data)
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to reject driver');
    }
    
    return response.json();
  },

  getDriverDocuments: async (driverId) => {
    const response = await fetch(`${API_BASE_URL}/drivers/${driverId}/documents`, {
      credentials: 'include'
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch driver documents');
    }
    
    return response.json();
  },

  /**
   * Get detailed driver documents with rejection info and review capability.
   */
  getDriverDocumentsDetailed: async (driverId) => {
    const response = await fetch(`${API_BASE_URL}/drivers/${driverId}/documents/detailed`, {
      credentials: 'include'
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch driver documents');
    }
    
    return response.json();
  },

  /**
   * Review (approve/reject) an individual driver document.
   * @param {number} driverId - Driver ID
   * @param {number} documentId - Document ID
   * @param {object} data - { status: 'APPROVED' | 'REJECTED', rejection_reason?: string }
   */
  reviewDriverDocument: async (driverId, documentId, data) => {
    const response = await fetch(`${API_BASE_URL}/drivers/${driverId}/documents/${documentId}/review`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(data)
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to review document');
    }
    
    return response.json();
  },

  // Fleet Management (Tenant Admin)
  getPendingFleets: async () => {
    const response = await fetch(`${API_BASE_URL}/fleets/pending`, {
      credentials: 'include'
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch pending fleets');
    }
    
    const data = await response.json();
    return Array.isArray(data) ? data : data.fleets || [];
  },

  getAllFleets: async () => {
    const response = await fetch(`${API_BASE_URL}/fleets`, {
      credentials: 'include'
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch fleets');
    }
    
    const data = await response.json();
    return Array.isArray(data) ? data : data.fleets || [];
  },

  approveFleet: async (fleetId) => {
    const response = await fetch(`${API_BASE_URL}/fleets/${fleetId}/approve`, {
      method: 'POST',
      credentials: 'include'
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to approve fleet');
    }
    
    return response.json();
  },

  rejectFleet: async (fleetId, data) => {
    const response = await fetch(`${API_BASE_URL}/fleets/${fleetId}/reject`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(data)
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to reject fleet');
    }
    
    return response.json();
  },

  getFleetDocumentsDetailed: async (fleetId) => {
    const response = await fetch(`${API_BASE_URL}/fleets/${fleetId}/documents/detailed`, {
      credentials: 'include'
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch fleet documents');
    }

    return response.json();
  },

  reviewFleetDocument: async (fleetId, documentId, data) => {
    const response = await fetch(`${API_BASE_URL}/fleets/${fleetId}/documents/${documentId}/review`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to review fleet document');
    }

    return response.json();
  },

  // Vehicle Management (Tenant Admin)
  getPendingVehicles: async () => {
    const response = await fetch(`${API_BASE_URL}/vehicles/pending-approval`, {
      credentials: 'include'
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch pending vehicles');
    }

    const data = await response.json();
    // Backend returns a direct array
    return Array.isArray(data) ? data : data.pending_vehicles || [];
  },getVehicleDocuments: async (vehicleId) => {
  const response = await fetch(
    `${API_BASE_URL}/vehicles/${vehicleId}/documents`,
    {
      credentials: 'include'
    }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch vehicle documents');
  }

  return response.json();
},
approveOrRejectVehicle: async (vehicleId, data) => {
  const response = await fetch(
    `${API_BASE_URL}/vehicles/${vehicleId}/approve`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(data)
    }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to update vehicle status');
  }

  return response.json();
},

  getAllVehicles: async () => {
    const response = await fetch(
      `${API_BASE_URL}/vehicles`,
      {
        credentials: 'include'
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch vehicles');
    }

    const data = await response.json();
    // Backend returns a direct array
    return Array.isArray(data) ? data : data.vehicles || [];
  },

  // Get approved vehicles only
  getApprovedVehicles: async () => {
    const response = await fetch(
      `${API_BASE_URL}/vehicles/approved`,
      {
        credentials: 'include'
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch approved vehicles');
    }

    const data = await response.json();
    return Array.isArray(data) ? data : data.vehicles || [];
  },

  // Update driver approval status
  updateDriverStatus: async (driverId, approvalStatus) => {
    const response = await fetch(
      `${API_BASE_URL}/drivers/${driverId}/status`,
      {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ approval_status: approvalStatus })
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update driver status');
    }

    return response.json();
  },

  // Update fleet approval status
  updateFleetStatus: async (fleetId, approvalStatus) => {
    const response = await fetch(
      `${API_BASE_URL}/fleets/${fleetId}/status`,
      {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ approval_status: approvalStatus })
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update fleet status');
    }

    return response.json();
  },

  // Update vehicle approval status
  updateVehicleStatus: async (vehicleId, approvalStatus) => {
    const response = await fetch(
      `${API_BASE_URL}/vehicles/${vehicleId}/status`,
      {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ approval_status: approvalStatus })
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update vehicle status');
    }

    return response.json();
  },

  // Get driver details with fleet assignment
  getDriverDetails: async (driverId) => {
    const response = await fetch(
      `${API_BASE_URL}/drivers/${driverId}/details`,
      {
        credentials: 'include'
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch driver details');
    }

    return response.json();
  },

  // ==================== Operating Regions ====================

  // Get all available countries
  getAllCountries: async () => {
    const response = await fetch(
      `${API_BASE_URL}/operating-regions/countries/all`,
      {
        credentials: 'include'
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch countries');
    }

    const data = await response.json();
    return data.countries || [];
  },

  // Get all available cities
  getAllCities: async (countryCode = null) => {
    let url = `${API_BASE_URL}/operating-regions/cities/all`;
    if (countryCode) {
      url += `?country_code=${countryCode}`;
    }

    const response = await fetch(url, {
      credentials: 'include'
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch cities');
    }

    const data = await response.json();
    return data.cities || [];
  },
  //Get All available cities 
  getAvailableCountries : async () => {
    const response = await fetch(
      `${API_BASE_URL}/operating-regions/countries/all`,
      {
        credentials: 'include'
      }
    );

      if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch tenant countries');
    }

    const data = await response.json();
    return data.countries || [];
  },

  // Get all available cities for a specific country
  getAvailableCities: async (countryCode) => {
    let url = `${API_BASE_URL}/operating-regions/cities/all`;
    if (countryCode) {
      url += `?country_code=${encodeURIComponent(countryCode)}`;
    }

    const response = await fetch(url, {
      credentials: 'include'
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch available cities');
    }

    const data = await response.json();
    return data.cities || [];
  },

  // Get tenant operating countries
  getTenantCountries: async () => {
    const response = await fetch(
      `${API_BASE_URL}/operating-regions/countries`,
      {
        credentials: 'include'
      }
      
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch tenant countries');
    }

    const data = await response.json();
    return data.countries || [];
  },

  // Add country to tenant
  addTenantCountry: async (countryCode) => {
    const response = await fetch(
      `${API_BASE_URL}/operating-regions/countries`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ country_code: countryCode })
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to add country');
    }

    return response.json();
  },

  // Remove country from tenant
  removeTenantCountry: async (countryCode) => {
    const response = await fetch(
      `${API_BASE_URL}/operating-regions/countries/${countryCode}`,
      {
        method: 'DELETE',
        credentials: 'include'
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to remove country');
    }

    return response.json();
  },

  // Get tenant operating cities
  getTenantCities: async () => {
    const response = await fetch(
      `${API_BASE_URL}/operating-regions/cities`,
      {
        credentials: 'include'
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch tenant cities');
    }

    const data = await response.json();
    return data.cities || [];
  },

  // Add city to tenant
  addTenantCity: async (cityId) => {
    const response = await fetch(
      `${API_BASE_URL}/operating-regions/cities`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ city_id: cityId })
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to add city');
    }

    return response.json();
  },

  // Remove city from tenant
  removeTenantCity: async (cityId) => {
    const response = await fetch(
      `${API_BASE_URL}/operating-regions/cities/${cityId}`,
      {
        method: 'DELETE',
        credentials: 'include'
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to remove city');
    }

    return response.json();
  },

  // ==================== PLATFORM SETTINGS: COUNTRIES ====================

  platformListCountries: async () => {
    const sessionId = adminService.getPlatformSessionId();
    const response = await fetch(`${PLATFORM_BASE_URL}/countries`, {
      headers: sessionId ? { 'X-Session-Id': sessionId } : {},
      credentials: 'include'
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch countries');
    }
    return response.json();
  },

  platformCreateCountry: async (data) => {
    const sessionId = adminService.getPlatformSessionId();
    const response = await fetch(`${PLATFORM_BASE_URL}/countries`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(sessionId ? { 'X-Session-Id': sessionId } : {})
      },
      credentials: 'include',
      body: JSON.stringify(data)
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create country');
    }
    return response.json();
  },

  platformUpdateCountry: async (countryCode, data) => {
    const sessionId = adminService.getPlatformSessionId();
    const response = await fetch(`${PLATFORM_BASE_URL}/countries/${countryCode}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...(sessionId ? { 'X-Session-Id': sessionId } : {})
      },
      credentials: 'include',
      body: JSON.stringify(data)
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update country');
    }
    return response.json();
  },

  // ==================== PLATFORM SETTINGS: CITIES ====================

  platformListCities: async (countryCode = null) => {
    const sessionId = adminService.getPlatformSessionId();
    const params = countryCode ? `?country_code=${countryCode}` : '';
    const response = await fetch(`${PLATFORM_BASE_URL}/cities${params}`, {
      headers: sessionId ? { 'X-Session-Id': sessionId } : {},
      credentials: 'include'
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch cities');
    }
    return response.json();
  },

  platformCreateCity: async (data) => {
    const sessionId = adminService.getPlatformSessionId();
    const response = await fetch(`${PLATFORM_BASE_URL}/cities`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(sessionId ? { 'X-Session-Id': sessionId } : {})
      },
      credentials: 'include',
      body: JSON.stringify(data)
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create city');
    }
    return response.json();
  },

  platformUpdateCity: async (cityId, data) => {
    const sessionId = adminService.getPlatformSessionId();
    const response = await fetch(`${PLATFORM_BASE_URL}/cities/${cityId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...(sessionId ? { 'X-Session-Id': sessionId } : {})
      },
      credentials: 'include',
      body: JSON.stringify(data)
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update city');
    }
    return response.json();
  },

  // ==================== PLATFORM SETTINGS: FARE CONFIG ====================

  platformListFareConfigs: async (cityId = null, vehicleCategory = null) => {
    const sessionId = adminService.getPlatformSessionId();
    const params = new URLSearchParams();
    if (cityId) params.append('city_id', cityId);
    if (vehicleCategory) params.append('vehicle_category', vehicleCategory);
    const qs = params.toString() ? `?${params.toString()}` : '';
    const response = await fetch(`${PLATFORM_BASE_URL}/fare-config${qs}`, {
      headers: sessionId ? { 'X-Session-Id': sessionId } : {},
      credentials: 'include'
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch fare configs');
    }
    return response.json();
  },

  platformCreateFareConfig: async (data) => {
    const sessionId = adminService.getPlatformSessionId();
    const response = await fetch(`${PLATFORM_BASE_URL}/fare-config`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(sessionId ? { 'X-Session-Id': sessionId } : {})
      },
      credentials: 'include',
      body: JSON.stringify(data)
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create fare config');
    }
    return response.json();
  },

  platformDeactivateFareConfig: async (fareConfigId) => {
    const sessionId = adminService.getPlatformSessionId();
    const response = await fetch(`${PLATFORM_BASE_URL}/fare-config/${fareConfigId}/deactivate`, {
      method: 'PUT',
      headers: sessionId ? { 'X-Session-Id': sessionId } : {},
      credentials: 'include'
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to deactivate fare config');
    }
    return response.json();
  },

  // ==================== PLATFORM SETTINGS: COMMISSION CONFIG ====================

  platformListCommissionConfigs: async (cityId = null, vehicleCategory = null) => {
    const sessionId = adminService.getPlatformSessionId();
    const params = new URLSearchParams();
    if (cityId) params.append('city_id', cityId);
    if (vehicleCategory) params.append('vehicle_category', vehicleCategory);
    const qs = params.toString() ? `?${params.toString()}` : '';
    const response = await fetch(`${PLATFORM_BASE_URL}/commission-config${qs}`, {
      headers: sessionId ? { 'X-Session-Id': sessionId } : {},
      credentials: 'include'
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch commission configs');
    }
    return response.json();
  },

  platformCreateCommissionConfig: async (data) => {
    const sessionId = adminService.getPlatformSessionId();
    const response = await fetch(`${PLATFORM_BASE_URL}/commission-config`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(sessionId ? { 'X-Session-Id': sessionId } : {})
      },
      credentials: 'include',
      body: JSON.stringify(data)
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create commission config');
    }
    return response.json();
  },

  platformDeactivateCommissionConfig: async (configId) => {
    const sessionId = adminService.getPlatformSessionId();
    const response = await fetch(`${PLATFORM_BASE_URL}/commission-config/${configId}/deactivate`, {
      method: 'PUT',
      headers: sessionId ? { 'X-Session-Id': sessionId } : {},
      credentials: 'include'
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to deactivate commission config');
    }
    return response.json();
  },

  platformUpdateFareConfig: async (fareConfigId, data) => {
    const sessionId = adminService.getPlatformSessionId();
    const response = await fetch(`${PLATFORM_BASE_URL}/fare-config/${fareConfigId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...(sessionId ? { 'X-Session-Id': sessionId } : {})
      },
      credentials: 'include',
      body: JSON.stringify(data)
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update fare config');
    }
    return response.json();
  },

  platformUpdateCommissionConfig: async (configId, data) => {
    const sessionId = adminService.getPlatformSessionId();
    const response = await fetch(`${PLATFORM_BASE_URL}/commission-config/${configId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...(sessionId ? { 'X-Session-Id': sessionId } : {})
      },
      credentials: 'include',
      body: JSON.stringify(data)
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update commission config');
    }
    return response.json();
  },

  // ==================== SURGE ZONE MANAGEMENT ====================

  surgeListZones: async (cityId = null) => {
    const params = cityId ? `?city_id=${cityId}` : '';
    const response = await fetch(`${API_BASE_URL}/surge-zones/${params}`, {
      credentials: 'include'
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch surge zones');
    }
    return response.json();
  },

  surgeGetZone: async (zoneId) => {
    const response = await fetch(`${API_BASE_URL}/surge-zones/${zoneId}`, {
      credentials: 'include'
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch surge zone');
    }
    return response.json();
  },

  surgeCreateZone: async (data) => {
    const response = await fetch(`${API_BASE_URL}/surge-zones/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(data)
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create surge zone');
    }
    return response.json();
  },

  surgeUpdateZone: async (zoneId, data) => {
    const response = await fetch(`${API_BASE_URL}/surge-zones/${zoneId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(data)
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update surge zone');
    }
    return response.json();
  },

  surgeActivateZone: async (zoneId, activate = true) => {
    const response = await fetch(`${API_BASE_URL}/surge-zones/${zoneId}/activate?activate=${activate}`, {
      method: 'PATCH',
      credentials: 'include'
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update surge zone status');
    }
    return response.json();
  },

  surgeDeleteZone: async (zoneId) => {
    const response = await fetch(`${API_BASE_URL}/surge-zones/${zoneId}`, {
      method: 'DELETE',
      credentials: 'include'
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to delete surge zone');
    }
    return response.json();
  },
};



export default adminService;
