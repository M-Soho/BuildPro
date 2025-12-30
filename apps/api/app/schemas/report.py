from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.report import ReportType, ReportStatus, ReportFormat


class ReportBase(BaseModel):
    type: ReportType
    format: ReportFormat = ReportFormat.PDF


class ReportCreate(ReportBase):
    project_id: UUID


class Report(ReportBase):
    id: UUID
    tenant_id: UUID
    project_id: UUID
    status: ReportStatus
    download_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Report generation request with options
class GenerateReportRequest(BaseModel):
    project_id: UUID
    type: ReportType
    format: ReportFormat = ReportFormat.PDF
    include_photos: bool = False
    include_materials: bool = True
    include_schedule: bool = True
