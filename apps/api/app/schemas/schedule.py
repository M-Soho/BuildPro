from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID
from app.models.schedule import MilestonePhase


class ScheduleMilestoneBase(BaseModel):
    phase: MilestonePhase
    description: Optional[str] = Field(None, max_length=500)
    baseline_start_date: date
    baseline_end_date: date
    actual_start_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    percent_complete: Decimal = Field(default=0, ge=0, le=100)


class ScheduleMilestoneCreate(ScheduleMilestoneBase):
    project_id: UUID


class ScheduleMilestoneUpdate(BaseModel):
    phase: Optional[MilestonePhase] = None
    description: Optional[str] = Field(None, max_length=500)
    baseline_start_date: Optional[date] = None
    baseline_end_date: Optional[date] = None
    actual_start_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    percent_complete: Optional[Decimal] = Field(None, ge=0, le=100)


class ScheduleMilestone(ScheduleMilestoneBase):
    id: UUID
    project_id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Schedule variance calculation
class ScheduleVariance(BaseModel):
    milestone_id: UUID
    phase: MilestonePhase
    variance_days: int
    is_late: bool
    baseline_end_date: date
    actual_or_current_date: date


class ProjectScheduleSummary(BaseModel):
    project_id: UUID
    total_milestones: int
    completed_milestones: int
    avg_percent_complete: Decimal
    variances: list[ScheduleVariance]
