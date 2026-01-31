from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List
from datetime import datetime, timezone

from app.models.vehicle import Vehicle, VehicleSpec, VehicleDocument, DriverVehicleAssignment
from app.models.fleet import Fleet, DriverProfile, FleetDriver
from app.models.operations import DriverShift
from app.models.identity import AppUser
from app.schemas.vehicle import (
    VehicleCreateRequest,
    VehicleSpecCreateRequest,
    VehicleDocumentCreateRequest
)


class VehicleService:

    @staticmethod
    def create_vehicle(
        db: Session,
        user: AppUser,
        data: VehicleCreateRequest
    ):
        # 1. Fetch fleet owned by current user
        fleet = (
            db.query(Fleet)
            .filter(Fleet.owner_user_id == user.user_id)
            .first()
        )

        if not fleet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fleet not found. Apply for fleet first."
            )

        # 2. Check if fleet is approved
        if fleet.approval_status != "APPROVED":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Fleet is not approved yet"
            )

        # 3. INDIVIDUAL fleet type validation
        if fleet.fleet_type == "INDIVIDUAL":
            driver_profile = (
                db.query(DriverProfile)
                .filter(DriverProfile.driver_id == user.user_id)
                .first()
            )

            if not driver_profile:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Driver profile not found"
                )

            if driver_profile.approval_status != "APPROVED":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Driver profile is not approved yet"
                )

            if not driver_profile.allowed_vehicle_categories:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No vehicle categories allowed for this driver"
                )

            if data.category not in driver_profile.allowed_vehicle_categories:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Category {data.category} not allowed for this driver"
                )

        # 4. Validate documents before creating vehicle
        ALLOWED_DOCUMENT_TYPES = {"RC", "INSURANCE", "PERMIT", "FITNESS", "VEHICLE_PHOTO"}
        
        if not data.documents:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vehicle documents are required"
            )
        
        doc_types_provided = [doc.document_type for doc in data.documents]
        
        # Check for unknown document types
        unknown_types = set(doc_types_provided) - ALLOWED_DOCUMENT_TYPES
        if unknown_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown document types: {', '.join(unknown_types)}"
            )
        
        # Enforce mandatory documents
        has_rc = "RC" in doc_types_provided
        has_insurance = "INSURANCE" in doc_types_provided
        has_photo = "VEHICLE_PHOTO" in doc_types_provided
        
        if not (has_rc and has_insurance and has_photo):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="RC, Insurance, and at least one vehicle photo are required"
            )

        # 5. Check registration_no uniqueness
        existing = (
            db.query(Vehicle)
            .filter(Vehicle.registration_no == data.registration_no)
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration number already exists"
            )

        # 6. Create vehicle
        # Vehicle starts as PENDING approval and INACTIVE status
        # Status will be set to ACTIVE when tenant approves
        vehicle = Vehicle(
            tenant_id=fleet.tenant_id,
            fleet_id=fleet.fleet_id,
            category=data.category,
            registration_no=data.registration_no,
            status="PENDING",
            approval_status="PENDING",
            created_by=user.user_id
        )

        db.add(vehicle)
        db.flush()

        # 7. Insert vehicle documents (only after validation)
        vehicle_docs = [
            VehicleDocument(
                vehicle_id=vehicle.vehicle_id,
                document_type=doc.document_type,
                file_url=doc.file_url,
                verification_status="PENDING",
                created_by=user.user_id
            )
            for doc in data.documents
        ]
        
        db.add_all(vehicle_docs)
        db.commit()
        db.refresh(vehicle)

        return vehicle

    @staticmethod
    def get_my_vehicles(db: Session, user: AppUser):
        # Fetch user's fleet
        fleet = (
            db.query(Fleet)
            .filter(Fleet.owner_user_id == user.user_id)
            .first()
        )

        if not fleet:
            return []

        # Return all vehicles in the fleet
        vehicles = (
            db.query(Vehicle)
            .filter(Vehicle.fleet_id == fleet.fleet_id)
            .all()
        )

        return vehicles

    @staticmethod
    def _verify_vehicle_ownership(db: Session, user: AppUser, vehicle_id: int) -> Vehicle:
        """
        Verify vehicle management permissions.
        
        Rules:
        - Fleet owners can manage vehicles in BUSINESS fleets
        - Drivers can manage vehicles in their INDIVIDUAL fleet only
        """
        # Get vehicle
        vehicle = (
            db.query(Vehicle)
            .filter(Vehicle.vehicle_id == vehicle_id)
            .first()
        )

        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found"
            )

        # Get the fleet that owns this vehicle
        fleet = (
            db.query(Fleet)
            .filter(Fleet.fleet_id == vehicle.fleet_id)
            .first()
        )

        if not fleet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fleet not found"
            )

        # Check permissions:
        # 1. User is fleet owner (can manage any vehicles in their fleet)
        is_owner = fleet.owner_user_id == user.user_id
        
        # 2. User is managing their own INDIVIDUAL fleet
        is_own_individual_fleet = (
            fleet.fleet_type == "INDIVIDUAL" and 
            fleet.owner_user_id == user.user_id
        )

        if not (is_owner or is_own_individual_fleet):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only manage vehicles in your own fleet. "
                       "Drivers cannot add vehicles to BUSINESS fleets."
            )

        return vehicle

    @staticmethod
    def create_vehicle_spec(
        db: Session,
        user: AppUser,
        vehicle_id: int,
        data: VehicleSpecCreateRequest
    ):
        # Verify ownership
        vehicle = VehicleService._verify_vehicle_ownership(db, user, vehicle_id)

        # Check if spec already exists
        existing_spec = (
            db.query(VehicleSpec)
            .filter(VehicleSpec.vehicle_id == vehicle_id)
            .first()
        )

        if existing_spec:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vehicle spec already exists"
            )

        # Create spec
        spec = VehicleSpec(
            vehicle_id=vehicle_id,
            manufacturer=data.manufacturer,
            model_name=data.model_name,
            manufacture_year=data.manufacture_year,
            fuel_type=data.fuel_type,
            seating_capacity=data.seating_capacity,
            created_by=user.user_id
        )

        db.add(spec)
        db.commit()
        db.refresh(spec)

        return spec

    @staticmethod
    def create_vehicle_document(
        db: Session,
        user: AppUser,
        vehicle_id: int,
        data: VehicleDocumentCreateRequest
    ):
        # Verify ownership
        vehicle = VehicleService._verify_vehicle_ownership(db, user, vehicle_id)

        # Create document
        document = VehicleDocument(
            vehicle_id=vehicle_id,
            document_type=data.document_type,
            file_url=data.file_url,
            verification_status="PENDING",
            created_by=user.user_id
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        return document

    @staticmethod
    def upload_vehicle_photos(
        db: Session,
        user: AppUser,
        vehicle_id: int,
        photo_urls: List[str]
    ):
        # Verify ownership
        vehicle = VehicleService._verify_vehicle_ownership(db, user, vehicle_id)

        # Create document for each photo
        documents = []
        for photo_url in photo_urls:
            document = VehicleDocument(
                vehicle_id=vehicle_id,
                document_type="VEHICLE_PHOTO",
                file_url=photo_url,
                verification_status="PENDING",
                created_by=user.user_id
            )
            documents.append(document)

        db.add_all(documents)
        db.commit()

        return documents

    @staticmethod
    def get_driver_approved_vehicles(db: Session, user: AppUser) -> List[dict]:
        """
        Get all APPROVED vehicles for an independent driver.
        Only works for drivers with INDIVIDUAL fleet.
        """
        # Check if driver has an INDIVIDUAL fleet (is independent)
        fleet = (
            db.query(Fleet)
            .filter(
                Fleet.owner_user_id == user.user_id,
                Fleet.fleet_type == "INDIVIDUAL"
            )
            .first()
        )

        if not fleet:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This feature is only available for independent drivers"
            )

        # Get all APPROVED vehicles in this fleet
        vehicles = (
            db.query(Vehicle)
            .filter(
                Vehicle.fleet_id == fleet.fleet_id,
                Vehicle.approval_status == "APPROVED"
            )
            .all()
        )

        # Check current active assignment
        active_assignment = (
            db.query(DriverVehicleAssignment)
            .filter(
                DriverVehicleAssignment.driver_id == user.user_id,
                DriverVehicleAssignment.end_time.is_(None)
            )
            .first()
        )

        active_vehicle_id = active_assignment.vehicle_id if active_assignment else None

        return [
            {
                "vehicle_id": v.vehicle_id,
                "registration_no": v.registration_no,
                "category": v.category,
                "approval_status": v.approval_status,
                "is_currently_assigned": v.vehicle_id == active_vehicle_id
            }
            for v in vehicles
        ]

    @staticmethod
    def select_vehicle_for_shift(db: Session, user: AppUser, vehicle_id: int, end_shift_if_active: bool = False) -> dict:
        """
        Select a vehicle for shift (independent drivers only).
        
        - Ends any existing active vehicle assignment
        - Creates new assignment for the selected vehicle
        - If end_shift_if_active=True, will auto-end any active shift first
        - If end_shift_if_active=False (default), will reject if shift is active
        """
        # Check if driver has an INDIVIDUAL fleet (is independent)
        fleet = (
            db.query(Fleet)
            .filter(
                Fleet.owner_user_id == user.user_id,
                Fleet.fleet_type == "INDIVIDUAL"
            )
            .first()
        )

        if not fleet:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This feature is only available for independent drivers"
            )

        # Check if driver has active shift
        active_shift = (
            db.query(DriverShift)
            .filter(
                DriverShift.driver_id == user.user_id,
                DriverShift.ended_at.is_(None)
            )
            .first()
        )

        if active_shift:
            if active_shift.status == "BUSY":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot switch vehicles while on an active trip"
                )
            
            if end_shift_if_active:
                # Auto-end the shift
                active_shift.status = "OFFLINE"
                active_shift.ended_at = datetime.now(timezone.utc)
                active_shift.updated_by = user.user_id
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot switch vehicles while on an active shift. Go offline first or set end_shift_if_active=true."
                )

        # Verify vehicle exists, belongs to driver's fleet, and is APPROVED
        vehicle = (
            db.query(Vehicle)
            .filter(
                Vehicle.vehicle_id == vehicle_id,
                Vehicle.fleet_id == fleet.fleet_id,
                Vehicle.approval_status == "APPROVED"
            )
            .first()
        )

        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found or not approved"
            )

        # End any existing active assignment
        existing_assignment = (
            db.query(DriverVehicleAssignment)
            .filter(
                DriverVehicleAssignment.driver_id == user.user_id,
                DriverVehicleAssignment.end_time.is_(None)
            )
            .first()
        )

        if existing_assignment:
            # If already assigned to this vehicle, just return
            if existing_assignment.vehicle_id == vehicle_id:
                return {
                    "vehicle_id": vehicle.vehicle_id,
                    "registration_no": vehicle.registration_no,
                    "category": vehicle.category,
                    "approval_status": vehicle.approval_status,
                    "is_currently_assigned": True
                }
            
            # End the existing assignment
            existing_assignment.end_time = datetime.now(timezone.utc)
            existing_assignment.updated_by = user.user_id

        # Create new assignment
        new_assignment = DriverVehicleAssignment(
            driver_id=user.user_id,
            vehicle_id=vehicle_id,
            start_time=datetime.now(timezone.utc),
            end_time=None,
            created_by=user.user_id
        )
        db.add(new_assignment)
        db.commit()

        return {
            "vehicle_id": vehicle.vehicle_id,
            "registration_no": vehicle.registration_no,
            "category": vehicle.category,
            "approval_status": vehicle.approval_status,
            "is_currently_assigned": True
        }
