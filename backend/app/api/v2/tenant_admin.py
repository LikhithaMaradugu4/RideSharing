from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import os
from pathlib import Path
from datetime import datetime, timezone

from app.api.deps.jwt_auth import get_current_user
from app.core.database import SessionLocal
from app.models.identity import AppUser, UserKYC
from app.models.fleet import DriverProfile

router = APIRouter(prefix="/tenant-admin", tags=["Tenant Admin"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/driver-applications")
def get_driver_applications(
    status_filter: str = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all driver applications for tenant admin.
    Query params:
    - status_filter: PENDING, APPROVED, REJECTED
    """
    user_id = current_user.get("user_id")
    user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # TODO: Add admin role check
    # if user.role != "TENANT_ADMIN":
    #     raise HTTPException(status_code=403, detail="Access denied")
    
    query = db.query(DriverProfile).filter(DriverProfile.tenant_id == user.tenant_id)
    
    if status_filter:
        query = query.filter(DriverProfile.approval_status == status_filter)
    
    drivers = query.all()
    
    result = []
    for driver in drivers:
        driver_user = db.query(AppUser).filter(AppUser.user_id == driver.user_id).first()
        result.append({
            "driver_id": driver.driver_id,
            "user_id": driver.user_id,
            "username": driver_user.username if driver_user else None,
            "driver_type": driver.driver_type,
            "approval_status": driver.approval_status,
            "rating": driver.rating,
            "driving_license_url": driver.driving_license_url,
            "aadhaar_url": driver.aadhaar_url,
            "pan_url": driver.pan_url,
            "passport_photo_url": driver.passport_photo_url,
            "created_at": driver.created_at.isoformat() if driver.created_at else None
        })
    
    return {"applications": result, "total": len(result)}


@router.get("/driver-applications/{driver_id}")
def get_driver_application_details(
    driver_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get detailed driver application with all document URLs"""
    user_id = current_user.get("user_id")
    user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    driver = db.query(DriverProfile).filter(
        DriverProfile.driver_id == driver_id,
        DriverProfile.tenant_id == user.tenant_id
    ).first()
    
    if not driver:
        raise HTTPException(status_code=404, detail="Driver application not found")
    
    driver_user = db.query(AppUser).filter(AppUser.user_id == driver.user_id).first()
    
    return {
        "driver_id": driver.driver_id,
        "user_id": driver.user_id,
        "username": driver_user.username if driver_user else None,
        "email": driver_user.email if driver_user else None,
        "phone": driver_user.phone_number if driver_user else None,
        "driver_type": driver.driver_type,
        "approval_status": driver.approval_status,
        "rating": driver.rating,
        "documents": {
            "driving_license": f"http://localhost:8000/{driver.driving_license_url}" if driver.driving_license_url else None,
            "aadhaar": f"http://localhost:8000/{driver.aadhaar_url}" if driver.aadhaar_url else None,
            "pan": f"http://localhost:8000/{driver.pan_url}" if driver.pan_url else None,
            "photo": f"http://localhost:8000/{driver.passport_photo_url}" if driver.passport_photo_url else None,
        },
        "created_at": driver.created_at.isoformat() if driver.created_at else None
    }


@router.put("/driver-applications/{driver_id}/approve")
def approve_driver_application(
    driver_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Approve a driver application and update both driver_profile and user_kyc tables"""
    user_id = current_user.get("user_id")
    user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    driver = db.query(DriverProfile).filter(
        DriverProfile.driver_id == driver_id,
        DriverProfile.tenant_id == user.tenant_id
    ).first()
    
    if not driver:
        raise HTTPException(status_code=404, detail="Driver application not found")
    
    # Update driver_profile status
    driver.approval_status = "APPROVED"
    
    # Update all related user_kyc documents for this driver
    kyc_records = db.query(UserKYC).filter(UserKYC.user_id == driver.user_id).all()
    
    for kyc in kyc_records:
        kyc.verification_status = "APPROVED"
        kyc.verified_by = user_id
        kyc.verified_on = datetime.now(timezone.utc)
    
    db.commit()
    
    return {
        "message": "Driver application approved",
        "driver_id": driver_id,
        "documents_updated": len(kyc_records)
    }


@router.put("/driver-applications/{driver_id}/reject")
def reject_driver_application(
    driver_id: int,
    reason: str = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Reject a driver application and update both driver_profile and user_kyc tables"""
    user_id = current_user.get("user_id")
    user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    driver = db.query(DriverProfile).filter(
        DriverProfile.driver_id == driver_id,
        DriverProfile.tenant_id == user.tenant_id
    ).first()
    
    if not driver:
        raise HTTPException(status_code=404, detail="Driver application not found")
    
    # Update driver_profile status
    driver.approval_status = "REJECTED"
    
    # Update all related user_kyc documents for this driver
    kyc_records = db.query(UserKYC).filter(UserKYC.user_id == driver.user_id).all()
    
    for kyc in kyc_records:
        kyc.verification_status = "REJECTED"
        kyc.verified_by = user_id
        kyc.verified_on = datetime.now(timezone.utc)
    
    db.commit()
    
    return {
        "message": "Driver application rejected",
        "driver_id": driver_id,
        "reason": reason,
        "documents_updated": len(kyc_records)
    }


@router.get("/download-document")
def download_document(
    file_path: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Download driver document (secured endpoint for admins).
    Usage: /api/v2/tenant-admin/download-document?file_path=uploads/driver_documents/123/driving_license_xxx.pdf
    """
    user_id = current_user.get("user_id")
    user = db.query(AppUser).filter(AppUser.user_id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Validate file path is within allowed directory
    if not file_path.startswith("uploads/driver_documents/"):
        raise HTTPException(status_code=403, detail="Access denied")
    
    full_path = Path(file_path)
    
    if not full_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=str(full_path),
        filename=full_path.name,
        media_type="application/octet-stream"
    )
