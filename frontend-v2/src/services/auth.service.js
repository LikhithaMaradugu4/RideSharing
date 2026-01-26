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
  }
};

export default authService;
