from sqlalchemy.orm import Session
from app.models.core import Tenant


class TenantService:

    @staticmethod
    def get_active_tenants(db: Session):
        """Get all active tenants"""
        tenants = (
            db.query(Tenant)
            .filter(Tenant.status == "ACTIVE")
            .all()
        )
        return tenants
