from fastapi import APIRouter, Depends, HTTPException, Request, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from app.db.base import get_db
from app.models.project import BuildProject, Lot, ProjectStatus
from app.models.material import MaterialLineItem
from app.models.schedule import ScheduleMilestone
from app.schemas.project import (
    BuildProject as ProjectSchema,
    BuildProjectCreate,
    BuildProjectUpdate,
    BuildProjectDetail,
    CloneProjectRequest,
    Lot as LotSchema,
    LotCreate,
    LotUpdate,
)
from app.middleware.rbac import get_current_tenant_id, get_current_user_id, require_role
from app.models.user import UserRole
from app.utils.audit import AuditLogger, dict_from_model
from app.models.audit import AuditAction

router = APIRouter()


@router.post("/", response_model=ProjectSchema, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: BuildProjectCreate,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
    user_id: str = Depends(get_current_user_id),
    _: UserRole = Depends(require_role(UserRole.PM)),
):
    """Create a new project"""
    db_project = BuildProject(
        **project.model_dump(),
        tenant_id=tenant_id,
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    # Audit log
    audit = AuditLogger(db, tenant_id, user_id)
    audit.log_create("BuildProject", str(db_project.id), dict_from_model(db_project))
    
    return db_project


@router.get("/", response_model=List[ProjectSchema])
async def list_projects(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[ProjectStatus] = None,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
):
    """List all projects (with optional status filter)"""
    query = db.query(BuildProject).filter(
        BuildProject.tenant_id == tenant_id,
        BuildProject.deleted_at == None,
    )
    
    if status_filter:
        query = query.filter(BuildProject.status == status_filter)
    
    projects = query.offset(skip).limit(limit).all()
    return projects


@router.get("/{project_id}", response_model=BuildProjectDetail)
async def get_project(
    project_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
):
    """Get project by ID with related data"""
    project = (
        db.query(BuildProject)
        .filter(
            BuildProject.id == project_id,
            BuildProject.tenant_id == tenant_id,
            BuildProject.deleted_at == None,
        )
        .first()
    )
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    
    return project


@router.patch("/{project_id}", response_model=ProjectSchema)
async def update_project(
    project_id: UUID,
    project_update: BuildProjectUpdate,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
    user_id: str = Depends(get_current_user_id),
    _: UserRole = Depends(require_role(UserRole.PM)),
):
    """Update project"""
    db_project = (
        db.query(BuildProject)
        .filter(
            BuildProject.id == project_id,
            BuildProject.tenant_id == tenant_id,
            BuildProject.deleted_at == None,
        )
        .first()
    )
    
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    
    # Store old values for audit
    before = dict_from_model(db_project)
    
    # Update fields
    update_data = project_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_project, field, value)
    
    db.commit()
    db.refresh(db_project)
    
    # Audit log
    audit = AuditLogger(db, tenant_id, user_id)
    audit.log_update("BuildProject", str(db_project.id), before, dict_from_model(db_project))
    
    return db_project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
    user_id: str = Depends(get_current_user_id),
    _: UserRole = Depends(require_role(UserRole.ADMIN)),
):
    """Soft delete project"""
    db_project = (
        db.query(BuildProject)
        .filter(
            BuildProject.id == project_id,
            BuildProject.tenant_id == tenant_id,
            BuildProject.deleted_at == None,
        )
        .first()
    )
    
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    
    # Soft delete
    db_project.deleted_at = datetime.utcnow()
    db.commit()
    
    # Audit log
    audit = AuditLogger(db, tenant_id, user_id)
    audit.log_delete("BuildProject", str(db_project.id), dict_from_model(db_project))
    
    return None


@router.post("/{project_id}/clone", response_model=ProjectSchema)
async def clone_project(
    project_id: UUID,
    clone_request: CloneProjectRequest,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
    user_id: str = Depends(get_current_user_id),
    _: UserRole = Depends(require_role(UserRole.PM)),
):
    """Clone a project (optionally with materials and schedule)"""
    # Get source project
    source_project = (
        db.query(BuildProject)
        .filter(
            BuildProject.id == clone_request.source_project_id,
            BuildProject.tenant_id == tenant_id,
            BuildProject.deleted_at == None,
        )
        .first()
    )
    
    if not source_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source project not found",
        )
    
    # Create new project
    new_project = BuildProject(
        tenant_id=tenant_id,
        title=clone_request.new_title,
        address=source_project.address,
        city=source_project.city,
        state=source_project.state,
        zip_code=source_project.zip_code,
        status=ProjectStatus.PLANNING,
        home_area_sqft=source_project.home_area_sqft,
        budget=source_project.budget,
    )
    db.add(new_project)
    db.flush()
    
    # Clone materials if requested
    if clone_request.clone_materials:
        source_materials = (
            db.query(MaterialLineItem)
            .filter(
                MaterialLineItem.project_id == source_project.id,
                MaterialLineItem.deleted_at == None,
            )
            .all()
        )
        
        for material in source_materials:
            new_material = MaterialLineItem(
                project_id=new_project.id,
                category=material.category,
                description=material.description,
                quantity=material.quantity,
                unit=material.unit,
                wastage_factor=material.wastage_factor,
                total_qty=material.total_qty,
                unit_cost=material.unit_cost,
                total_cost=material.total_cost,
                notes=material.notes,
            )
            db.add(new_material)
    
    # Clone schedule if requested
    if clone_request.clone_schedule:
        source_milestones = (
            db.query(ScheduleMilestone)
            .filter(
                ScheduleMilestone.project_id == source_project.id,
                ScheduleMilestone.deleted_at == None,
            )
            .all()
        )
        
        for milestone in source_milestones:
            new_milestone = ScheduleMilestone(
                project_id=new_project.id,
                phase=milestone.phase,
                description=milestone.description,
                baseline_start_date=milestone.baseline_start_date,
                baseline_end_date=milestone.baseline_end_date,
                percent_complete=0,  # Reset completion
            )
            db.add(new_milestone)
    
    db.commit()
    db.refresh(new_project)
    
    # Audit log
    audit = AuditLogger(db, tenant_id, user_id)
    audit.log_create(
        "BuildProject",
        str(new_project.id),
        {**dict_from_model(new_project), "cloned_from": str(source_project.id)},
    )
    
    return new_project


# Lot endpoints
@router.post("/{project_id}/lots", response_model=LotSchema)
async def create_lot(
    project_id: UUID,
    lot: LotCreate,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
    user_id: str = Depends(get_current_user_id),
):
    """Add a lot to a project"""
    # Verify project exists and belongs to tenant
    project = (
        db.query(BuildProject)
        .filter(
            BuildProject.id == project_id,
            BuildProject.tenant_id == tenant_id,
            BuildProject.deleted_at == None,
        )
        .first()
    )
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    
    db_lot = Lot(**lot.model_dump())
    db.add(db_lot)
    db.commit()
    db.refresh(db_lot)
    
    return db_lot


@router.get("/{project_id}/lots", response_model=List[LotSchema])
async def list_lots(
    project_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
):
    """List all lots for a project"""
    # Verify project access
    project = (
        db.query(BuildProject)
        .filter(
            BuildProject.id == project_id,
            BuildProject.tenant_id == tenant_id,
        )
        .first()
    )
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    
    lots = db.query(Lot).filter(Lot.project_id == project_id).all()
    return lots
