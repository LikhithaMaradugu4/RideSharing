from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps.jwt_auth import get_current_user
from app.core.database import SessionLocal
from app.models.identity import AppUser
from app.schemas.vehicle import (
    VehicleCreateRequest,
    VehicleResponse,
    VehicleSpecCreateRequest,
    VehicleSpecResponse,
    VehicleDocumentCreateRequest,
    VehicleDocumentResponse,
    VehiclePhotoUploadRequest,
    DriverVehicleResponse,
    SelectVehicleRequest
)
from app.services.vehicle_service import VehicleService


router = APIRouter(prefix="/vehicles", tags=["Phase-2 Vehicles"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("", response_model=VehicleResponse)
def create_vehicle(
    data: VehicleCreateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get("user_id")
    user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    vehicle = VehicleService.create_vehicle(db=db, user=user, data=data)

    return VehicleResponse(
        vehicle_id=vehicle.vehicle_id,
        tenant_id=vehicle.tenant_id,
        fleet_id=vehicle.fleet_id,
        category=vehicle.category,
        registration_no=vehicle.registration_no,
        status=vehicle.status,
        approval_status=vehicle.approval_status
    )


@router.get("", response_model=List[VehicleResponse])
def get_my_vehicles(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get("user_id")
    user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    vehicles = VehicleService.get_my_vehicles(db=db, user=user)

    return [
        VehicleResponse(
            vehicle_id=v.vehicle_id,
            tenant_id=v.tenant_id,
            fleet_id=v.fleet_id,
            category=v.category,
            registration_no=v.registration_no,
            status=v.status,
            approval_status=v.approval_status
        )
        for v in vehicles
    ]


@router.post("/{vehicle_id}/spec", response_model=VehicleSpecResponse)
def create_vehicle_spec(
    vehicle_id: int,
    data: VehicleSpecCreateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get("user_id")
    user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    spec = VehicleService.create_vehicle_spec(
        db=db,
        user=user,
        vehicle_id=vehicle_id,
        data=data
    )

    return VehicleSpecResponse(
        vehicle_id=spec.vehicle_id,
        manufacturer=spec.manufacturer,
        model_name=spec.model_name,
        manufacture_year=spec.manufacture_year,
        fuel_type=spec.fuel_type,
        seating_capacity=spec.seating_capacity
    )


@router.post("/{vehicle_id}/documents", response_model=VehicleDocumentResponse)
def create_vehicle_document(
    vehicle_id: int,
    data: VehicleDocumentCreateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get("user_id")
    user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    document = VehicleService.create_vehicle_document(
        db=db,
        user=user,
        vehicle_id=vehicle_id,
        data=data
    )

    return VehicleDocumentResponse(
        document_id=document.document_id,
        vehicle_id=document.vehicle_id,
        document_type=document.document_type,
        file_url=document.file_url,
        verification_status=document.verification_status
    )


@router.post("/{vehicle_id}/photos", response_model=List[VehicleDocumentResponse])
def upload_vehicle_photos(
    vehicle_id: int,
    data: VehiclePhotoUploadRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get("user_id")
    user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    documents = VehicleService.upload_vehicle_photos(
        db=db,
        user=user,
        vehicle_id=vehicle_id,
        photo_urls=data.photo_urls
    )

    return [
        VehicleDocumentResponse(
            document_id=doc.document_id,
            vehicle_id=doc.vehicle_id,
            document_type=doc.document_type,
            file_url=doc.file_url,
            verification_status=doc.verification_status
        )
        for doc in documents
    ]


# ---------------------- Independent Driver Vehicle Selection ----------------------

@router.get("/driver/approved", response_model=List[DriverVehicleResponse])
def get_driver_approved_vehicles(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all APPROVED vehicles for an independent driver.
    
    Only for INDIVIDUAL fleet drivers (independent drivers).
    Returns vehicles with their current assignment status.
    Business fleet drivers will get 403.
    """
    user_id = current_user.get("user_id")
    user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    vehicles = VehicleService.get_driver_approved_vehicles(db=db, user=user)

    return [
        DriverVehicleResponse(
            vehicle_id=v["vehicle_id"],
            registration_no=v["registration_no"],
            category=v["category"],
            approval_status=v["approval_status"],
            is_currently_assigned=v["is_currently_assigned"]
        )
        for v in vehicles
    ]


@router.post("/driver/select", response_model=DriverVehicleResponse)
def select_vehicle_for_shift(
    data: SelectVehicleRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Select a vehicle for shift (independent drivers only).
    
    - Ends any existing active vehicle assignment
    - Creates new assignment for the selected vehicle
    - Only works for INDIVIDUAL fleet drivers
    - Vehicle must be APPROVED
    - If end_shift_if_active=True, will auto-end any active shift first
    """
    user_id = current_user.get("user_id")
    user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    result = VehicleService.select_vehicle_for_shift(
        db=db, 
        user=user, 
        vehicle_id=data.vehicle_id,
        end_shift_if_active=data.end_shift_if_active
    )

    return DriverVehicleResponse(
        vehicle_id=result["vehicle_id"],
        registration_no=result["registration_no"],
        category=result["category"],
        approval_status=result["approval_status"],
        is_currently_assigned=result["is_currently_assigned"]
    )
