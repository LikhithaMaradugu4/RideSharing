"""
Redis key definitions - ONE place for all key formats
Prevents typos, ensures consistency across the app
"""

# OTP Keys
OTP_KEY = "otp:{phone}"  # Format: otp:+919876543210
OTP_ATTEMPTS_KEY = "otp:attempts:{phone}"  # Format: otp:attempts:+919876543210
OTP_LOCKOUT_KEY = "otp:lockout:{phone}"  # Format: otp:lockout:+919876543210

# JWT Blacklist Keys
JWT_BLACKLIST_KEY = "jwt:blacklist:{jti}"  # Format: jwt:blacklist:abc123xyz
JWT_REFRESH_TOKEN_KEY = "jwt:refresh:{jti}"  # Format: jwt:refresh:xyz789abc

# Driver Location Keys
DRIVER_LOCATION_KEY = "driver:location:{driver_id}"  # Format: driver:location:5
DRIVERS_IN_CITY_KEY = "drivers:city:{city_id}"  # Format: drivers:city:1

# Driver Shift Keys
DRIVER_SHIFT_KEY = "driver:shift:{driver_id}"  # Format: driver:shift:5
ACTIVE_SHIFTS_KEY = "shifts:active:{tenant_id}"  # Format: shifts:active:2

# Session Keys
SESSION_KEY = "session:{session_id}"  # Format: session:abc123xyz

# Driver Availability (for dispatch)
AVAILABLE_DRIVERS_KEY = "drivers:available:{city_id}"  # Format: drivers:available:1
DRIVER_AVAILABILITY_KEY = "driver:available:{driver_id}"  # Format: driver:available:5


#Ride Request Keys
RIDE_REQUEST_KEY = "ride:request:{ride_id}"  # Format: ride:request:12
PENDING_RIDES_KEY = "rides:pending:{city_id}"  # Format: rides:pending:1

# Rate Limiting Keys
RATE_LIMIT_KEY = "ratelimit:{endpoint}:{user_id}"  # Format: ratelimit:/pricing/estimate:7

# Driver GEO Key (for Redis GEO operations - GEOADD/GEORADIUS)
DRIVERS_GEO_KEY = "drivers:geo"  # Single key for all driver locations


def format_key(template: str, **kwargs) -> str:
    """
    Format a Redis key template with values
    
    Example:
        format_key(OTP_KEY, phone="+919876543210")
        → "otp:+919876543210"
    """
    return template.format(**kwargs)
