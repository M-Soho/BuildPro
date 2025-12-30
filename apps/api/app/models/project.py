from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Date, Enum as SQLEnum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum
from app.db.base import Base


class ProjectStatus(str, enum.Enum):
    PLANNING = "PLANNING"
    ACTIVE = "ACTIVE"
    ON_HOLD = "ON_HOLD"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"


class BuildProject(Base):
    __tablename__ = "build_projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    
    title = Column(String(255), nullable=False)
    address = Column(String(500))
    city = Column(String(100))
    state = Column(String(50))
    zip_code = Column(String(20))
    
    status = Column(SQLEnum(ProjectStatus), nullable=False, default=ProjectStatus.PLANNING)
    home_area_sqft = Column(Numeric(10, 2))
    budget = Column(Numeric(12, 2))
    
    baseline_start_date = Column(Date)
    baseline_end_date = Column(Date)
    actual_start_date = Column(Date)
    actual_end_date = Column(Date)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    lots = relationship("Lot", back_populates="project", cascade="all, delete-orphan")
    materials = relationship("MaterialLineItem", back_populates="project", cascade="all, delete-orphan")
    milestones = relationship("ScheduleMilestone", back_populates="project", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="project", cascade="all, delete-orphan")
    files = relationship("File", back_populates="project", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("ix_project_tenant", "tenant_id"),
        Index("ix_project_tenant_status", "tenant_id", "status"),
        Index("ix_project_tenant_deleted", "tenant_id", "deleted_at"),
    )

    def __repr__(self):
        return f"<BuildProject {self.title}>"


class Lot(Base):
    __tablename__ = "lots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("build_projects.id", ondelete="CASCADE"), nullable=False)
    
    lot_number = Column(String(50), nullable=False)
    address = Column(String(500))
    area_sqft = Column(Numeric(10, 2))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    project = relationship("BuildProject", back_populates="lots")

    # Indexes
    __table_args__ = (
        Index("ix_lot_project", "project_id"),
    )

    def __repr__(self):
        return f"<Lot {self.lot_number}>"
