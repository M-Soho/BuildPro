from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from app.models.material import MaterialCategory, UnitOfMeasure


class MaterialLineItemBase(BaseModel):
    category: MaterialCategory
    description: str = Field(..., min_length=1, max_length=500)
    quantity: Decimal = Field(default=0, ge=0)
    unit: UnitOfMeasure
    wastage_factor: Decimal = Field(default=0, ge=0, le=1)
    unit_cost: Decimal = Field(default=0, ge=0)
    notes: Optional[str] = None


class MaterialLineItemCreate(MaterialLineItemBase):
    project_id: UUID


class MaterialLineItemUpdate(BaseModel):
    category: Optional[MaterialCategory] = None
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    quantity: Optional[Decimal] = Field(None, ge=0)
    unit: Optional[UnitOfMeasure] = None
    wastage_factor: Optional[Decimal] = Field(None, ge=0, le=1)
    unit_cost: Optional[Decimal] = Field(None, ge=0)
    notes: Optional[str] = None


class MaterialLineItem(MaterialLineItemBase):
    id: UUID
    project_id: UUID
    total_qty: Decimal  # Computed server-side
    total_cost: Decimal  # Computed server-side
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Bulk import schemas
class MaterialImportRow(BaseModel):
    category: str
    description: str
    quantity: float
    unit: str
    wastage_factor: float = 0
    unit_cost: float = 0
    notes: Optional[str] = None


class MaterialImportRequest(BaseModel):
    project_id: UUID
    materials: list[MaterialImportRow]


class MaterialImportResponse(BaseModel):
    success_count: int
    error_count: int
    errors: list[dict] = []
    created_ids: list[UUID] = []


# Summary by category
class MaterialCategorySummary(BaseModel):
    category: MaterialCategory
    total_cost: Decimal
    item_count: int


class MaterialsSummary(BaseModel):
    total_cost: Decimal
    by_category: list[MaterialCategorySummary]
