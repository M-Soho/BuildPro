from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import datetime, date
from app.db.base import get_db
from app.models.schedule import ScheduleMilestone
from app.models.project import BuildProject
from app.schemas.schedule import (
    ScheduleMilestone as MilestoneSchema,
    ScheduleMilestoneCreate,
    ScheduleMilestoneUpdate,
    ScheduleVariance,
    ProjectScheduleSummary,
)
from app.middleware.rbac import get_current_tenant_id, get_current_user_id
from app.utils.calculations import ConstructionCalculator
from app.utils.audit import AuditLogger, dict_from_model
from decimal import Decimal

router = APIRouter()


@router.post("/", response_model=MilestoneSchema, status_code=status.HTTP_201_CREATED)
async def create_milestone(
    milestone: ScheduleMilestoneCreate,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
    user_id: str = Depends(get_current_user_id),
):
    """Create a new schedule milestone"""
    # Verify project
    project = (
        db.query(BuildProject)
        .filter(
            BuildProject.id == milestone.project_id,
            BuildProject.tenant_id == tenant_id,
        )
        .first()
    )
    
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    db_milestone = ScheduleMilestone(**milestone.model_dump())
    db.add(db_milestone)
    db.commit()
    db.refresh(db_milestone)
    
    audit = AuditLogger(db, tenant_id, user_id)
    audit.log_create("ScheduleMilestone", str(db_milestone.id), dict_from_model(db_milestone))
    
    return db_milestone


@router.get("/", response_model=List[MilestoneSchema])
async def list_milestones(
    request: Request,
    project_id: UUID,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
):
    """List milestones for a project"""
    project = (
        db.query(BuildProject)
        .filter(BuildProject.id == project_id, BuildProject.tenant_id == tenant_id)
        .first()
    )
    
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    milestones = (
        db.query(ScheduleMilestone)
        .filter(
            ScheduleMilestone.project_id == project_id,
            ScheduleMilestone.deleted_at == None,
        )
        .all()
    )
    
    return milestones


@router.patch("/{milestone_id}", response_model=MilestoneSchema)
async def update_milestone(
    milestone_id: UUID,
    milestone_update: ScheduleMilestoneUpdate,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
    user_id: str = Depends(get_current_user_id),
):
    """Update milestone"""
    db_milestone = (
        db.query(ScheduleMilestone)
        .join(BuildProject)
        .filter(
            ScheduleMilestone.id == milestone_id,
            BuildProject.tenant_id == tenant_id,
            ScheduleMilestone.deleted_at == None,
        )
        .first()
    )
    
    if not db_milestone:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found")
    
    before = dict_from_model(db_milestone)
    update_data = milestone_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_milestone, field, value)
    
    db.commit()
    db.refresh(db_milestone)
    
    audit = AuditLogger(db, tenant_id, user_id)
    audit.log_update("ScheduleMilestone", str(db_milestone.id), before, dict_from_model(db_milestone))
    
    return db_milestone


@router.get("/variance/{project_id}", response_model=ProjectScheduleSummary)
async def get_schedule_variance(
    project_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
):
    """Get schedule variance analysis for a project"""
    project = (
        db.query(BuildProject)
        .filter(BuildProject.id == project_id, BuildProject.tenant_id == tenant_id)
        .first()
    )
    
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    milestones = (
        db.query(ScheduleMilestone)
        .filter(
            ScheduleMilestone.project_id == project_id,
            ScheduleMilestone.deleted_at == None,
        )
        .all()
    )
    
    variances = []
    completed_count = 0
    total_percent = Decimal('0')
    
    for milestone in milestones:
        if milestone.percent_complete == 100:
            completed_count += 1
        
        total_percent += milestone.percent_complete
        
        # Calculate variance
        actual_date = milestone.actual_end_date or date.today()
        variance_days = ConstructionCalculator.schedule_variance_days(
            milestone.baseline_end_date.isoformat(),
            milestone.actual_end_date.isoformat() if milestone.actual_end_date else None,
        )
        
        variances.append(
            ScheduleVariance(
                milestone_id=milestone.id,
                phase=milestone.phase,
                variance_days=variance_days,
                is_late=variance_days < 0,
                baseline_end_date=milestone.baseline_end_date,
                actual_or_current_date=actual_date,
            )
        )
    
    avg_complete = total_percent / len(milestones) if milestones else Decimal('0')
    
    return ProjectScheduleSummary(
        project_id=project_id,
        total_milestones=len(milestones),
        completed_milestones=completed_count,
        avg_percent_complete=avg_complete,
        variances=variances,
    )
