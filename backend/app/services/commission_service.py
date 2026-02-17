"""
Commission Service - Fetch and calculate commission rates from commission_config table.

Commission Model (FINAL):
- All percentages calculated from TOTAL FARE (F)
- No fixed commission (percentage only)
- No cascading percentage

Formula:
    platform_commission = F * platform_percentage
    tenant_commission   = F * tenant_percentage
    fleet_commission    = F * fleet_percentage (if applicable)
    driver_earning      = F - (platform + tenant + fleet)
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException, status
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, Dict

from app.models.financial import CommissionConfig


class CommissionService:
    """Service for fetching and calculating commission rates."""
    
    @staticmethod
    def get_commission_rate(
        db: Session,
        commission_type: str,
        tenant_id: Optional[int] = None,
        city_id: Optional[int] = None,
        vehicle_category: Optional[str] = None,
        currency: str = 'INR'
    ) -> Decimal:
        """
        Get commission percentage for a specific type.
        
        Lookup order (most specific to least):
        1. tenant_id + city_id + vehicle_category
        2. tenant_id + city_id
        3. tenant_id + vehicle_category
        4. tenant_id only
        5. city_id + vehicle_category
        6. city_id only
        7. vehicle_category only
        8. Global default (no filters)
        
        Returns the percentage as Decimal (e.g., 0.20 for 20%)
        """
        now = datetime.now(timezone.utc)
        
        # Build base query
        base_query = (
            db.query(CommissionConfig)
            .filter(
                CommissionConfig.commission_type == commission_type,
                CommissionConfig.is_active == True,
                CommissionConfig.effective_from <= now,
                or_(
                    CommissionConfig.effective_to.is_(None),
                    CommissionConfig.effective_to > now
                )
            )
        )
        
        # Try most specific to least specific
        lookups = []
        
        # 1. All filters
        if tenant_id and city_id and vehicle_category:
            lookups.append((tenant_id, city_id, vehicle_category))
        
        # 2. tenant + city
        if tenant_id and city_id:
            lookups.append((tenant_id, city_id, None))
        
        # 3. tenant + vehicle
        if tenant_id and vehicle_category:
            lookups.append((tenant_id, None, vehicle_category))
        
        # 4. tenant only
        if tenant_id:
            lookups.append((tenant_id, None, None))
        
        # 5. city + vehicle
        if city_id and vehicle_category:
            lookups.append((None, city_id, vehicle_category))
        
        # 6. city only
        if city_id:
            lookups.append((None, city_id, None))
        
        # 7. vehicle only
        if vehicle_category:
            lookups.append((None, None, vehicle_category))
        
        # 8. Global default
        lookups.append((None, None, None))
        
        for t_id, c_id, v_cat in lookups:
            query = base_query
            
            if t_id is not None:
                query = query.filter(CommissionConfig.tenant_id == t_id)
            else:
                query = query.filter(CommissionConfig.tenant_id.is_(None))
            
            if c_id is not None:
                query = query.filter(CommissionConfig.city_id == c_id)
            else:
                query = query.filter(CommissionConfig.city_id.is_(None))
            
            if v_cat is not None:
                query = query.filter(CommissionConfig.vehicle_category == v_cat)
            else:
                query = query.filter(CommissionConfig.vehicle_category.is_(None))
            
            config = query.first()
            
            if config:
                print(f"✓ Found config: type={commission_type}, tenant={t_id}, city={c_id}, vehicle={v_cat}, percentage={config.percentage}")
                return Decimal(str(config.percentage))
        
        # No config found, return 0
        print(f"✗ No config found for: type={commission_type}, tenant_id={tenant_id}, city_id={city_id}, vehicle_category={vehicle_category}")
        return Decimal('0')
    
    @staticmethod
    def get_all_commission_rates(
        db: Session,
        tenant_id: Optional[int] = None,
        city_id: Optional[int] = None,
        vehicle_category: Optional[str] = None,
        currency: str = 'INR'
    ) -> Dict[str, Decimal]:
        """
        Get all commission rates (platform, tenant, fleet).
        
        Returns dict with keys: platform_percentage, tenant_percentage, fleet_percentage
        """
        return {
            'platform_percentage': CommissionService.get_commission_rate(
                db, 'platform', tenant_id, city_id, vehicle_category, currency
            ),
            'tenant_percentage': CommissionService.get_commission_rate(
                db, 'tenant', tenant_id, city_id, vehicle_category, currency
            ),
            'fleet_percentage': CommissionService.get_commission_rate(
                db, 'fleet', tenant_id, city_id, vehicle_category, currency
            )
        }
    
    @staticmethod
    def calculate_fare_split(
        db: Session,
        total_fare: Decimal,
        tenant_id: Optional[int] = None,
        city_id: Optional[int] = None,
        vehicle_category: Optional[str] = None,
        has_fleet: bool = False,
        currency: str = 'INR'
    ) -> Dict:
        """
        Calculate complete fare split using DB commission rates.
        
        Formula:
            platform_commission = F * platform_percentage
            tenant_commission   = F * tenant_percentage
            fleet_commission    = F * fleet_percentage (if has_fleet)
            driver_earning      = F - (platform + tenant + fleet)
        
        Args:
            db: Database session
            total_fare: Total trip fare (F)
            tenant_id: Tenant ID for specific rates
            city_id: City ID for specific rates
            vehicle_category: Vehicle category for specific rates
            has_fleet: Whether driver belongs to a BUSINESS fleet
            currency: Currency code
        
        Returns:
            Dict with fare split details
        """
        F = Decimal(str(total_fare))
        
        print("===== INSIDE calculate_fare_split =====")
        print(f"total_fare: {F}")
        print(f"tenant_id: {tenant_id}")
        print(f"city_id: {city_id}")
        print(f"vehicle_category: {vehicle_category}")
        print(f"has_fleet: {has_fleet}")
        print(f"currency: {currency}")
        
        # Get rates from DB
        rates = CommissionService.get_all_commission_rates(
            db, tenant_id, city_id, vehicle_category, currency
        )
        
        print(f"Rates fetched: {rates}")
        print(f"platform_percentage: {rates['platform_percentage']}")
        print(f"tenant_percentage: {rates['tenant_percentage']}")
        print(f"fleet_percentage: {rates['fleet_percentage']}")
        print("=======================================")
        
        # Calculate commissions from total fare
        platform_commission = (F * rates['platform_percentage']).quantize(Decimal('0.01'))
        tenant_commission = (F * rates['tenant_percentage']).quantize(Decimal('0.01'))
        
        # Fleet commission only if driver is in BUSINESS fleet
        if has_fleet:
            fleet_commission = (F * rates['fleet_percentage']).quantize(Decimal('0.01'))
        else:
            fleet_commission = Decimal('0.00')
        
        # Driver earning = Total - all commissions
        driver_earning = F - platform_commission - tenant_commission - fleet_commission
        
        # Ensure driver earning is not negative
        if driver_earning < 0:
            driver_earning = Decimal('0.00')
        
        return {
            'total_fare': F,
            'platform_commission': platform_commission,
            'tenant_commission': tenant_commission,
            'fleet_commission': fleet_commission,
            'driver_earning': driver_earning,
            'currency': currency,
            'rates': {
                'platform_percentage': float(rates['platform_percentage']),
                'tenant_percentage': float(rates['tenant_percentage']),
                'fleet_percentage': float(rates['fleet_percentage']) if has_fleet else 0
            }
        }
