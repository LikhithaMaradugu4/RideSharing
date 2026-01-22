from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.fleet import DriverProfile
from app.models.identity import AppUser, UserKYC
from app.schemas.driver import DriverApplyWithDocumentsRequest


class DriverService:

    @staticmethod
    def apply_with_documents(
        db: Session,
        user: AppUser,
        data: DriverApplyWithDocumentsRequest
    ):
        # Prevent duplicate application
        existing = (
            db.query(DriverProfile)
            .filter(DriverProfile.driver_id == user.user_id)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Driver application already exists"
            )

        # Validate mandatory documents: Driving License required; Aadhaar or PAN required
        if not data.driving_license_number or not data.driving_license_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Driving License number and URL are required"
            )

        has_aadhaar = bool(data.aadhaar_number and data.aadhaar_url)
        has_pan = bool(data.pan_number and data.pan_url)

        if not (has_aadhaar or has_pan):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one government ID (Aadhaar or PAN) is required"
            )

        # Create driver profile (capability)
        driver_profile = DriverProfile(
            driver_id=user.user_id,
            tenant_id=data.tenant_id,
            driver_type=data.driver_type,
            approval_status="PENDING",
            rating=5.00,
            alternate_phone_number=data.alternate_phone_number,
            created_by=user.user_id
        )
        db.add(driver_profile)
        db.flush()  # ensure FK safety

        # Mandatory KYC documents
        kyc_records = [
            UserKYC(
                user_id=user.user_id,
                document_type="DRIVING_LICENSE",
                document_number=data.driving_license_number,
                file_url=data.driving_license_url,
                verification_status="PENDING",
                created_by=user.user_id
            )
        ]

        if has_aadhaar:
            kyc_records.append(
                UserKYC(
                    user_id=user.user_id,
                    document_type="AADHAAR",
                    document_number=data.aadhaar_number,
                    file_url=data.aadhaar_url,
                    verification_status="PENDING",
                    created_by=user.user_id
                )
            )

        if has_pan:
            kyc_records.append(
                UserKYC(
                    user_id=user.user_id,
                    document_type="PAN",
                    document_number=data.pan_number,
                    file_url=data.pan_url,
                    verification_status="PENDING",
                    created_by=user.user_id
                )
            )

        # PHOTO is optional but if provided, insert with empty number allowed
        if data.passport_photo_url:
            kyc_records.append(
                UserKYC(
                    user_id=user.user_id,
                    document_type="PHOTO",
                    document_number="",
                    file_url=data.passport_photo_url,
                    verification_status="PENDING",
                    created_by=user.user_id
                )
            )

        db.add_all(kyc_records)
        db.commit()
        db.refresh(driver_profile)

        return driver_profile

    @staticmethod
    def get_my_profile(db: Session, user: AppUser):
        profile = (
            db.query(DriverProfile)
            .filter(DriverProfile.driver_id == user.user_id)
            .first()
        )

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver profile not found. Apply first."
            )

        return profile
