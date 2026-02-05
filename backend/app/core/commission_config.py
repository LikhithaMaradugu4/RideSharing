"""
Commission Configuration - Fare Split Settings

This file contains all commission values for the platform.
These values are intentionally file-based (not in DB) for simplicity.
No admin APIs are needed - edit this file directly to change commissions.

Hybrid formula: commission = max(fixed_amount, percentage * base_amount)
"""

from typing import Optional
from decimal import Decimal

# =====================================
# COMMISSION CONFIGURATION
# =====================================

# Platform commission (deducted first from total fare)
PLATFORM_COMMISSION = {
    "fixed": Decimal("20.00"),      # Minimum ₹20
    "percentage": Decimal("0.20")   # 20% of fare
}

# Tenant commission (deducted after platform)
TENANT_COMMISSION = {
    "fixed": Decimal("10.00"),      # Minimum ₹10
    "percentage": Decimal("0.10")   # 10% of remaining
}

# Fleet commission (deducted after tenant, only if driver belongs to a fleet)
FLEET_COMMISSION = {
    "fixed": Decimal("15.00"),      # Minimum ₹15
    "percentage": Decimal("0.15")   # 15% of remaining
}


# =====================================
# HELPER FUNCTIONS
# =====================================

def get_platform_commission() -> dict:
    """Get platform commission config."""
    return PLATFORM_COMMISSION


def get_tenant_commission() -> dict:
    """Get tenant commission config."""
    return TENANT_COMMISSION


def get_fleet_commission() -> dict:
    """Get fleet commission config."""
    return FLEET_COMMISSION


def calculate_hybrid_commission(base_amount: Decimal, config: dict) -> Decimal:
    """
    Calculate commission using hybrid formula.
    
    Hybrid formula: commission = max(fixed_amount, percentage * base_amount)
    
    Args:
        base_amount: The base amount to calculate commission from
        config: Commission config dict with 'fixed' and 'percentage' keys
    
    Returns:
        Commission amount (Decimal)
    """
    fixed = config.get("fixed", Decimal("0"))
    percentage = config.get("percentage", Decimal("0"))
    
    percentage_amount = base_amount * percentage
    
    return max(fixed, percentage_amount)


def calculate_fare_split(
    final_fare: Decimal,
    has_fleet: bool = False
) -> dict:
    """
    Calculate complete fare split.
    
    Split order:
    1. Platform commission (from total fare)
    2. Tenant commission (from remainder after platform)
    3. Fleet commission (from remainder after tenant, only if has_fleet=True)
    4. Driver earning (what's left)
    
    Invariant: platform + tenant + fleet + driver = final_fare
    
    Args:
        final_fare: Total trip fare (F)
        has_fleet: Whether driver belongs to a fleet
    
    Returns:
        Dict with platform_commission, tenant_commission, fleet_commission, driver_earning
    """
    F = Decimal(str(final_fare))
    
    # Platform commission (from F)
    platform_commission = calculate_hybrid_commission(F, PLATFORM_COMMISSION)
    # Cap at available amount
    platform_commission = min(platform_commission, F)
    R1 = F - platform_commission
    
    # Tenant commission (from R1)
    tenant_commission = calculate_hybrid_commission(R1, TENANT_COMMISSION)
    # Cap at available amount
    tenant_commission = min(tenant_commission, R1)
    R2 = R1 - tenant_commission
    
    # Fleet commission (from R2, only if driver has fleet)
    if has_fleet:
        fleet_commission = calculate_hybrid_commission(R2, FLEET_COMMISSION)
        # Cap at available amount
        fleet_commission = min(fleet_commission, R2)
        R3 = R2 - fleet_commission
    else:
        fleet_commission = Decimal("0")
        R3 = R2
    
    # Driver earning is what remains
    driver_earning = R3
    
    # Round all values to 2 decimal places
    result = {
        "platform_commission": round(platform_commission, 2),
        "tenant_commission": round(tenant_commission, 2),
        "fleet_commission": round(fleet_commission, 2),
        "driver_earning": round(driver_earning, 2),
        "total": round(F, 2)
    }
    
    # Verify invariant: all splits sum to total fare
    splits_sum = (
        result["platform_commission"] + 
        result["tenant_commission"] + 
        result["fleet_commission"] + 
        result["driver_earning"]
    )
    
    # Handle any rounding differences by adjusting driver earning
    if splits_sum != result["total"]:
        diff = result["total"] - splits_sum
        result["driver_earning"] += diff
    
    return result
