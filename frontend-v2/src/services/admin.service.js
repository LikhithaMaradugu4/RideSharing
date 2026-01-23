const API_BASE_URL = 'http://localhost:8000/api/admin';

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
  listTenants: async () => {
    const response = await fetch(`${API_BASE_URL}/tenants`, {
      credentials: 'include'
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch tenants');
    }
    
    return response.json();
  },

  createTenant: async (tenantData) => {
    const response = await fetch(`${API_BASE_URL}/tenants`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(tenantData)
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create tenant');
    }
    
    return response.json();
  },

  getTenantDetails: async (tenantId) => {
    const response = await fetch(`${API_BASE_URL}/tenants/${tenantId}`, {
      credentials: 'include'
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch tenant details');
    }
    
    return response.json();
  },

  deleteTenant: async (tenantId) => {
    const response = await fetch(`${API_BASE_URL}/tenants/${tenantId}`, {
      method: 'DELETE',
      credentials: 'include'
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to delete tenant');
    }
    
    return true;
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
  }
};

export default adminService;
