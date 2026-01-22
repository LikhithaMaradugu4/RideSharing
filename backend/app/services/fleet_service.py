from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.fleet import Fleet, FleetDocument, DriverProfile
from app.models.identity import AppUser
from app.schemas.fleet import FleetApplyRequest


class FleetService:

    @staticmethod
    def apply_fleet(
        db: Session,
        user: AppUser,
        data: FleetApplyRequest
    ):
        # BUSINESS fleet only - INDIVIDUAL fleets are auto-created for approved drivers
        if data.fleet_type != "BUSINESS":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only BUSINESS fleet type can be applied for. INDIVIDUAL fleets are auto-created."
            )

        # Optional policy: Reject if user already has APPROVED driver_profile
        existing_driver = (
            db.query(DriverProfile)
            .filter(
                DriverProfile.driver_id == user.user_id,
                DriverProfile.approval_status == "APPROVED"
            )
            .first()
        )
        
        if existing_driver:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Approved drivers cannot apply as BUSINESS fleet owners"
            )

        # Check if user already owns a fleet
        existing_fleet = (
            db.query(Fleet)
            .filter(Fleet.owner_user_id == user.user_id)
            .first()
        )

        if existing_fleet:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You already have a fleet application"
            )

        # Validate documents before creating fleet
        ALLOWED_DOCUMENT_TYPES = {
            "AADHAAR", "PAN", 
            "COMPANY_REGISTRATION", "BUSINESS_PAN", "GST_CERTIFICATE", "SIGNED_AGREEMENT"
        }
        
        if not data.documents:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one identity document (AADHAAR or PAN) is required"
            )
        
        doc_types_provided = [doc.document_type for doc in data.documents]
        
        # Check for unknown document types
        unknown_types = set(doc_types_provided) - ALLOWED_DOCUMENT_TYPES
        if unknown_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown document types: {', '.join(unknown_types)}"
            )
        
        # Enforce mandatory identity documents: at least ONE of AADHAAR or PAN
        has_aadhaar = "AADHAAR" in doc_types_provided
        has_pan = "PAN" in doc_types_provided
        
        if not (has_aadhaar or has_pan):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one identity document (AADHAAR or PAN) is required"
            )

        # Create new BUSINESS fleet with PENDING approval
        fleet = Fleet(
            owner_user_id=user.user_id,
            tenant_id=data.tenant_id,
            fleet_name=data.fleet_name,
            fleet_type="BUSINESS",
            approval_status="PENDING",
            status="ACTIVE",
            created_by=user.user_id
        )

        db.add(fleet)
        db.flush()

        # Store fleet documents (all PENDING verification)
        fleet_docs = [
            FleetDocument(
                fleet_id=fleet.fleet_id,
                document_type=doc.document_type,
                file_url=doc.file_url,
                verification_status="PENDING",
                created_by=user.user_id
            )
            for doc in data.documents
        ]

        db.add_all(fleet_docs)
        db.commit()
        db.refresh(fleet)

        return fleet

    @staticmethod
    def get_my_fleet(db: Session, user: AppUser):
        fleet = (
            db.query(Fleet)
            .filter(Fleet.owner_user_id == user.user_id)
            .first()
        )

        if not fleet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fleet not found. Apply first."
            )

        return fleet
