/**
 * User Service - For normal (OTP-authenticated) users
 */
import authService from './auth.service';

const API_BASE_URL = 'http://localhost:8000/api/v2';

const userService = {
  /**
   * Get current user capabilities
   * Backend-driven API that returns user capabilities
   */
  getCapabilities: async (token) => {
    try {
      // Ensure token is valid, refresh if needed
      const validToken = await authService.getValidToken();
      
      const response = await fetch(`${API_BASE_URL}/me/capabilities`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${validToken}`
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
