from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum, Index, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum
from app.db.base import Base


class ReportType(str, enum.Enum):
    PROGRESS = "PROGRESS"
    BUDGET_VS_ACTUAL = "BUDGET_VS_ACTUAL"
    TAKEOFF_SUMMARY = "TAKEOFF_SUMMARY"
    OM_BINDER = "OM_BINDER"


class ReportStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ReportFormat(str, enum.Enum):
    PDF = "PDF"
    CSV = "CSV"
    XLSX = "XLSX"


class Report(Base):
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("build_projects.id", ondelete="CASCADE"), nullable=False)
    
    type = Column(SQLEnum(ReportType), nullable=False)
    format = Column(SQLEnum(ReportFormat), nullable=False)
    status = Column(SQLEnum(ReportStatus), nullable=False, default=ReportStatus.PENDING)
    
    download_url = Column(String(1000))
    error_message = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    project = relationship("BuildProject", back_populates="reports")

    # Indexes
    __table_args__ = (
        Index("ix_report_tenant", "tenant_id"),
        Index("ix_report_tenant_project", "tenant_id", "project_id"),
        Index("ix_report_status", "status"),
    )

    def __repr__(self):
        return f"<Report {self.type} - {self.status}>"
