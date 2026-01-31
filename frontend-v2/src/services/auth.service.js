// OTP Auth Service for Phase-2 JWT
const API_BASE_URL = 'http://localhost:8000/api/v2/auth';

const authService = {
  sendOtp: async (phoneNumber) => {
    const res = await fetch(`${API_BASE_URL}/send-otp`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone_number: phoneNumber })
    });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || 'Failed to send OTP');
    }
    return data; // { message, phone_number }
  },

  verifyOtp: async (phoneNumber, otpCode) => {
    const res = await fetch(`${API_BASE_URL}/verify-otp`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone_number: phoneNumber, otp_code: otpCode })
    });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || 'Invalid OTP');
    }
    return data; // { access_token, refresh_token, expires_in, user }
  },

  /**
   * Refresh the access token using the stored refresh token
   */
  refreshToken: async () => {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const res = await fetch(`${API_BASE_URL}/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken })
    });
    const data = await res.json();
    if (!res.ok) {
      // If refresh token is invalid, clear tokens and redirect to login
      localStorage.removeItem('jwt_token');
      localStorage.removeItem('refresh_token');
      throw new Error(data.detail || 'Session expired. Please login again.');
    }
    
    // Store new access token
    localStorage.setItem('jwt_token', data.access_token);
    return data.access_token;
  },

  /**
   * Check if token is about to expire (within 2 minutes)
   */
  isTokenExpiringSoon: () => {
    const token = localStorage.getItem('jwt_token');
    if (!token) return true;
    
    try {
      // Decode JWT payload (base64)
      const payload = JSON.parse(atob(token.split('.')[1]));
      const exp = payload.exp;
      const now = Math.floor(Date.now() / 1000);
      // Return true if expires within 2 minutes
      return (exp - now) < 120;
    } catch (e) {
      return true;
    }
  },

  /**
   * Ensure we have a valid token, refreshing if needed
   */
  getValidToken: async () => {
    if (authService.isTokenExpiringSoon()) {
      try {
        return await authService.refreshToken();
      } catch (e) {
        // Refresh failed, return current token (might fail on API call)
        return localStorage.getItem('jwt_token');
      }
    }
    return localStorage.getItem('jwt_token');
  }
};

export default authService;
