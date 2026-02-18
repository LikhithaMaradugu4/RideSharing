from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timezone as tz

from app.models.core import Tenant, Country, City
from app.models.pricing import FareConfig
from app.models.financial import CommissionConfig
from app.models.tenant import TenantAdmin, TenantDocument
from app.models.identity import AppUser
from app.schemas.platform_admin import (
    TenantCreateRequest,
    TenantUpdateStatusRequest,
    TenantAdminAssignRequest,
    TenantDocumentUploadRequest,
    CountryCreateRequest,
    CountryUpdateRequest,
    CityCreateRequest,
    CityUpdateRequest,
    FareConfigCreateRequest,
    FareConfigUpdateRequest,
    CommissionConfigCreateRequest,
    CommissionConfigUpdateRequest,
)


class PlatformAdminService:
    """Service for platform admin operations (tenant management only)"""

    # ==================== TENANT MANAGEMENT ====================

    @staticmethod
    def create_tenant(
        db: Session,
        user: AppUser,
        data: TenantCreateRequest
    ) -> Tenant:
        """Create a new tenant (ENTERPRISE onboarding offline)"""
        
        # 1. Verify user is PLATFORM_ADMIN
        if user.role != "PLATFORM_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only platform admins can create tenants"
            )
        
        # 2. Check tenant_code uniqueness
        existing_code = (
            db.query(Tenant)
            .filter(Tenant.tenant_code == data.tenant_code)
            .first()
        )
        
        if existing_code:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Tenant code '{data.tenant_code}' already exists"
            )
        
        # 3. Check tenant name uniqueness
        existing_name = (
            db.query(Tenant)
            .filter(Tenant.name == data.name)
            .first()
        )
        
        if existing_name:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Tenant name '{data.name}' already exists"
            )
        
        # 4. Create tenant with ACTIVE status
        tenant = Tenant(
            name=data.name,
            tenant_code=data.tenant_code,
            default_currency=data.default_currency,
            default_timezone=data.default_timezone,
            status="ACTIVE",
            created_by=user.user_id
        )
        
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
        
        return tenant
    
    @staticmethod
    def get_tenant(db: Session, user: AppUser, tenant_id: int) -> Tenant:
        """Fetch tenant details (platform admin only)"""
        
        if user.role != "PLATFORM_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only platform admins can access tenant details"
            )
        
        tenant = (
            db.query(Tenant)
            .filter(Tenant.tenant_id == tenant_id)
            .first()
        )
        
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        return tenant
    
    @staticmethod
    def list_tenants(db: Session, user: AppUser) -> list:
        """List all tenants (platform admin only)"""
        
        if user.role != "PLATFORM_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only platform admins can list tenants"
            )
        
        tenants = (
            db.query(Tenant)
            .all()
        )
        
        return tenants
    
    @staticmethod
    def update_tenant_status(
        db: Session,
        user: AppUser,
        tenant_id: int,
        data: TenantUpdateStatusRequest
    ) -> Tenant:
        """Update tenant status (ACTIVE or SUSPENDED)"""
        
        # 1. Verify user is PLATFORM_ADMIN
        if user.role != "PLATFORM_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only platform admins can update tenant status"
            )
        
        # 2. Validate status
        if data.status not in ["ACTIVE", "SUSPENDED"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Status must be ACTIVE or SUSPENDED"
            )
        
        # 3. Fetch tenant
        tenant = (
            db.query(Tenant)
            .filter(Tenant.tenant_id == tenant_id)
            .first()
        )
        
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        # 4. Update status
        tenant.status = data.status
        tenant.updated_by = user.user_id
        tenant.updated_on = datetime.utcnow()
        
        db.commit()
        db.refresh(tenant)
        
        return tenant

    # ==================== TENANT ADMIN ASSIGNMENT ====================

    @staticmethod
    def assign_tenant_admin(
        db: Session,
        user: AppUser,
        tenant_id: int,
        data: TenantAdminAssignRequest
    ) -> TenantAdmin:
        """Assign a tenant admin to a tenant"""
        
        # 1. Verify user is PLATFORM_ADMIN
        if user.role != "PLATFORM_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only platform admins can assign tenant admins"
            )
        
        # 2. Verify tenant exists and is ACTIVE
        tenant = (
            db.query(Tenant)
            .filter(Tenant.tenant_id == tenant_id)
            .first()
        )
        
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        if tenant.status != "ACTIVE":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tenant must be ACTIVE to assign admins"
            )
        
        # 3. Verify target user exists
        target_user = (
            db.query(AppUser)
            .filter(AppUser.user_id == data.user_id)
            .first()
        )
        
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target user not found"
            )
        
        # 4. Check if user is already tenant admin for another tenant
        existing_admin = (
            db.query(TenantAdmin)
            .filter(TenantAdmin.user_id == data.user_id)
            .first()
        )
        
        if existing_admin:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User is already a tenant admin for another tenant"
            )
        
        # 5. If primary = true, check for existing primary admin
        if data.is_primary:
            existing_primary = (
                db.query(TenantAdmin)
                .filter(
                    TenantAdmin.tenant_id == tenant_id,
                    TenantAdmin.is_primary == True
                )
                .first()
            )
            
            if existing_primary:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Tenant already has a primary admin"
                )
        
        # 6. Create tenant admin (TRANSACTION START)
        try:
            tenant_admin = TenantAdmin(
                tenant_id=tenant_id,
                user_id=data.user_id,
                is_primary=data.is_primary,
                created_by=user.user_id
            )
            
            db.add(tenant_admin)
            db.flush()
            
            # 7. Update app_user role and tenant_id
            target_user.role = "TENANT_ADMIN"
            target_user.tenant_id = tenant_id
            
            db.commit()
            db.refresh(tenant_admin)
            
            return tenant_admin
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to assign tenant admin: {str(e)}"
            )

    # ==================== TENANT DOCUMENT MANAGEMENT ====================

    @staticmethod
    def upload_tenant_document(
        db: Session,
        user: AppUser,
        tenant_id: int,
        data: TenantDocumentUploadRequest
    ) -> TenantDocument:
        """Upload a tenant document (offline onboarding docs)"""
        
        # 1. Verify user is PLATFORM_ADMIN
        if user.role != "PLATFORM_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only platform admins can upload tenant documents"
            )
        
        # 2. Verify tenant exists
        tenant = (
            db.query(Tenant)
            .filter(Tenant.tenant_id == tenant_id)
            .first()
        )
        
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        # 3. Store document metadata (file already in private storage)
        doc = TenantDocument(
            tenant_id=tenant_id,
            document_type=data.document_type,
            file_name=data.file_name,
            file_url=data.file_url,
            file_hash=data.file_hash,
            is_active=True,
            created_by=user.user_id
        )
        
        db.add(doc)
        db.commit()
        db.refresh(doc)
        
        return doc
    
    @staticmethod
    def list_tenant_documents(
        db: Session,
        user: AppUser,
        tenant_id: int
    ) -> list:
        """List active documents for a tenant (platform admin only)"""
        
        # 1. Verify user is PLATFORM_ADMIN
        if user.role != "PLATFORM_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only platform admins can view tenant documents"
            )
        
        # 2. Verify tenant exists
        tenant = (
            db.query(Tenant)
            .filter(Tenant.tenant_id == tenant_id)
            .first()
        )
        
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        # 3. Fetch active documents only
        documents = (
            db.query(TenantDocument)
            .filter(
                TenantDocument.tenant_id == tenant_id,
                TenantDocument.is_active == True
            )
            .all()
        )
        
        return documents
    
    @staticmethod
    def get_tenant_document(
        db: Session,
        user: AppUser,
        tenant_id: int,
        document_id: int
    ) -> TenantDocument:
        """Get a specific tenant document (platform admin only)"""
        
        # 1. Verify user is PLATFORM_ADMIN
        if user.role != "PLATFORM_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only platform admins can access tenant documents"
            )
        
        # 2. Fetch document
        document = (
            db.query(TenantDocument)
            .filter(
                TenantDocument.document_id == document_id,
                TenantDocument.tenant_id == tenant_id
            )
            .first()
        )
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        return document

    # ==================== COUNTRY MANAGEMENT ====================

    @staticmethod
    def _require_platform_admin(user: AppUser):
        if user.role != "PLATFORM_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only platform admins can perform this action"
            )

    @staticmethod
    def create_country(db: Session, user: AppUser, data: CountryCreateRequest) -> Country:
        PlatformAdminService._require_platform_admin(user)

        code = data.country_code.upper()
        existing = db.query(Country).filter(Country.country_code == code).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Country code '{code}' already exists"
            )

        country = Country(
            country_code=code,
            name=data.name,
            phone_code=data.phone_code,
            default_timezone=data.default_timezone,
            default_currency=data.default_currency.upper(),
            created_by=user.user_id,
        )
        db.add(country)
        db.commit()
        db.refresh(country)
        return country

    @staticmethod
    def list_countries(db: Session, user: AppUser) -> list:
        PlatformAdminService._require_platform_admin(user)
        return db.query(Country).order_by(Country.name).all()

    @staticmethod
    def update_country(db: Session, user: AppUser, country_code: str, data: CountryUpdateRequest) -> Country:
        PlatformAdminService._require_platform_admin(user)

        country = db.query(Country).filter(Country.country_code == country_code.upper()).first()
        if not country:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Country not found")

        if data.name is not None:
            country.name = data.name
        if data.phone_code is not None:
            country.phone_code = data.phone_code
        if data.default_timezone is not None:
            country.default_timezone = data.default_timezone
        if data.default_currency is not None:
            country.default_currency = data.default_currency.upper()

        country.updated_by = user.user_id
        country.updated_on = datetime.now(tz.utc)
        db.commit()
        db.refresh(country)
        return country

    # ==================== CITY MANAGEMENT ====================

    @staticmethod
    def create_city(db: Session, user: AppUser, data: CityCreateRequest) -> City:
        PlatformAdminService._require_platform_admin(user)

        country = db.query(Country).filter(Country.country_code == data.country_code.upper()).first()
        if not country:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Country code does not exist")

        city = City(
            country_code=data.country_code.upper(),
            name=data.name,
            timezone=data.timezone,
            currency=data.currency.upper(),
            boundary_geojson=data.boundary_geojson or "{}",
            is_active=True,
            created_by=user.user_id,
        )
        db.add(city)
        db.commit()
        db.refresh(city)
        return city

    @staticmethod
    def list_cities(db: Session, user: AppUser, country_code: str = None) -> list:
        PlatformAdminService._require_platform_admin(user)

        q = db.query(City)
        if country_code:
            q = q.filter(City.country_code == country_code.upper())
        return q.order_by(City.name).all()

    @staticmethod
    def update_city(db: Session, user: AppUser, city_id: int, data: CityUpdateRequest) -> City:
        PlatformAdminService._require_platform_admin(user)

        city = db.query(City).filter(City.city_id == city_id).first()
        if not city:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="City not found")

        if data.name is not None:
            city.name = data.name
        if data.timezone is not None:
            city.timezone = data.timezone
        if data.currency is not None:
            city.currency = data.currency.upper()
        if data.boundary_geojson is not None:
            city.boundary_geojson = data.boundary_geojson
        if data.is_active is not None:
            city.is_active = data.is_active

        city.updated_by = user.user_id
        city.updated_on = datetime.now(tz.utc)
        db.commit()
        db.refresh(city)
        return city

    # ==================== FARE CONFIG MANAGEMENT ====================

    @staticmethod
    def create_fare_config(db: Session, user: AppUser, data: FareConfigCreateRequest) -> FareConfig:
        PlatformAdminService._require_platform_admin(user)

        # Validate city exists
        city = db.query(City).filter(City.city_id == data.city_id).first()
        if not city:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="City not found")

        # Validate currency matches city
        if data.currency.upper() != city.currency.upper():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Currency must match city currency ({city.currency})"
            )

        # Validate date range
        if data.effective_to and data.effective_from >= data.effective_to:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="effective_from must be before effective_to"
            )

        # Check for overlapping fare configs
        from sqlalchemy import and_, or_
        overlap_q = db.query(FareConfig).filter(
            FareConfig.city_id == data.city_id,
            FareConfig.vehicle_category == data.vehicle_category.upper(),
        )
        # Overlap condition: existing.effective_from < new.effective_to AND existing.effective_to > new.effective_from
        if data.effective_to:
            overlap_q = overlap_q.filter(
                FareConfig.effective_from < data.effective_to,
                or_(
                    FareConfig.effective_to.is_(None),
                    FareConfig.effective_to > data.effective_from
                )
            )
        else:
            # New config has no end date — overlaps if existing has no end or ends after new start
            overlap_q = overlap_q.filter(
                or_(
                    FareConfig.effective_to.is_(None),
                    FareConfig.effective_to > data.effective_from
                )
            )

        existing_overlap = overlap_q.first()
        if existing_overlap:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Overlapping fare config exists for this city + vehicle category + date range"
            )

        fare = FareConfig(
            city_id=data.city_id,
            vehicle_category=data.vehicle_category.upper(),
            currency=data.currency.upper(),
            base_fare=data.base_fare,
            per_km_rate=data.per_km_rate,
            per_min_rate=data.per_min_rate,
            minimum_fare=data.minimum_fare,
            booking_fee=data.booking_fee,
            surge_allowed=data.surge_allowed,
            night_charge_pct=data.night_charge_pct,
            effective_from=data.effective_from,
            effective_to=data.effective_to,
            created_by=user.user_id,
        )
        db.add(fare)
        db.commit()
        db.refresh(fare)
        return fare

    @staticmethod
    def list_fare_configs(db: Session, user: AppUser, city_id: int = None, vehicle_category: str = None) -> list:
        PlatformAdminService._require_platform_admin(user)

        q = db.query(FareConfig)
        if city_id:
            q = q.filter(FareConfig.city_id == city_id)
        if vehicle_category:
            q = q.filter(FareConfig.vehicle_category == vehicle_category.upper())
        return q.order_by(FareConfig.effective_from.desc()).all()

    @staticmethod
    def deactivate_fare_config(db: Session, user: AppUser, fare_config_id: int) -> FareConfig:
        PlatformAdminService._require_platform_admin(user)

        fare = db.query(FareConfig).filter(FareConfig.fare_config_id == fare_config_id).first()
        if not fare:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fare config not found")

        if fare.effective_to is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Fare config already has an end date"
            )

        fare.effective_to = datetime.now(tz.utc)
        db.commit()
        db.refresh(fare)
        return fare

    @staticmethod
    def update_fare_config(db: Session, user: AppUser, fare_config_id: int, data: FareConfigUpdateRequest) -> FareConfig:
        PlatformAdminService._require_platform_admin(user)

        fare = db.query(FareConfig).filter(FareConfig.fare_config_id == fare_config_id).first()
        if not fare:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fare config not found")

        if data.base_fare is not None:
            fare.base_fare = data.base_fare
        if data.per_km_rate is not None:
            fare.per_km_rate = data.per_km_rate
        if data.per_min_rate is not None:
            fare.per_min_rate = data.per_min_rate
        if data.minimum_fare is not None:
            fare.minimum_fare = data.minimum_fare
        if data.booking_fee is not None:
            fare.booking_fee = data.booking_fee
        if data.surge_allowed is not None:
            fare.surge_allowed = data.surge_allowed
        if data.night_charge_pct is not None:
            fare.night_charge_pct = data.night_charge_pct
        if data.effective_from is not None:
            fare.effective_from = data.effective_from
        if data.effective_to is not None:
            fare.effective_to = data.effective_to

        db.commit()
        db.refresh(fare)
        return fare

    # ==================== COMMISSION CONFIG MANAGEMENT ====================

    @staticmethod
    def create_commission_config(db: Session, user: AppUser, data: CommissionConfigCreateRequest) -> CommissionConfig:
        PlatformAdminService._require_platform_admin(user)

        # Validate city
        city = db.query(City).filter(City.city_id == data.city_id).first()
        if not city:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="City not found")

        # Validate currency
        if data.currency.upper() != city.currency.upper():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Currency must match city currency ({city.currency})"
            )

        # Validate commission_type
        ctype = data.commission_type.upper()
        if ctype not in ("FIXED", "PERCENTAGE"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="commission_type must be FIXED or PERCENTAGE"
            )

        if ctype == "FIXED" and not data.fixed_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="fixed_amount is required when commission_type is FIXED"
            )
        if ctype == "PERCENTAGE" and not data.percentage:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="percentage is required when commission_type is PERCENTAGE"
            )

        # Validate date range
        if data.effective_to and data.effective_from >= data.effective_to:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="effective_from must be before effective_to"
            )

        # Check for overlapping configs
        from sqlalchemy import or_
        overlap_q = db.query(CommissionConfig).filter(
            CommissionConfig.city_id == data.city_id,
            CommissionConfig.vehicle_category == data.vehicle_category.upper(),
            CommissionConfig.is_active == True,
        )
        if data.effective_to:
            overlap_q = overlap_q.filter(
                CommissionConfig.effective_from < data.effective_to,
                or_(
                    CommissionConfig.effective_to.is_(None),
                    CommissionConfig.effective_to > data.effective_from
                )
            )
        else:
            overlap_q = overlap_q.filter(
                or_(
                    CommissionConfig.effective_to.is_(None),
                    CommissionConfig.effective_to > data.effective_from
                )
            )

        if overlap_q.first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Overlapping commission config exists for this city + vehicle category + date range"
            )

        cc = CommissionConfig(
            commission_type=ctype,
            city_id=data.city_id,
            vehicle_category=data.vehicle_category.upper(),
            fixed_amount=data.fixed_amount or 0,
            percentage=data.percentage or 0,
            currency=data.currency.upper(),
            is_active=True,
            effective_from=data.effective_from,
            effective_to=data.effective_to,
            created_by=user.user_id,
        )
        db.add(cc)
        db.commit()
        db.refresh(cc)
        return cc

    @staticmethod
    def list_commission_configs(db: Session, user: AppUser, city_id: int = None, vehicle_category: str = None) -> list:
        PlatformAdminService._require_platform_admin(user)

        q = db.query(CommissionConfig).filter(CommissionConfig.is_active == True)
        if city_id:
            q = q.filter(CommissionConfig.city_id == city_id)
        if vehicle_category:
            q = q.filter(CommissionConfig.vehicle_category == vehicle_category.upper())
        return q.order_by(CommissionConfig.effective_from.desc()).all()

    @staticmethod
    def update_commission_config(db: Session, user: AppUser, config_id: int, data: CommissionConfigUpdateRequest) -> CommissionConfig:
        PlatformAdminService._require_platform_admin(user)

        cc = db.query(CommissionConfig).filter(CommissionConfig.id == config_id).first()
        if not cc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Commission config not found")

        if data.commission_type is not None:
            ctype = data.commission_type.upper()
            if ctype not in ("FIXED", "PERCENTAGE"):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="commission_type must be FIXED or PERCENTAGE")
            cc.commission_type = ctype
        if data.fixed_amount is not None:
            cc.fixed_amount = data.fixed_amount
        if data.percentage is not None:
            cc.percentage = data.percentage
        if data.effective_from is not None:
            cc.effective_from = data.effective_from
        if data.effective_to is not None:
            cc.effective_to = data.effective_to

        cc.updated_by = user.user_id
        cc.updated_on = datetime.now(tz.utc)
        db.commit()
        db.refresh(cc)
        return cc

    @staticmethod
    def deactivate_commission_config(db: Session, user: AppUser, config_id: int) -> CommissionConfig:
        PlatformAdminService._require_platform_admin(user)

        cc = db.query(CommissionConfig).filter(CommissionConfig.id == config_id).first()
        if not cc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Commission config not found")

        if not cc.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Commission config is already inactive"
            )

        cc.effective_to = datetime.now(tz.utc)
        cc.is_active = False
        cc.updated_by = user.user_id
        cc.updated_on = datetime.now(tz.utc)
        db.commit()
        db.refresh(cc)
        return cc
