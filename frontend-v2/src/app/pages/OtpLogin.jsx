import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import authService from '../../services/auth.service';
import tokenStorage from '../../services/tokenStorage';
import './OtpLogin.css';

// Simple list of countries - In a real app, this might come from a library or API
const COUNTRIES = [
  { code: 'US', dial_code: '+1', flag: '🇺🇸' },
  { code: 'IN', dial_code: '+91', flag: '🇮🇳' },
  { code: 'GB', dial_code: '+44', flag: '🇬🇧' },
  { code: 'CA', dial_code: '+1', flag: '🇨🇦' },
  { code: 'AU', dial_code: '+61', flag: '🇦🇺' },
  { code: 'DE', dial_code: '+49', flag: '🇩🇪' },
  { code: 'JP', dial_code: '+81', flag: '🇯🇵' },
];

function OtpLogin() {
  const navigate = useNavigate();
  
  // Phone State
  const [countryCode, setCountryCode] = useState('+91');
  const [localPhone, setLocalPhone] = useState('');
  
  // OTP State (Array of 6 strings)
  const [otp, setOtp] = useState(new Array(6).fill(""));
  
  // UI State
  const [step, setStep] = useState('phone'); // 'phone' | 'otp'
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  
  // Refs to control focus movement
  const otpBoxReference = useRef([]);

  // --- Phone Logic ---

  const handleSendOtp = async (e) => {
    e.preventDefault();
    setError('');
    setMessage('');

    // Combine code + number for validation/API
    const fullPhoneNumber = `${countryCode}${localPhone}`;

    if (!/^\+?[0-9]{8,15}$/.test(fullPhoneNumber)) {
      setError('Please enter a valid phone number');
      return;
    }

    try {
      setLoading(true);
      const res = await authService.sendOtp(fullPhoneNumber);
      // Determine masking based on response or local input
      const displayPhone = res.phone_number || fullPhoneNumber;
      setMessage(`OTP sent to ${displayPhone}`);
      // Log full response for debugging and explicitly log OTP when available.
      // Only show OTP in console during development or on localhost to avoid leaking in production.
      const isLocalhost = window && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');
      if (res && res.debug_otp) {
        if (isLocalhost || import.meta.env.DEV) {
          console.log('Debug OTP (for testing):', res.debug_otp);
        }
      }
      setStep('otp');
    } catch (err) {
      setError(err.message || 'Failed to send OTP');
    } finally {
      setLoading(false);
    }
  };

  // --- OTP Logic ---

  const handleOtpChange = (value, index) => {
    let newArr = [...otp];
    newArr[index] = value;
    setOtp(newArr);

    // Move focus to next box if value is entered
    if (value && index < 5) {
      otpBoxReference.current[index + 1].focus();
    }
  };

  const handleBackspaceAndEnter = (e, index) => {
    if (e.key === "Backspace" && !e.target.value && index > 0) {
      // Move to previous box on backspace if current is empty
      otpBoxReference.current[index - 1].focus();
    }
    if (e.key === "Enter" && index === 5) {
        handleVerifyOtp(e);
    }
  };

  const handlePaste = (e) => {
    e.preventDefault();
    const data = e.clipboardData.getData("text");
    // Ensure only numbers and max 6 chars
    const sanitized = data.replace(/\D/g, "").slice(0, 6).split("");
    
    if (sanitized.length > 0) {
        const newOtp = [...otp];
        sanitized.forEach((digit, i) => {
            if (i < 6) newOtp[i] = digit;
        });
        setOtp(newOtp);
        
        // Focus the last filled input
        const focusIndex = Math.min(sanitized.length, 5);
        otpBoxReference.current[focusIndex].focus();
    }
  };

  const handleVerifyOtp = async (e) => {
    e.preventDefault();
    setError('');
    setMessage('');

    const otpString = otp.join("");
    const fullPhoneNumber = `${countryCode}${localPhone}`;

    if (otpString.length !== 6) {
      setError('Please enter the complete 6-digit code');
      return;
    }

    try {
      setLoading(true);
      const res = await authService.verifyOtp(fullPhoneNumber, otpString);

      const role = (res.user?.role || '').toUpperCase();
      if (role === 'ADMIN' || role === 'PLATFORM_ADMIN') {
        setError('Admin accounts must use the admin login');
        return;
      }

      tokenStorage.set('jwt_token', res.access_token);
      tokenStorage.set('refresh_token', res.refresh_token);

      setMessage('Login successful. Redirecting...');
      await Promise.resolve();
      navigate('/app/home');

    } catch (err) {
      setError(err.message || 'Invalid OTP');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="otp-container">
      <div className="otp-card">
        <h1>{step === 'phone' ? 'Welcome Back' : 'Verify Account'}</h1>
        <p className="subtitle">
          {step === 'phone' 
            ? 'Enter your phone number to sign in' 
            : `Enter the code sent to ${countryCode} ${localPhone}`
          }
        </p>

        {message && <div className="message">{message}</div>}
        {error && <div className="error">{error}</div>}

        {step === 'phone' && (
          <form onSubmit={handleSendOtp}>
            <label htmlFor="phone">Phone Number</label>
            
            <div className="phone-input-group">
                <select 
                    className="country-select"
                    value={countryCode}
                    onChange={(e) => setCountryCode(e.target.value)}
                    disabled={loading}
                >
                    {COUNTRIES.map((c) => (
                        <option key={c.code} value={c.dial_code}>
                            {c.flag} {c.dial_code}
                        </option>
                    ))}
                </select>
                <input
                    type="tel"
                    className="phone-input"
                    placeholder="555 000 0000"
                    value={localPhone}
                    onChange={(e) => setLocalPhone(e.target.value.replace(/\D/g, ''))} // Only numbers
                    disabled={loading}
                />
            </div>

            <button type="submit" className="primary" disabled={loading}>
              {loading ? 'Sending Code...' : 'Get OTP'}
            </button>
          </form>
        )}

        {step === 'otp' && (
          <form onSubmit={handleVerifyOtp}>
            <label>Enter 6-digit Code</label>
            
            <div className="otp-input-group">
                {otp.map((digit, index) => (
                    <input
                        key={index}
                        type="text"
                        maxLength={1}
                        value={digit}
                        onChange={(e) => handleOtpChange(e.target.value, index)}
                        onKeyDown={(e) => handleBackspaceAndEnter(e, index)}
                        onPaste={index === 0 ? handlePaste : undefined}
                        ref={(reference) => (otpBoxReference.current[index] = reference)}
                        className={`otp-box ${digit ? 'filled' : ''}`}
                        disabled={loading}
                        inputMode="numeric"
                        autoComplete="one-time-code"
                    />
                ))}
            </div>

            <button type="submit" className="primary" disabled={loading}>
              {loading ? 'Verifying...' : 'Verify & Continue'}
            </button>
            <button 
                type="button" 
                className="link" 
                onClick={() => { setStep('phone'); setOtp(new Array(6).fill("")); setError(''); }} 
                disabled={loading}
            >
              Change phone number
            </button>
          </form>
        )}

        <div className="footnote">By continuing, you agree to our Terms of Service.</div>
      </div>
    </div>
  );
}

export default OtpLogin;