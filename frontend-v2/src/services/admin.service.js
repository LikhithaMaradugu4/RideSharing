const API_BASE_URL = 'http://localhost:8000/api/admin';
const PLATFORM_BASE_URL = 'http://localhost:8000/api/v2/platform-admin';
const USER_AUTH_BASE_URL = 'http://localhost:8000/auth';
const PLATFORM_SESSION_KEY = 'platform_session_id';

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
        localStorage.setItem(PLATFORM_SESSION_KEY, data.session_id);
      } catch {}
    }
    return data;
  },

  getPlatformSessionId: () => {
    try {
      return localStorage.getItem(PLATFORM_SESSION_KEY);
    } catch {
      return null;
    }
  },

  clearPlatformSession: () => {
    try {
      localStorage.removeItem(PLATFORM_SESSION_KEY);
    } catch {}
  },

  getCurrentAdmin: async () => {
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
    
    return response.json();
  },

  getAllDrivers: async () => {
    const response = await fetch(`${API_BASE_URL}/drivers`, {
      credentials: 'include'
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch drivers');
    }
    
    return response.json();
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

  // Fleet Management (Tenant Admin)
  getPendingFleets: async () => {
    const response = await fetch(`${API_BASE_URL}/fleets/pending`, {
      credentials: 'include'
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch pending fleets');
    }
    
    return response.json();
  },

  getAllFleets: async () => {
    const response = await fetch(`${API_BASE_URL}/fleets`, {
      credentials: 'include'
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch fleets');
    }
    
    return response.json();
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
  }
};

export default adminService;
