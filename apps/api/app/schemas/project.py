from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID
from app.models.project import ProjectStatus


# BuildProject Schemas
class BuildProjectBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=50)
    zip_code: Optional[str] = Field(None, max_length=20)
    status: ProjectStatus = ProjectStatus.PLANNING
    home_area_sqft: Optional[Decimal] = Field(None, ge=0)
    budget: Optional[Decimal] = Field(None, ge=0)
    baseline_start_date: Optional[date] = None
    baseline_end_date: Optional[date] = None
    actual_start_date: Optional[date] = None
    actual_end_date: Optional[date] = None


class BuildProjectCreate(BuildProjectBase):
    pass


class BuildProjectUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=50)
    zip_code: Optional[str] = Field(None, max_length=20)
    status: Optional[ProjectStatus] = None
    home_area_sqft: Optional[Decimal] = Field(None, ge=0)
    budget: Optional[Decimal] = Field(None, ge=0)
    baseline_start_date: Optional[date] = None
    baseline_end_date: Optional[date] = None
    actual_start_date: Optional[date] = None
    actual_end_date: Optional[date] = None


class BuildProject(BuildProjectBase):
    id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Lot Schemas
class LotBase(BaseModel):
    lot_number: str = Field(..., min_length=1, max_length=50)
    address: Optional[str] = Field(None, max_length=500)
    area_sqft: Optional[Decimal] = Field(None, ge=0)


class LotCreate(LotBase):
    project_id: UUID


class LotUpdate(BaseModel):
    lot_number: Optional[str] = Field(None, min_length=1, max_length=50)
    address: Optional[str] = Field(None, max_length=500)
    area_sqft: Optional[Decimal] = Field(None, ge=0)


class Lot(LotBase):
    id: UUID
    project_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Project with related data
class BuildProjectDetail(BuildProject):
    lots: list[Lot] = []


# Clone project request
class CloneProjectRequest(BaseModel):
    source_project_id: UUID
    new_title: str = Field(..., min_length=1)
    clone_materials: bool = True
    clone_schedule: bool = True
