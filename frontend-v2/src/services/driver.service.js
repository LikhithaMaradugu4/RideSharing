/**
 * Driver Service - For driver-specific operations
 */

const API_BASE_URL = 'http://localhost:8000/api/v2';

const driverService = {
  /**
   * Get all tenants (for tenant selection during application)
   */
  getTenants: async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/driver/tenants`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch tenants');
      }

      const data = await response.json();
      return data.tenants || data;
    } catch (error) {
      console.error('Error fetching tenants:', error);
      throw error;
    }
  },

  /**
   * Get current driver profile
   */
  getMyProfile: async (token) => {
    try {
      const response = await fetch(`${API_BASE_URL}/driver/me`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        if (response.status === 404) {
          return null; // No driver profile
        }
        const error = await response.json();
        throw new Error(error.detail || 'Failed to fetch driver profile');
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching driver profile:', error);
      throw error;
    }
  },

  /**
   * Apply for driver capability with documents
   * multipart/form-data with files
   */
  applyWithDocuments: async (token, formData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/driver/apply-with-documents`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to submit driver application');
      }

      return await response.json();
    } catch (error) {
      console.error('Error submitting driver application:', error);
      throw error;
    }
  },

  /**
   * Start shift (online)
   */
  startShift: async (token) => {
    try {
      const response = await fetch(`${API_BASE_URL}/driver/availability/online`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to start shift');
      }

      return await response.json();
    } catch (error) {
      console.error('Error starting shift:', error);
      throw error;
    }
  },

  /**
   * End shift (offline)
   */
  endShift: async (token) => {
    try {
      const response = await fetch(`${API_BASE_URL}/driver/availability/offline`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to end shift');
      }

      return await response.json();
    } catch (error) {
      console.error('Error ending shift:', error);
      throw error;
    }
  },

  /**
   * Get active shift status
   */
  getActiveShift: async (token) => {
    try {
      const response = await fetch(`${API_BASE_URL}/driver/shift/active`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        if (response.status === 404) {
          return null; // No active shift
        }
        const error = await response.json();
        throw new Error(error.detail || 'Failed to fetch shift status');
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching shift status:', error);
      throw error;
    }
  },

  /**
   * Get pending dispatches
   */
  getPendingDispatches: async (token) => {
    try {
      const response = await fetch(`${API_BASE_URL}/driver/dispatches/pending`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to fetch pending dispatches');
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching pending dispatches:', error);
      throw error;
    }
  },

  /**
   * Accept a dispatch
   */
  acceptDispatch: async (token, dispatchId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/driver/dispatches/${dispatchId}/accept`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to accept dispatch');
      }

      return await response.json();
    } catch (error) {
      console.error('Error accepting dispatch:', error);
      throw error;
    }
  },

  /**
   * Reject a dispatch
   */
  rejectDispatch: async (token, dispatchId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/driver/dispatches/${dispatchId}/reject`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to reject dispatch');
      }

      return await response.json();
    } catch (error) {
      console.error('Error rejecting dispatch:', error);
      throw error;
    }
  },

  /**
   * Get driver vehicles
   */
  getVehicles: async (token) => {
    try {
      const response = await fetch(`${API_BASE_URL}/vehicles`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to fetch vehicles');
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching vehicles:', error);
      throw error;
    }
  },

  /**
   * Add a vehicle
   */
  createVehicle: async (token, vehicleData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/vehicles`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(vehicleData)
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to create vehicle');
      }

      return await response.json();
    } catch (error) {
      console.error('Error creating vehicle:', error);
      throw error;
    }
  },

  /**
   * Add vehicle specs
   */
  addVehicleSpec: async (token, vehicleId, specData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/vehicles/${vehicleId}/spec`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(specData)
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to add vehicle spec');
      }

      return await response.json();
    } catch (error) {
      console.error('Error adding vehicle spec:', error);
      throw error;
    }
  },

  /**
   * Upload vehicle documents
   */
  uploadVehicleDocuments: async (token, vehicleId, formData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/vehicles/${vehicleId}/documents`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to upload documents');
      }

      return await response.json();
    } catch (error) {
      console.error('Error uploading documents:', error);
      throw error;
    }
  },

  /**
   * Upload vehicle photos
   */
  uploadVehiclePhotos: async (token, vehicleId, formData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/vehicles/${vehicleId}/photos`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to upload photos');
      }

      return await response.json();
    } catch (error) {
      console.error('Error uploading photos:', error);
      throw error;
    }
  },

  /**
   * Discover fleets
   */
  discoverFleets: async (token, params) => {
    try {
      const qs = params ? new URLSearchParams({
        city_id: params.cityId ? String(params.cityId) : undefined,
        tenant_id: params.tenantId ? String(params.tenantId) : undefined
      }) : null;
      const url = qs ? `${API_BASE_URL}/fleets/discover?${qs.toString()}` : `${API_BASE_URL}/fleets/discover`;
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to discover fleets');
      }

      return await response.json();
    } catch (error) {
      console.error('Error discovering fleets:', error);
      throw error;
    }
  },

  /**
   * Get fleet invites
   */
  getFleetInvites: async (token) => {
    try {
      const response = await fetch(`${API_BASE_URL}/driver/fleet-invites`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to fetch fleet invites');
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching fleet invites:', error);
      throw error;
    }
  },

  /**
   * Accept fleet invite
   */
  acceptFleetInvite: async (token, fleetId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/driver/fleet-invites/${fleetId}/accept`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to accept fleet invite');
      }

      return await response.json();
    } catch (error) {
      console.error('Error accepting fleet invite:', error);
      throw error;
    }
  },

  /**
   * Reject fleet invite
   */
  rejectFleetInvite: async (token, fleetId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/driver/fleet-invites/${fleetId}/reject`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to reject fleet invite');
      }

      return await response.json();
    } catch (error) {
      console.error('Error rejecting fleet invite:', error);
      throw error;
    }
  },

  /**
   * Set work availability
   */
  setWorkAvailability: async (token, availabilityData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/driver/work-availability`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(availabilityData)
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to set work availability');
      }

      return await response.json();
    } catch (error) {
      console.error('Error setting work availability:', error);
      throw error;
    }
  },

  /**
   * Get work availability
   */
  getWorkAvailability: async (token) => {
    try {
      const response = await fetch(`${API_BASE_URL}/driver/work-availability`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to fetch work availability');
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching work availability:', error);
      throw error;
    }
  },

  /**
   * Update work availability
   */
  updateWorkAvailability: async (token, availabilityData) => {
    try {
      // Map to backend schema: { date, is_available, note }
      const payload = {
        date: availabilityData.date,
        is_available: availabilityData.is_available,
        note: availabilityData.note ?? availabilityData.notes ?? null
      };
      const response = await fetch(`${API_BASE_URL}/driver/work-availability`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to update work availability');
      }

      return await response.json();
    } catch (error) {
      console.error('Error updating work availability:', error);
      throw error;
    }
  },

  /**
   * Delete work availability for a date
   */
  deleteWorkAvailability: async (token, date) => {
    // Backend doesn't support DELETE; mark as unavailable instead
    return driverService.updateWorkAvailability(token, { date, is_available: false, note: null });
  },

  /**
   * Get my vehicles (wrapper for getVehicles)
   */
  getMyVehicles: async (token) => {
    return driverService.getVehicles(token);
  },

  /**
   * Add vehicle (wrapper that supports multipart FormData)
   */
  addVehicle: async (token, formData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/vehicles`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to add vehicle');
      }

      return await response.json();
    } catch (error) {
      console.error('Error adding vehicle:', error);
      throw error;
    }
  },

  /**
   * Update vehicle
   */
  updateVehicle: async (token, vehicleId, updateData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/vehicles/${vehicleId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(updateData)
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to update vehicle');
      }

      return await response.json();
    } catch (error) {
      console.error('Error updating vehicle:', error);
      throw error;
    }
  },

  /**
   * Remove vehicle
   */
  removeVehicle: async (token, vehicleId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/vehicles/${vehicleId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to remove vehicle');
      }

      return { success: true };
    } catch (error) {
      console.error('Error removing vehicle:', error);
      throw error;
    }
  }
};

export default driverService;
