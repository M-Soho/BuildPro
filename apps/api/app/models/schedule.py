from sqlalchemy import Column, String, DateTime, ForeignKey, Date, Numeric, Enum as SQLEnum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum
from app.db.base import Base


class MilestonePhase(str, enum.Enum):
    SITEWORK = "SITEWORK"
    FOUNDATION = "FOUNDATION"
    FRAMING = "FRAMING"
    ROUGH_IN = "ROUGH_IN"
    INSULATION = "INSULATION"
    DRYWALL = "DRYWALL"
    INTERIOR_FINISH = "INTERIOR_FINISH"
    EXTERIOR_FINISH = "EXTERIOR_FINISH"
    FINAL = "FINAL"


class ScheduleMilestone(Base):
    __tablename__ = "schedule_milestones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("build_projects.id", ondelete="CASCADE"), nullable=False)
    
    phase = Column(SQLEnum(MilestonePhase), nullable=False)
    description = Column(String(500))
    
    baseline_start_date = Column(Date, nullable=False)
    baseline_end_date = Column(Date, nullable=False)
    actual_start_date = Column(Date)
    actual_end_date = Column(Date)
    
    percent_complete = Column(Numeric(5, 2), nullable=False, default=0)  # 0.00 to 100.00
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    project = relationship("BuildProject", back_populates="milestones")

    # Indexes
    __table_args__ = (
        Index("ix_milestone_project", "project_id"),
        Index("ix_milestone_project_deleted", "project_id", "deleted_at"),
        Index("ix_milestone_phase", "phase"),
    )

    def __repr__(self):
        return f"<ScheduleMilestone {self.phase}>"
