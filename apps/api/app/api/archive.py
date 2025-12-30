from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_
from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from app.db.base import get_db
from app.models.project import BuildProject, ProjectStatus
from app.models.material import MaterialLineItem
from app.schemas.project import BuildProject as ProjectSchema
from app.middleware.rbac import get_current_tenant_id
from pydantic import BaseModel

router = APIRouter()


class SearchFilters(BaseModel):
    query: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    status: Optional[ProjectStatus] = None
    min_area: Optional[float] = None
    max_area: Optional[float] = None
    min_cost_per_sqft: Optional[float] = None
    max_cost_per_sqft: Optional[float] = None


class ProjectComparison(BaseModel):
    project_a: ProjectSchema
    project_b: ProjectSchema
    cost_per_sqft_diff: Optional[Decimal] = None
    area_diff: Optional[Decimal] = None
    budget_diff: Optional[Decimal] = None


@router.get("/search", response_model=List[ProjectSchema])
async def search_archive(
    request: Request,
    q: Optional[str] = Query(None, description="Search query (title, address, city)"),
    city: Optional[str] = None,
    state: Optional[str] = None,
    status: Optional[ProjectStatus] = None,
    min_area: Optional[float] = None,
    max_area: Optional[float] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
):
    """Search project archive with filters"""
    query = db.query(BuildProject).filter(
        BuildProject.tenant_id == tenant_id,
        BuildProject.deleted_at == None,
    )
    
    # Text search (simple LIKE for MVP - would use tsvector in production)
    if q:
        search_filter = or_(
            BuildProject.title.ilike(f"%{q}%"),
            BuildProject.address.ilike(f"%{q}%"),
            BuildProject.city.ilike(f"%{q}%"),
        )
        query = query.filter(search_filter)
    
    # Filters
    if city:
        query = query.filter(BuildProject.city.ilike(f"%{city}%"))
    
    if state:
        query = query.filter(BuildProject.state == state)
    
    if status:
        query = query.filter(BuildProject.status == status)
    
    if min_area is not None:
        query = query.filter(BuildProject.home_area_sqft >= min_area)
    
    if max_area is not None:
        query = query.filter(BuildProject.home_area_sqft <= max_area)
    
    projects = query.offset(skip).limit(limit).all()
    return projects


@router.get("/compare", response_model=ProjectComparison)
async def compare_projects(
    request: Request,
    project_a_id: UUID = Query(..., description="First project ID"),
    project_b_id: UUID = Query(..., description="Second project ID"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
):
    """Compare two projects"""
    project_a = (
        db.query(BuildProject)
        .filter(
            BuildProject.id == project_a_id,
            BuildProject.tenant_id == tenant_id,
        )
        .first()
    )
    
    project_b = (
        db.query(BuildProject)
        .filter(
            BuildProject.id == project_b_id,
            BuildProject.tenant_id == tenant_id,
        )
        .first()
    )
    
    if not project_a or not project_b:
        raise HTTPException(status_code=404, detail="One or both projects not found")
    
    # Calculate metrics
    cost_per_sqft_a = None
    cost_per_sqft_b = None
    cost_per_sqft_diff = None
    
    if project_a.home_area_sqft and project_a.budget:
        cost_per_sqft_a = project_a.budget / project_a.home_area_sqft
    
    if project_b.home_area_sqft and project_b.budget:
        cost_per_sqft_b = project_b.budget / project_b.home_area_sqft
    
    if cost_per_sqft_a and cost_per_sqft_b:
        cost_per_sqft_diff = cost_per_sqft_b - cost_per_sqft_a
    
    area_diff = None
    if project_a.home_area_sqft and project_b.home_area_sqft:
        area_diff = project_b.home_area_sqft - project_a.home_area_sqft
    
    budget_diff = None
    if project_a.budget and project_b.budget:
        budget_diff = project_b.budget - project_a.budget
    
    return ProjectComparison(
        project_a=project_a,
        project_b=project_b,
        cost_per_sqft_diff=cost_per_sqft_diff,
        area_diff=area_diff,
        budget_diff=budget_diff,
    )
