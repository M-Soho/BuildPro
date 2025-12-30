from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.user import UserRole


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)


class UserCreate(UserBase):
    external_id: Optional[str] = None


class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)


class User(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Membership Schemas
class MembershipBase(BaseModel):
    role: UserRole


class MembershipCreate(MembershipBase):
    tenant_id: UUID
    user_id: UUID


class MembershipUpdate(BaseModel):
    role: Optional[UserRole] = None


class Membership(MembershipBase):
    id: UUID
    tenant_id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# User with memberships
class UserWithMemberships(User):
    memberships: list[Membership] = []


# /me endpoint response
class CurrentUserResponse(BaseModel):
    user: User
    memberships: list[Membership]
    current_tenant_id: Optional[UUID] = None
