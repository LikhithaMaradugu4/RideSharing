"""
Pickup OTP Service - Generate and verify OTP for trip pickup verification.

Flow:
1. Driver arrives at pickup location -> Rider generates OTP (visible on rider's app)
2. Rider shares OTP with driver verbally
3. Driver enters OTP in app -> System verifies
4. On successful verification -> Trip can proceed to PICKED_UP status

Security:
- OTP expires after 5 minutes
- Max 3 attempts per OTP
- OTP is regenerated if expired or max attempts exceeded
"""

import secrets
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.trips import Trip


# OTP Configuration
OTP_LENGTH = 6
OTP_EXPIRY_MINUTES = 5
MAX_OTP_ATTEMPTS = 3


class PickupOTPService:
    """Service for pickup OTP generation and verification."""

    @staticmethod
    def generate_otp() -> str:
        """
        Generate a cryptographically secure 6-digit OTP.
        
        Returns:
            6-digit numeric string
        """
        return ''.join(secrets.choice('0123456789') for _ in range(OTP_LENGTH))

    @staticmethod
    def generate_pickup_otp(db: Session, trip_id: int) -> dict:
        """
        Generate a new pickup OTP for a trip.
        
        This is called when the driver arrives at pickup (ARRIVED status).
        The OTP is shown to the rider who shares it with the driver.
        
        Args:
            db: Database session
            trip_id: Trip ID
        
        Returns:
            dict with trip_id, otp, and expires_at
        
        Raises:
            HTTPException 404: Trip not found
            HTTPException 400: Trip not in ARRIVED status
        """
        trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()
        
        if not trip:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trip not found"
            )
        
        # OTP can only be generated when driver has ARRIVED at pickup
        if trip.status != "ARRIVED":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"OTP can only be generated when trip status is ARRIVED. Current: {trip.status}"
            )
        
        # Generate new OTP
        otp = PickupOTPService.generate_otp()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRY_MINUTES)
        
        # Update trip with OTP
        trip.pickup_otp = otp
        trip.pickup_otp_expires_at = expires_at
        trip.pickup_otp_attempts = 0
        trip.pickup_otp_verified_at = None
        
        db.commit()
        
        return {
            "trip_id": trip_id,
            "otp": otp,
            "expires_at": expires_at.isoformat()
        }

    @staticmethod
    def verify_pickup_otp(db: Session, trip_id: int, entered_otp: str) -> dict:
        """
        Verify the pickup OTP entered by the driver.
        
        Args:
            db: Database session
            trip_id: Trip ID
            entered_otp: OTP entered by driver
        
        Returns:
            dict with trip_id, verified (bool), and message
        
        Raises:
            HTTPException 404: Trip not found
            HTTPException 400: OTP expired, max attempts exceeded, or invalid status
        """
        trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()
        
        if not trip:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trip not found"
            )
        
        # Check trip status
        if trip.status != "ARRIVED":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"OTP verification only allowed when trip status is ARRIVED. Current: {trip.status}"
            )
        
        # Check if OTP exists
        if not trip.pickup_otp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No OTP generated for this trip. Rider must generate OTP first."
            )
        
        # Check if OTP is expired
        now = datetime.now(timezone.utc)
        if trip.pickup_otp_expires_at and trip.pickup_otp_expires_at < now:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP has expired. Rider must generate a new OTP."
            )
        
        # Check attempt count
        if trip.pickup_otp_attempts >= MAX_OTP_ATTEMPTS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximum OTP attempts ({MAX_OTP_ATTEMPTS}) exceeded. Rider must generate a new OTP."
            )
        
        # Increment attempt count
        trip.pickup_otp_attempts = (trip.pickup_otp_attempts or 0) + 1
        
        # Verify OTP
        if entered_otp == trip.pickup_otp:
            trip.pickup_otp_verified_at = now
            db.commit()
            
            return {
                "trip_id": trip_id,
                "verified": True,
                "message": "OTP verified successfully. Trip pickup confirmed."
            }
        else:
            db.commit()
            remaining = MAX_OTP_ATTEMPTS - trip.pickup_otp_attempts
            
            return {
                "trip_id": trip_id,
                "verified": False,
                "message": f"Invalid OTP. {remaining} attempt(s) remaining."
            }

    @staticmethod
    def is_otp_verified(db: Session, trip_id: int) -> bool:
        """
        Check if pickup OTP has been verified for a trip.
        
        Args:
            db: Database session
            trip_id: Trip ID
        
        Returns:
            True if OTP is verified, False otherwise
        """
        trip = db.query(Trip).filter(Trip.trip_id == trip_id).first()
        
        if not trip:
            return False
        
        return trip.pickup_otp_verified_at is not None
