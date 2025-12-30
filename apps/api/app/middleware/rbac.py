from fastapi import Request, HTTPException, status, Depends
from sqlalchemy.orm import Session
from functools import wraps
from typing import Optional
from app.models.user import UserRole
from app.db.base import get_db


# Role hierarchy (higher value = more permissions)
ROLE_HIERARCHY = {
    UserRole.OWNER: 6,
    UserRole.ADMIN: 5,
    UserRole.PM: 4,
    UserRole.SUPERVISOR: 3,
    UserRole.ESTIMATOR: 2,
    UserRole.SUB: 1,
}


def get_current_tenant_id(request: Request) -> str:
    """Dependency to get current tenant ID from request state"""
    tenant_id = getattr(request.state, "tenant_id", None)
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tenant context not found. Authentication required.",
        )
    return tenant_id


def get_current_user_id(request: Request) -> str:
    """Dependency to get current user ID from request state"""
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User context not found. Authentication required.",
        )
    return user_id


def get_current_user_role(request: Request) -> UserRole:
    """Dependency to get current user role from request state"""
    role = getattr(request.state, "user_role", None)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User role not found. Authentication required.",
        )
    return UserRole(role)


def require_role(min_role: UserRole):
    """
    Dependency factory to require a minimum role level
    Usage: Depends(require_role(UserRole.PM))
    """
    def check_role(current_role: UserRole = Depends(get_current_user_role)) -> UserRole:
        if ROLE_HIERARCHY.get(current_role, 0) < ROLE_HIERARCHY.get(min_role, 0):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {min_role.value}, Current: {current_role.value}",
            )
        return current_role
    return check_role


def enforce_tenant_isolation(query, model, tenant_id: str):
    """
    Helper to enforce tenant isolation on queries
    Usage: query = enforce_tenant_isolation(query, BuildProject, tenant_id)
    """
    if hasattr(model, "tenant_id"):
        return query.filter(model.tenant_id == tenant_id)
    return query


class TenantContext:
    """Context manager for tenant-scoped queries"""
    
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
    
    def query(self, model):
        """Create a tenant-scoped query"""
        query = self.db.query(model)
        if hasattr(model, "tenant_id"):
            query = query.filter(model.tenant_id == self.tenant_id)
        return query
    
    def get(self, model, id: str):
        """Get a single record by ID with tenant isolation"""
        query = self.query(model).filter(model.id == id)
        return query.first()
