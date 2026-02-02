from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date, datetime
import os
import shutil
from pathlib import Path

from app.api.deps.jwt_auth import get_current_user
from app.core.database import SessionLocal
from app.models.identity import AppUser
from app.models.core import City
from app.schemas.fleet import (
    FleetApplyRequest,
    FleetApplyResponse,
    FleetResponse,
    FleetDriverInviteRequest,
    FleetDriverResponse,
    FleetDriverListResponse,
    FleetAssignmentCreateRequest,
    FleetAssignmentResponse,
    FleetAssignmentListResponse,
    FleetCityAddRequest,
    FleetCityResponse,
    FleetCityListResponse,
    FleetDriverAvailabilityListResponse,
    FleetDocumentInput
)
from app.services.fleet_service import FleetService
from app.services.fleet_owner_service import FleetOwnerService
from app.services.driver_work_availability_service import DriverWorkAvailabilityService


router = APIRouter(prefix="/fleet", tags=["Phase-2 Fleet"])

# Directory for fleet document uploads
FLEET_UPLOAD_DIR = Path("uploads/fleet_documents")
FLEET_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/apply-with-documents", response_model=FleetApplyResponse)
async def apply_fleet_with_documents(
    tenant_id: int = Form(...),
    fleet_name: str = Form(...),
    aadhaar: UploadFile = File(None),
    pan: UploadFile = File(None),
    gst_certificate: UploadFile = File(None),
    company_registration: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Apply for fleet owner with document file uploads.
    Files are stored locally in uploads/fleet_documents/{user_id}/
    
    Required:
    - tenant_id
    - fleet_name
    - At least one of: aadhaar, pan
    
    Optional:
    - gst_certificate
    - company_registration
    """
    user_id = current_user.get("user_id")
    user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Validate at least one identity document
    if not aadhaar and not pan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one of Aadhaar or PAN must be provided"
        )

    # Create user-specific directory
    user_dir = FLEET_UPLOAD_DIR / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)

    # Helper function to save file locally
    async def save_file(upload_file: UploadFile, doc_type: str) -> str:
        """Save uploaded file and return relative path"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_ext = os.path.splitext(upload_file.filename)[1]
        filename = f"{doc_type}_{timestamp}{file_ext}"
        file_path = user_dir / filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        
        # Return relative path for database storage
        return f"uploads/fleet_documents/{user_id}/{filename}"

    # Build documents list
    documents = []
    
    if aadhaar:
        aadhaar_path = await save_file(aadhaar, "AADHAAR")
        documents.append(FleetDocumentInput(document_type="AADHAAR", file_url=aadhaar_path))
    
    if pan:
        pan_path = await save_file(pan, "PAN")
        documents.append(FleetDocumentInput(document_type="PAN", file_url=pan_path))
    
    if gst_certificate:
        gst_path = await save_file(gst_certificate, "GST_CERTIFICATE")
        documents.append(FleetDocumentInput(document_type="GST_CERTIFICATE", file_url=gst_path))
    
    if company_registration:
        company_path = await save_file(company_registration, "COMPANY_REGISTRATION")
        documents.append(FleetDocumentInput(document_type="COMPANY_REGISTRATION", file_url=company_path))

    # Create application data
    data = FleetApplyRequest(
        tenant_id=tenant_id,
        fleet_name=fleet_name,
        fleet_type="BUSINESS",
        documents=documents
    )

    fleet = FleetService.apply_fleet(db=db, user=user, data=data)

    return FleetApplyResponse(
        fleet_id=fleet.fleet_id,
        approval_status=fleet.approval_status
    )


@router.post("/apply", response_model=FleetApplyResponse)
def apply_fleet(
    data: FleetApplyRequest,
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

    fleet = FleetService.apply_fleet(db=db, user=user, data=data)

    return FleetApplyResponse(
        fleet_id=fleet.fleet_id,
        approval_status=fleet.approval_status
    )


@router.get("/my", response_model=FleetResponse)
def get_my_fleet(
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

    fleet = FleetService.get_my_fleet(db=db, user=user)

    return FleetResponse(
        fleet_id=fleet.fleet_id,
        fleet_name=fleet.fleet_name,
        tenant_id=fleet.tenant_id,
        approval_status=fleet.approval_status,
        status=fleet.status
    )


# ==================== Fleet Owner Driver Management ====================

@router.post("/drivers/invite")
def invite_driver(
    data: FleetDriverInviteRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a pending invite for a driver to join the fleet."""
    user_id = current_user.get("user_id")
    user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    invite = FleetOwnerService.invite_driver(db=db, user=user, driver_id=data.driver_id)

    driver_user = db.query(AppUser).filter(AppUser.user_id == data.driver_id).first()

    return {
        "invite_id": invite.invite_id,
        "fleet_id": invite.fleet_id,
        "driver_id": invite.driver_id,
        "driver_name": driver_user.full_name if driver_user else "",
        "driver_phone": driver_user.phone if driver_user else "",
        "status": invite.status,
        "invited_at": invite.invited_at,
        "responded_at": invite.responded_at
    }


@router.get("/drivers", response_model=FleetDriverListResponse)
def list_fleet_drivers(
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

    rows = FleetOwnerService.list_drivers(db=db, user=user)

    drivers = [
        FleetDriverResponse(
            driver_id=user_row.user_id,
            full_name=user_row.full_name,
            phone=user_row.phone,
            start_date=assoc.start_date,
            end_date=assoc.end_date
        )
        for assoc, user_row in rows
    ]

    return FleetDriverListResponse(drivers=drivers, total=len(drivers))


@router.post("/drivers/{driver_id}/remove")
def remove_fleet_driver(
    driver_id: int,
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

    FleetOwnerService.remove_driver(db=db, user=user, driver_id=driver_id)

    return {"message": "Driver removed from fleet"}


# ==================== Fleet Owner Assignments ====================

@router.post("/assignments", response_model=FleetAssignmentResponse)
def create_assignment(
    data: FleetAssignmentCreateRequest,
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

    assignment = FleetOwnerService.create_assignment(
        db=db,
        user=user,
        driver_id=data.driver_id,
        vehicle_id=data.vehicle_id
    )

    return FleetAssignmentResponse(
        assignment_id=assignment.assignment_id,
        driver_id=assignment.driver_id,
        vehicle_id=assignment.vehicle_id,
        start_time=assignment.start_time,
        end_time=assignment.end_time
    )


@router.post("/assignments/{assignment_id}/end", response_model=FleetAssignmentResponse)
def end_assignment(
    assignment_id: int,
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

    assignment = FleetOwnerService.end_assignment(db=db, user=user, assignment_id=assignment_id)

    return FleetAssignmentResponse(
        assignment_id=assignment.assignment_id,
        driver_id=assignment.driver_id,
        vehicle_id=assignment.vehicle_id,
        start_time=assignment.start_time,
        end_time=assignment.end_time
    )


@router.get("/assignments/active", response_model=FleetAssignmentListResponse)
def list_active_assignments(
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

    assignments = FleetOwnerService.list_active_assignments(db=db, user=user)

    items = [
        FleetAssignmentResponse(
            assignment_id=a.assignment_id,
            driver_id=a.driver_id,
            vehicle_id=a.vehicle_id,
            start_time=a.start_time,
            end_time=a.end_time
        )
        for a in assignments
    ]

    return FleetAssignmentListResponse(assignments=items, total=len(items))


# ==================== Fleet Cities ====================

@router.post("/cities", response_model=FleetCityResponse)
def add_fleet_city(
    data: FleetCityAddRequest,
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

    record = FleetOwnerService.add_city(db=db, user=user, city_id=data.city_id, address=data.address)

    city = db.query(City).filter(City.city_id == record.city_id).first()
    return FleetCityResponse(
        city_id=record.city_id, 
        city_name=city.name if city else "",
        address=record.address
    )


@router.get("/cities", response_model=FleetCityListResponse)
def list_fleet_cities(
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

    rows = FleetOwnerService.list_cities(db=db, user=user)
    cities = [
        FleetCityResponse(city_id=city.city_id, city_name=city.name, address=fc.address)
        for fc, city in rows
    ]
    return FleetCityListResponse(cities=cities, total=len(cities))


@router.get("/cities/available")
def list_available_cities(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get cities available for this fleet owner to add.
    Returns cities in the fleet's tenant that are not yet added to the fleet.
    """
    user_id = current_user.get("user_id")
    user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    from app.models.fleet import Fleet, FleetCity
    from app.models.tenant import TenantCity
    
    # Get fleet for this owner
    fleet = (
        db.query(Fleet)
        .filter(
            Fleet.owner_user_id == user.user_id,
            Fleet.fleet_type == "BUSINESS",
            Fleet.approval_status == "APPROVED"
        )
        .first()
    )
    if not fleet:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only approved fleet owners can view available cities"
        )
    
    # Get cities already added to fleet
    existing_city_ids = (
        db.query(FleetCity.city_id)
        .filter(FleetCity.fleet_id == fleet.fleet_id)
        .subquery()
    )
    
    # Get tenant cities not yet added
    available = (
        db.query(City)
        .join(TenantCity, TenantCity.city_id == City.city_id)
        .filter(
            TenantCity.tenant_id == fleet.tenant_id,
            ~City.city_id.in_(existing_city_ids)
        )
        .all()
    )
    
    return {
        "cities": [{"city_id": c.city_id, "city_name": c.name} for c in available],
        "total": len(available)
    }


@router.delete("/cities/{city_id}")
def remove_fleet_city(
    city_id: int,
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

    FleetOwnerService.remove_city(db=db, user=user, city_id=city_id)
    return {"message": "City removed"}


# ---------------------- Driver Availability (Fleet Owner View) ----------------------

@router.get("/drivers/availability", response_model=FleetDriverAvailabilityListResponse)
def view_drivers_availability(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """View all drivers' work availability in fleet for date range."""
    user_id = current_user.get("user_id")
    user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    rows = DriverWorkAvailabilityService.list_fleet_driver_availability(
        db=db,
        user=user,
        start_date=start_date,
        end_date=end_date
    )

    from app.schemas.fleet import FleetDriverAvailabilityItem

    items = [
        FleetDriverAvailabilityItem(
            driver_id=app_user.user_id,
            full_name=app_user.full_name,
            phone=app_user.phone,
            date=avail.date,
            is_available=avail.is_available,
            note=avail.note
        )
        for avail, app_user in rows
    ]

    return FleetDriverAvailabilityListResponse(records=items, total=len(items))


# ==================== Driver Lookup (by phone) ====================

@router.get("/drivers/search")
def search_driver_by_phone(
    phone: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Search for an APPROVED driver by phone number.
    Fleet owner can use this to find drivers to invite.
    """
    user_id = current_user.get("user_id")
    user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Ensure user has approved fleet
    from app.models.fleet import Fleet, DriverProfile
    fleet = (
        db.query(Fleet)
        .filter(
            Fleet.owner_user_id == user.user_id,
            Fleet.fleet_type == "BUSINESS",
            Fleet.approval_status == "APPROVED"
        )
        .first()
    )
    if not fleet:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only approved fleet owners can search for drivers"
        )

    # Find driver by phone
    driver_user = (
        db.query(AppUser)
        .filter(AppUser.phone == phone)
        .first()
    )
    
    if not driver_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No user found with this phone number"
        )

    # Check if they have an approved driver profile
    driver_profile = (
        db.query(DriverProfile)
        .filter(DriverProfile.driver_id == driver_user.user_id)
        .first()
    )
    
    if not driver_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not a registered driver"
        )
    
    if driver_profile.approval_status != "APPROVED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Driver is not approved (status: {driver_profile.approval_status})"
        )

    # Check tenant match
    if driver_profile.tenant_id != fleet.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Driver belongs to a different tenant"
        )

    return {
        "driver_id": driver_user.user_id,
        "full_name": driver_user.full_name,
        "phone": driver_user.phone,
        "approval_status": driver_profile.approval_status,
        "allowed_vehicle_categories": driver_profile.allowed_vehicle_categories or []
    }


# ==================== Pending Invites (Fleet Owner View) ====================

@router.get("/invites/pending")
def list_pending_invites(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all pending invites sent by this fleet owner."""
    user_id = current_user.get("user_id")
    user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    from app.models.fleet import Fleet, FleetDriverInvite
    
    fleet = (
        db.query(Fleet)
        .filter(
            Fleet.owner_user_id == user.user_id,
            Fleet.fleet_type == "BUSINESS",
            Fleet.approval_status == "APPROVED"
        )
        .first()
    )
    if not fleet:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only approved fleet owners can view invites"
        )

    invites = (
        db.query(FleetDriverInvite, AppUser)
        .join(AppUser, AppUser.user_id == FleetDriverInvite.driver_id)
        .filter(FleetDriverInvite.fleet_id == fleet.fleet_id)
        .order_by(FleetDriverInvite.invited_at.desc())
        .all()
    )

    return {
        "invites": [
            {
                "invite_id": invite.invite_id,
                "driver_id": invite.driver_id,
                "driver_name": driver.full_name,
                "driver_phone": driver.phone,
                "status": invite.status,
                "invited_at": invite.invited_at.isoformat() if invite.invited_at else None,
                "responded_at": invite.responded_at.isoformat() if invite.responded_at else None
            }
            for invite, driver in invites
        ],
        "total": len(invites)
    }


# ==================== Fleet Trips (Read-only) ====================

@router.get("/trips")
def list_fleet_trips(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    List trips completed by drivers in this fleet.
    Read-only historical view.
    """
    user_id = current_user.get("user_id")
    user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    from app.models.fleet import Fleet, FleetDriver
    from app.models.trips import Trip
    from app.models.vehicle import Vehicle
    
    fleet = (
        db.query(Fleet)
        .filter(
            Fleet.owner_user_id == user.user_id,
            Fleet.fleet_type == "BUSINESS",
            Fleet.approval_status == "APPROVED"
        )
        .first()
    )
    if not fleet:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only approved fleet owners can view fleet trips"
        )

    # Get driver IDs in this fleet
    fleet_driver_ids = (
        db.query(FleetDriver.driver_id)
        .filter(FleetDriver.fleet_id == fleet.fleet_id)
        .subquery()
    )

    # Get trips by fleet drivers
    trips = (
        db.query(Trip, AppUser, Vehicle)
        .outerjoin(AppUser, AppUser.user_id == Trip.driver_id)
        .outerjoin(Vehicle, Vehicle.vehicle_id == Trip.vehicle_id)
        .filter(Trip.driver_id.in_(fleet_driver_ids))
        .order_by(Trip.requested_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    total = (
        db.query(Trip)
        .filter(Trip.driver_id.in_(fleet_driver_ids))
        .count()
    )

    return {
        "trips": [
            {
                "trip_id": trip.trip_id,
                "driver_id": trip.driver_id,
                "driver_name": driver.full_name if driver else None,
                "vehicle_id": trip.vehicle_id,
                "vehicle_registration": vehicle.registration_no if vehicle else None,
                "vehicle_category": vehicle.category if vehicle else None,
                "status": trip.status,
                "fare_amount": float(trip.fare_amount) if trip.fare_amount else None,
                "requested_at": trip.requested_at.isoformat() if trip.requested_at else None,
                "completed_at": trip.completed_at.isoformat() if trip.completed_at else None
            }
            for trip, driver, vehicle in trips
        ],
        "total": total,
        "skip": skip,
        "limit": limit
    }


# ==================== Fleet Vehicles (Read-only list) ====================

@router.get("/vehicles")
def list_fleet_vehicles(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all vehicles belonging to this fleet."""
    user_id = current_user.get("user_id")
    user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    from app.models.fleet import Fleet
    from app.models.vehicle import Vehicle
    
    fleet = (
        db.query(Fleet)
        .filter(
            Fleet.owner_user_id == user.user_id,
            Fleet.fleet_type == "BUSINESS",
            Fleet.approval_status == "APPROVED"
        )
        .first()
    )
    if not fleet:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only approved fleet owners can view fleet vehicles"
        )

    vehicles = (
        db.query(Vehicle)
        .filter(Vehicle.fleet_id == fleet.fleet_id)
        .all()
    )

    return {
        "vehicles": [
            {
                "vehicle_id": v.vehicle_id,
                "registration_no": v.registration_no,
                "category": v.category,
                "status": v.status,
                "approval_status": v.approval_status
            }
            for v in vehicles
        ],
        "total": len(vehicles)
    }
