/**
 * User Service - For normal (OTP-authenticated) users
 */

const API_BASE_URL = 'http://localhost:8000/api/v2';

const userService = {
  /**
   * Get current user capabilities
   * Backend-driven API that returns user capabilities
   */
  getCapabilities: async (token) => {
    try {
      const response = await fetch(`${API_BASE_URL}/me/capabilities`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to fetch capabilities');
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching capabilities:', error);
      throw error;
    }
  }
};

export default userService;
