"""
Phase-2 JWT authentication schemas
"""

from pydantic import BaseModel


# OTP Request/Response
class SendOTPRequest(BaseModel):
    phone_number: str  # Format: +919876543210


class SendOTPResponse(BaseModel):
    message: str
    phone_number: str


class VerifyOTPRequest(BaseModel):
    phone_number: str
    otp_code: str


class JWTTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # Access token expiry in seconds
    user: dict


# Refresh Token
class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # Access token expiry in seconds


# Logout
class LogoutResponse(BaseModel):
    message: str
