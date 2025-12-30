from fastapi import APIRouter, Depends, HTTPException, Request, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.db.base import get_db
from app.models.report import Report, ReportStatus
from app.models.project import BuildProject
from app.schemas.report import (
    Report as ReportSchema,
    GenerateReportRequest,
)
from app.middleware.rbac import get_current_tenant_id, get_current_user_id

router = APIRouter()


async def generate_report_task(report_id: UUID, db: Session):
    """Background task to generate report (placeholder for Celery)"""
    # This would normally be a Celery task
    # For MVP, we'll just mark as completed
    report = db.query(Report).filter(Report.id == report_id).first()
    if report:
        report.status = ReportStatus.COMPLETED
        report.download_url = f"/api/reports/{report_id}/download"
        db.commit()


@router.post("/generate", response_model=ReportSchema)
async def generate_report(
    report_request: GenerateReportRequest,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
    user_id: str = Depends(get_current_user_id),
):
    """Generate a report (async)"""
    # Verify project
    project = (
        db.query(BuildProject)
        .filter(
            BuildProject.id == report_request.project_id,
            BuildProject.tenant_id == tenant_id,
        )
        .first()
    )
    
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    # Create report record
    db_report = Report(
        tenant_id=tenant_id,
        project_id=report_request.project_id,
        type=report_request.type,
        format=report_request.format,
        status=ReportStatus.PENDING,
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    
    # Add background task (in production, this would queue a Celery task)
    background_tasks.add_task(generate_report_task, db_report.id, db)
    
    return db_report


@router.get("/{report_id}", response_model=ReportSchema)
async def get_report(
    report_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
):
    """Get report status and download URL"""
    report = (
        db.query(Report)
        .filter(Report.id == report_id, Report.tenant_id == tenant_id)
        .first()
    )
    
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    
    return report


@router.get("/", response_model=List[ReportSchema])
async def list_reports(
    request: Request,
    project_id: UUID = None,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
):
    """List reports for tenant or project"""
    query = db.query(Report).filter(Report.tenant_id == tenant_id)
    
    if project_id:
        query = query.filter(Report.project_id == project_id)
    
    reports = query.order_by(Report.created_at.desc()).all()
    return reports
