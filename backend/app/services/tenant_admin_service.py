from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime, timezone

from app.models.fleet import DriverProfile, Fleet, FleetDriver
from app.models.identity import UserKYC
from app.models.vehicle import Vehicle, VehicleDocument, DriverVehicleAssignment
from app.models.tenant import TenantAdmin, TenantCountry, TenantCity
from app.models.identity import AppUser
from app.models.core import Country, City

class TenantAdminService:

    @staticmethod
    def _get_admin_tenant(db: Session, user: AppUser):
        admin = (
            db.query(TenantAdmin)
            .filter(TenantAdmin.user_id == user.user_id)
            .first()
        )

        if not admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not a tenant admin"
            )

        return admin.tenant_id

    @staticmethod
    def approve_driver(db: Session, user: AppUser, driver_id: int):
        if user.role != "TENANT_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only tenant admins can approve drivers"
            )

        tenant_id = TenantAdminService._get_admin_tenant(db, user)

        driver = (
            db.query(DriverProfile)
            .filter(
                DriverProfile.driver_id == driver_id,
                DriverProfile.tenant_id == tenant_id
            )
            .first()
        )

        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found for this tenant"
            )

        if driver.approval_status != "PENDING":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Driver is not in pending state"
            )

        # Approve driver profile
        driver.approval_status = "APPROVED"
        
        # Auto-create INDIVIDUAL fleet
        fleet = Fleet(
            owner_user_id=driver_id,
            tenant_id=tenant_id,
            fleet_name=f"Driver {driver_id} Fleet",
            fleet_type="INDIVIDUAL",
            approval_status="APPROVED",
            status="ACTIVE",
            created_by=user.user_id
        )
        db.add(fleet)
        db.flush()  # Get fleet_id
        
        # Create active fleet_driver association
        fleet_driver = FleetDriver(
            fleet_id=fleet.fleet_id,
            driver_id=driver_id,
            start_date=datetime.now(timezone.utc),
            end_date=None,
            created_by=user.user_id
        )
        db.add(fleet_driver)
        db.commit()

    @staticmethod
    def reject_driver(db: Session, user: AppUser, driver_id: int):
        if user.role != "TENANT_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only tenant admins can reject drivers"
            )

        tenant_id = TenantAdminService._get_admin_tenant(db, user)

        driver = (
            db.query(DriverProfile)
            .filter(
                DriverProfile.driver_id == driver_id,
                DriverProfile.tenant_id == tenant_id
            )
            .first()
        )

        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found for this tenant"
            )

        driver.approval_status = "REJECTED"
        db.commit()

    @staticmethod
    def get_pending_drivers(db: Session, user: AppUser):
        if user.role != "TENANT_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only tenant admins can view pending drivers"
            )

        tenant_id = TenantAdminService._get_admin_tenant(db, user)

        drivers = (
            db.query(DriverProfile, AppUser)
            .join(AppUser, DriverProfile.driver_id == AppUser.user_id)
            .filter(
                DriverProfile.tenant_id == tenant_id,
                DriverProfile.approval_status == "PENDING"
            )
            .all()
        )

        return drivers

    @staticmethod
    def get_all_drivers(db: Session, user: AppUser):
        if user.role != "TENANT_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only tenant admins can view drivers"
            )

        tenant_id = TenantAdminService._get_admin_tenant(db, user)

        drivers = (
            db.query(DriverProfile, AppUser)
            .join(AppUser, DriverProfile.driver_id == AppUser.user_id)
            .filter(DriverProfile.tenant_id == tenant_id)
            .all()
        )

        return drivers

    @staticmethod
    def approve_driver_with_fleet(
        db: Session,
        user: AppUser,
        driver_id: int,
        allowed_vehicle_categories: List[str]
    ):
        if user.role != "TENANT_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only tenant admins can approve drivers"
            )

        if not allowed_vehicle_categories:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="allowed_vehicle_categories is required"
            )

        tenant_id = TenantAdminService._get_admin_tenant(db, user)

        driver = (
            db.query(DriverProfile)
            .filter(
                DriverProfile.driver_id == driver_id,
                DriverProfile.tenant_id == tenant_id
            )
            .first()
        )

        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found for this tenant"
            )

        if driver.approval_status != "PENDING":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Driver is not in pending state"
            )

        # Update driver profile
        driver.approval_status = "APPROVED"
        driver.allowed_vehicle_categories = allowed_vehicle_categories

        # Auto-create INDIVIDUAL fleet
        fleet = Fleet(
            owner_user_id=driver_id,
            tenant_id=tenant_id,
            fleet_name=f"Driver {driver_id} Fleet",
            fleet_type="INDIVIDUAL",
            approval_status="APPROVED",
            status="ACTIVE",
            created_by=user.user_id
        )

        db.add(fleet)
        db.flush()  # Get fleet_id
        
        # Create active fleet_driver association
        fleet_driver = FleetDriver(
            fleet_id=fleet.fleet_id,
            driver_id=driver_id,
            start_date=datetime.now(timezone.utc),
            end_date=None,
            created_by=user.user_id
        )
        db.add(fleet_driver)
        db.commit()

        return driver

    @staticmethod
    def reject_driver_with_reason(
        db: Session,
        user: AppUser,
        driver_id: int,
        reason: Optional[str] = None
    ):
        if user.role != "TENANT_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only tenant admins can reject drivers"
            )

        tenant_id = TenantAdminService._get_admin_tenant(db, user)

        driver = (
            db.query(DriverProfile)
            .filter(
                DriverProfile.driver_id == driver_id,
                DriverProfile.tenant_id == tenant_id
            )
            .first()
        )

        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found for this tenant"
            )

        driver.approval_status = "REJECTED"
        # Note: reason could be stored in a separate field if schema supports it
        db.commit()

    @staticmethod
    def approve_fleet(db: Session, user: AppUser, fleet_id: int):
        if user.role != "TENANT_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only tenant admins can approve fleets"
            )

        tenant_id = TenantAdminService._get_admin_tenant(db, user)

        fleet = (
            db.query(Fleet)
            .filter(
                Fleet.fleet_id == fleet_id,
                Fleet.tenant_id == tenant_id
            )
            .first()
        )

        if not fleet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fleet not found for this tenant"
            )

        if fleet.fleet_type != "BUSINESS":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only BUSINESS fleets can be approved here"
            )

        if fleet.approval_status != "PENDING":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Fleet is not in pending state"
            )

        fleet.approval_status = "APPROVED"
        db.commit()

    @staticmethod
    def reject_fleet(db: Session, user: AppUser, fleet_id: int):
        if user.role != "TENANT_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only tenant admins can reject fleets"
            )

        tenant_id = TenantAdminService._get_admin_tenant(db, user)

        fleet = (
            db.query(Fleet)
            .filter(
                Fleet.fleet_id == fleet_id,
                Fleet.tenant_id == tenant_id
            )
            .first()
        )

        if not fleet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fleet not found for this tenant"
            )

        fleet.approval_status = "REJECTED"
        db.commit()

    @staticmethod
    def get_pending_fleets_with_docs(db: Session, user: AppUser):
        if user.role != "TENANT_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only tenant admins can view pending fleets"
            )

        tenant_id = TenantAdminService._get_admin_tenant(db, user)

        fleets = (
            db.query(Fleet)
            .filter(
                Fleet.tenant_id == tenant_id,
                Fleet.approval_status == "PENDING",
                Fleet.fleet_type == "BUSINESS"
            )
            .all()
        )

        result = []
        for fleet in fleets:
            docs = list(fleet.documents) if hasattr(fleet, "documents") else []
            result.append((fleet, docs))

        return result

    @staticmethod
    def get_all_fleets(db: Session, user: AppUser):
        if user.role != "TENANT_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only tenant admins can view fleets"
            )

        tenant_id = TenantAdminService._get_admin_tenant(db, user)

        fleets = (
            db.query(Fleet)
            .filter(Fleet.tenant_id == tenant_id,
                    Fleet.fleet_type == "BUSINESS",
                    Fleet.approval_status == "APPROVED"
            )
            .all()
        )

        return fleets

    @staticmethod
    def get_driver_documents(db: Session, user: AppUser, driver_id: int):
        if user.role != "TENANT_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only tenant admins can view driver documents"
            )

        tenant_id = TenantAdminService._get_admin_tenant(db, user)

        driver = (
            db.query(DriverProfile)
            .filter(
                DriverProfile.driver_id == driver_id,
                DriverProfile.tenant_id == tenant_id
            )
            .first()
        )

        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found for this tenant"
            )

        documents = (
            db.query(UserKYC)
            .filter(UserKYC.user_id == driver_id)
            .all()
        )

        return documents

    @staticmethod
    def get_vehicle_documents(db: Session, user: AppUser, vehicle_id: int):
        if user.role != "TENANT_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only tenant admins can view vehicle documents"
            )

        tenant_id = TenantAdminService._get_admin_tenant(db, user)
        vehicle = (
            db.query(Vehicle)
            .filter(
                Vehicle.vehicle_id == vehicle_id,
                Vehicle.tenant_id == tenant_id
            )
            .first()
        )
        

        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found for this tenant"
            )

        documents = (
            db.query(VehicleDocument)
            .filter(VehicleDocument.vehicle_id == vehicle_id)
            .all()
        )

        return documents

    @staticmethod
    def get_pending_vehicles(db: Session, user: AppUser):
        if user.role != "TENANT_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only tenant admins can view pending vehicles"
            )
    
        tenant_id = TenantAdminService._get_admin_tenant(db, user)
    
        return (
            db.query(Vehicle)
            .filter(
                Vehicle.tenant_id == tenant_id,
                Vehicle.approval_status == "PENDING"
            )
            .order_by(Vehicle.created_on.desc())
            .all()
        )


    @staticmethod
    def approve_vehicle(
        db: Session, 
        user: AppUser, 
        vehicle_id: int, 
        approval_status: str,
        rejection_reason: Optional[str] = None
    ):
        """Approve or reject a vehicle."""
        if user.role != "TENANT_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only tenant admins can approve vehicles"
            )

        if approval_status not in ["APPROVED", "REJECTED"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="approval_status must be APPROVED or REJECTED"
            )

        tenant_id = TenantAdminService._get_admin_tenant(db, user)

        vehicle = (
           db.query(Vehicle)
           .filter(
               Vehicle.vehicle_id == vehicle_id,
               Vehicle.tenant_id == tenant_id
           )
           .first()
        
        )
        

        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found for this tenant"
            )

        vehicle.approval_status = approval_status
        vehicle.updated_by = user.user_id
        
        # Update status column based on approval
        # APPROVED -> ACTIVE, REJECTED -> INACTIVE
        if approval_status == "APPROVED":
            vehicle.status = "ACTIVE"
        elif approval_status == "REJECTED":
            vehicle.status = "INACTIVE"

        # Update all vehicle documents to match the vehicle approval status
        # When vehicle is APPROVED/REJECTED, all documents get the same status
        document_status = approval_status  # APPROVED or REJECTED
        vehicle_documents = (
            db.query(VehicleDocument)
            .filter(VehicleDocument.vehicle_id == vehicle_id)
            .all()
        )
        for doc in vehicle_documents:
            doc.verification_status = document_status
            doc.verified_by = user.user_id
            doc.verified_on = datetime.now(timezone.utc)

        # If vehicle is APPROVED, auto-assign to driver for INDIVIDUAL fleets
        if approval_status == "APPROVED":
            fleet = db.query(Fleet).filter(Fleet.fleet_id == vehicle.fleet_id).first()
            
            if fleet and fleet.fleet_type == "INDIVIDUAL":
                # For INDIVIDUAL fleets, the owner is the driver
                driver_id = fleet.owner_user_id
                
                # Check if there's already an active assignment for this driver-vehicle pair
                existing_assignment = (
                    db.query(DriverVehicleAssignment)
                    .filter(
                        DriverVehicleAssignment.driver_id == driver_id,
                        DriverVehicleAssignment.vehicle_id == vehicle_id,
                        DriverVehicleAssignment.end_time.is_(None)
                    )
                    .first()
                )
                
                if not existing_assignment:
                    # Create new vehicle assignment
                    assignment = DriverVehicleAssignment(
                        driver_id=driver_id,
                        vehicle_id=vehicle_id,
                        start_time=datetime.now(timezone.utc),
                        end_time=None,
                        created_by=user.user_id
                    )
                    db.add(assignment)

        db.commit()
        db.refresh(vehicle)

        return vehicle
    @staticmethod
    def get_all_vehicles(db: Session, user: AppUser):
      if user.role != "TENANT_ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only tenant admins can view vehicles"
        )

      tenant_id = TenantAdminService._get_admin_tenant(db, user)

      vehicles = (
        db.query(Vehicle)
        .filter(Vehicle.tenant_id == tenant_id)
        .order_by(Vehicle.created_on.desc())
        .all()
    )

      return vehicles

    @staticmethod
    def get_approved_vehicles(db: Session, user: AppUser):
        """Get all approved vehicles for admin's tenant."""
        if user.role != "TENANT_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only tenant admins can view vehicles"
            )

        tenant_id = TenantAdminService._get_admin_tenant(db, user)

        vehicles = (
            db.query(Vehicle)
            .filter(
                Vehicle.tenant_id == tenant_id,
                Vehicle.approval_status == "APPROVED"
            )
            .order_by(Vehicle.created_on.desc())
            .all()
        )

        return vehicles

    # ============================================
    # APPROVAL STATUS UPDATE METHODS
    # ============================================

    @staticmethod
    def update_driver_approval_status(db: Session, user: AppUser, driver_id: int, new_status: str):
        """Update driver approval status."""
        if user.role != "TENANT_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only tenant admins can update driver status"
            )

        if new_status not in ["PENDING", "APPROVED", "REJECTED"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid approval status"
            )

        tenant_id = TenantAdminService._get_admin_tenant(db, user)

        driver = (
            db.query(DriverProfile)
            .filter(
                DriverProfile.driver_id == driver_id,
                DriverProfile.tenant_id == tenant_id
            )
            .first()
        )

        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found for this tenant"
            )

        driver.approval_status = new_status
        driver.updated_by = user.user_id
        db.commit()
        db.refresh(driver)
        return driver

    @staticmethod
    def update_fleet_approval_status(db: Session, user: AppUser, fleet_id: int, new_status: str):
        """Update fleet approval status."""
        if user.role != "TENANT_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only tenant admins can update fleet status"
            )

        if new_status not in ["PENDING", "APPROVED", "REJECTED"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid approval status"
            )

        tenant_id = TenantAdminService._get_admin_tenant(db, user)

        fleet = (
            db.query(Fleet)
            .filter(
                Fleet.fleet_id == fleet_id,
                Fleet.tenant_id == tenant_id
            )
            .first()
        )

        if not fleet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fleet not found for this tenant"
            )

        fleet.approval_status = new_status
        fleet.updated_by = user.user_id
        db.commit()
        db.refresh(fleet)
        return fleet

    @staticmethod
    def update_vehicle_approval_status(db: Session, user: AppUser, vehicle_id: int, new_status: str):
        """Update vehicle approval status."""
        if user.role != "TENANT_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only tenant admins can update vehicle status"
            )

        if new_status not in ["PENDING", "APPROVED", "REJECTED"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid approval status"
            )

        tenant_id = TenantAdminService._get_admin_tenant(db, user)

        vehicle = (
            db.query(Vehicle)
            .filter(
                Vehicle.vehicle_id == vehicle_id,
                Vehicle.tenant_id == tenant_id
            )
            .first()
        )

        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found for this tenant"
            )

        vehicle.approval_status = new_status
        vehicle.updated_by = user.user_id
        
        # Update status column based on approval
        if new_status == "APPROVED":
            vehicle.status = "ACTIVE"
        elif new_status == "REJECTED":
            vehicle.status = "INACTIVE"
        
        db.commit()
        db.refresh(vehicle)
        return vehicle

    # ============================================
    # TENANT OPERATING COUNTRIES/CITIES
    # ============================================

    @staticmethod
    def get_all_countries(db: Session):
        """Get all available countries."""
        return db.query(Country).order_by(Country.name).all()

    @staticmethod
    def get_all_cities(db: Session, country_code: Optional[str] = None):
        """Get all available cities, optionally filtered by country."""
        query = db.query(City).filter(City.is_active == True)
        if country_code:
            query = query.filter(City.country_code == country_code)
        return query.order_by(City.name).all()

    @staticmethod
    def get_tenant_countries(db: Session, user: AppUser):
        """Get countries where tenant operates."""
        if user.role != "TENANT_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only tenant admins can view tenant countries"
            )

        tenant_id = TenantAdminService._get_admin_tenant(db, user)

        countries = (
            db.query(TenantCountry, Country)
            .join(Country, Country.country_code == TenantCountry.country_code)
            .filter(TenantCountry.tenant_id == tenant_id)
            .all()
        )

        return countries

    @staticmethod
    def add_tenant_country(db: Session, user: AppUser, country_code: str):
        """Add a country to tenant's operating regions."""
        if user.role != "TENANT_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only tenant admins can add countries"
            )

        tenant_id = TenantAdminService._get_admin_tenant(db, user)

        # Verify country exists
        country = db.query(Country).filter(Country.country_code == country_code).first()
        if not country:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Country not found"
            )

        # Check if already exists
        existing = (
            db.query(TenantCountry)
            .filter(
                TenantCountry.tenant_id == tenant_id,
                TenantCountry.country_code == country_code
            )
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Country already added to tenant"
            )

        tenant_country = TenantCountry(
            tenant_id=tenant_id,
            country_code=country_code,
            created_by=user.user_id
        )
        db.add(tenant_country)
        db.commit()
        db.refresh(tenant_country)
        return tenant_country, country

    @staticmethod
    def remove_tenant_country(db: Session, user: AppUser, country_code: str):
        """Remove a country from tenant's operating regions."""
        if user.role != "TENANT_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only tenant admins can remove countries"
            )

        tenant_id = TenantAdminService._get_admin_tenant(db, user)

        tenant_country = (
            db.query(TenantCountry)
            .filter(
                TenantCountry.tenant_id == tenant_id,
                TenantCountry.country_code == country_code
            )
            .first()
        )

        if not tenant_country:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Country not found for this tenant"
            )

        db.delete(tenant_country)
        db.commit()
        return {"message": "Country removed"}

    @staticmethod
    def get_tenant_cities(db: Session, user: AppUser):
        """Get cities where tenant operates."""
        if user.role != "TENANT_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only tenant admins can view tenant cities"
            )

        tenant_id = TenantAdminService._get_admin_tenant(db, user)

        cities = (
            db.query(TenantCity, City)
            .join(City, City.city_id == TenantCity.city_id)
            .filter(TenantCity.tenant_id == tenant_id)
            .all()
        )

        return cities

    @staticmethod
    def add_tenant_city(db: Session, user: AppUser, city_id: int):
        """Add a city to tenant's operating regions."""
        if user.role != "TENANT_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only tenant admins can add cities"
            )

        tenant_id = TenantAdminService._get_admin_tenant(db, user)

        # Verify city exists
        city = db.query(City).filter(City.city_id == city_id).first()
        if not city:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="City not found"
            )

        # Verify country is added to tenant
        tenant_country = (
            db.query(TenantCountry)
            .filter(
                TenantCountry.tenant_id == tenant_id,
                TenantCountry.country_code == city.country_code
            )
            .first()
        )
        if not tenant_country:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="City's country is not added to tenant. Add country first."
            )

        # Check if already exists
        existing = (
            db.query(TenantCity)
            .filter(
                TenantCity.tenant_id == tenant_id,
                TenantCity.city_id == city_id
            )
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="City already added to tenant"
            )

        tenant_city = TenantCity(
            tenant_id=tenant_id,
            city_id=city_id,
            created_by=user.user_id
        )
        db.add(tenant_city)
        db.commit()
        db.refresh(tenant_city)
        return tenant_city, city

    @staticmethod
    def remove_tenant_city(db: Session, user: AppUser, city_id: int):
        """Remove a city from tenant's operating regions."""
        if user.role != "TENANT_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only tenant admins can remove cities"
            )

        tenant_id = TenantAdminService._get_admin_tenant(db, user)

        tenant_city = (
            db.query(TenantCity)
            .filter(
                TenantCity.tenant_id == tenant_id,
                TenantCity.city_id == city_id
            )
            .first()
        )

        if not tenant_city:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="City not found for this tenant"
            )

        db.delete(tenant_city)
        db.commit()
        return {"message": "City removed"}

    @staticmethod
    def get_driver_details(db: Session, user: AppUser, driver_id: int):
        """Get driver details including fleet assignment info."""
        if user.role != "TENANT_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only tenant admins can view driver details"
            )

        tenant_id = TenantAdminService._get_admin_tenant(db, user)

        # Get driver profile and user info
        result = (
            db.query(DriverProfile, AppUser)
            .join(AppUser, DriverProfile.driver_id == AppUser.user_id)
            .filter(
                DriverProfile.driver_id == driver_id,
                DriverProfile.tenant_id == tenant_id
            )
            .first()
        )

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found for this tenant"
            )

        driver_profile, app_user = result

        # Get fleet assignment info
        fleet_info = (
            db.query(FleetDriver, Fleet)
            .join(Fleet, Fleet.fleet_id == FleetDriver.fleet_id)
            .filter(FleetDriver.driver_id == driver_id)
            .order_by(FleetDriver.start_date.desc())
            .first()
        )

        fleet_id = None
        fleet_name = None
        assignment_start_date = None
        assignment_end_date = None
        assignment_status = None

        if fleet_info:
            fleet_driver, fleet = fleet_info
            fleet_id = fleet.fleet_id
            fleet_name = fleet.fleet_name
            assignment_start_date = fleet_driver.start_date
            assignment_end_date = fleet_driver.end_date
            
            # Determine assignment status
            now = datetime.now(timezone.utc)
            if fleet_driver.end_date is None:
                assignment_status = "ACTIVE"
            elif fleet_driver.end_date > now:
                assignment_status = "ACTIVE"
            else:
                assignment_status = "EXPIRED"

        return {
            "driver_id": driver_profile.driver_id,
            "full_name": app_user.full_name,
            "phone": app_user.phone,
            "approval_status": driver_profile.approval_status,
            "allowed_vehicle_categories": driver_profile.allowed_vehicle_categories,
            "driver_type": driver_profile.driver_type,
            "fleet_id": fleet_id,
            "fleet_name": fleet_name,
            "assignment_start_date": assignment_start_date,
            "assignment_end_date": assignment_end_date,
            "assignment_status": assignment_status
        }

    