/**
 * User Service - For normal (OTP-authenticated) users
 */
import authService from './auth.service';

// const API_BASE_URL = 'http://localhost:8000/api/v2';// const API_BASE_URL = 'http://localhost:8000/api/v2';
const API_BASE_URL = 'http://192.168.1.241:8000/api/v2'; // Local network IP for testing on mobile
//const API_BASE_URL = 'http://lo:8000/api/v2'; // Default API base URL

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
