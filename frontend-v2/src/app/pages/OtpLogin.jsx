import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import authService from '../../services/auth.service';
import './OtpLogin.css';

function OtpLogin() {
  const navigate = useNavigate();
  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState('');
  const [step, setStep] = useState('phone'); // 'phone' | 'otp'
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const validatePhone = (value) => {
    // Basic validation: must start with + and be digits
    return /^\+?[0-9]{8,15}$/.test(value);
  };

  const handleSendOtp = async (e) => {
    e.preventDefault();
    setError('');
    setMessage('');

    if (!validatePhone(phone)) {
      setError('Enter a valid phone number (e.g., +15555551234)');
      return;
    }

    try {
      setLoading(true);
      const res = await authService.sendOtp(phone);
      setMessage(`OTP sent to ${res.phone_number}`);
      setStep('otp');
    } catch (err) {
      setError(err.message || 'Failed to send OTP');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOtp = async (e) => {
    e.preventDefault();
    setError('');
    setMessage('');

    if (!/^\d{6}$/.test(otp)) {
      setError('Enter the 6-digit OTP');
      return;
    }

    try {
      setLoading(true);
      const res = await authService.verifyOtp(phone, otp);

      // Block admin tokens from user flow
      const role = (res.user?.role || '').toUpperCase();
      if (role === 'ADMIN' || role === 'PLATFORM_ADMIN') {
        setError('Admin accounts must use the admin login');
        return;
      }

      // Store tokens
      localStorage.setItem('jwt_token', res.access_token);
      localStorage.setItem('refresh_token', res.refresh_token);

      // Small UX note and redirect
      setMessage('Login successful. Redirecting...');
      // Use replace to avoid back to OTP
      navigate('/app/home', { replace: true });
    } catch (err) {
      setError(err.message || 'Invalid OTP');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="otp-container">
      <div className="otp-card">
        <h1>OTP Login</h1>
        <p className="subtitle">Enter your phone to receive a one-time code</p>

        {message && <div className="message">{message}</div>}
        {error && <div className="error">{error}</div>}

        {step === 'phone' && (
          <form onSubmit={handleSendOtp}>
            <label htmlFor="phone">Phone Number</label>
            <input
              id="phone"
              type="tel"
              placeholder="+15555551234"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              disabled={loading}
            />
            <button type="submit" className="primary" disabled={loading}>
              {loading ? 'Sending...' : 'Send OTP'}
            </button>
          </form>
        )}

        {step === 'otp' && (
          <form onSubmit={handleVerifyOtp}>
            <label htmlFor="otp">Enter OTP</label>
            <input
              id="otp"
              type="text"
              placeholder="123456"
              value={otp}
              onChange={(e) => setOtp(e.target.value)}
              disabled={loading}
              maxLength={6}
            />
            <button type="submit" className="primary" disabled={loading}>
              {loading ? 'Verifying...' : 'Verify & Continue'}
            </button>
            <button type="button" className="link" onClick={() => setStep('phone')} disabled={loading}>
              Change phone
            </button>
          </form>
        )}

        <div className="footnote">By continuing, you agree to receive your OTP.</div>
      </div>
    </div>
  );
}

export default OtpLogin;
