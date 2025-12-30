from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.db.base import get_db
from app.models.user import User, Membership
from app.schemas.user import (
    User as UserSchema,
    UserCreate,
    UserUpdate,
    Membership as MembershipSchema,
    CurrentUserResponse,
)
from app.middleware.rbac import get_current_tenant_id, get_current_user_id
from app.auth.jwt import get_current_user_from_token

router = APIRouter()


@router.get("/me", response_model=CurrentUserResponse)
async def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    claims: dict = Depends(get_current_user_from_token),
):
    """Get current user profile and memberships"""
    user_id = get_current_user_id(request)
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    memberships = db.query(Membership).filter(Membership.user_id == user_id).all()
    
    return CurrentUserResponse(
        user=user,
        memberships=memberships,
        current_tenant_id=getattr(request.state, "tenant_id", None),
    )


@router.get("/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
):
    """Get user by ID (tenant-scoped via memberships)"""
    # Verify user belongs to tenant
    membership = (
        db.query(Membership)
        .filter(Membership.user_id == user_id, Membership.tenant_id == tenant_id)
        .first()
    )
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in this tenant",
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    return user


@router.get("/", response_model=List[UserSchema])
async def list_users(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
):
    """List all users in the current tenant"""
    # Get user IDs in this tenant
    memberships = db.query(Membership).filter(Membership.tenant_id == tenant_id).all()
    user_ids = [m.user_id for m in memberships]
    
    users = (
        db.query(User)
        .filter(User.id.in_(user_ids))
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    return users
