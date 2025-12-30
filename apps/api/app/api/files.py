from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import uuid
from app.db.base import get_db
from app.models.file import File
from app.models.project import BuildProject
from app.schemas.file import (
    File as FileSchema,
    FileCreate,
    PresignedUploadUrlResponse,
    PresignedDownloadUrlResponse,
)
from app.middleware.rbac import get_current_tenant_id, get_current_user_id

router = APIRouter()


@router.post("/upload-url", response_model=PresignedUploadUrlResponse)
async def get_upload_url(
    filename: str,
    project_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
):
    """Get presigned URL for file upload"""
    # Verify project
    project = (
        db.query(BuildProject)
        .filter(BuildProject.id == project_id, BuildProject.tenant_id == tenant_id)
        .first()
    )
    
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    # Generate storage key
    storage_key = f"{tenant_id}/{project_id}/{uuid.uuid4()}/{filename}"
    
    # In production, generate presigned URL with boto3
    # For MVP, return placeholder
    upload_url = f"https://s3.example.com/upload?key={storage_key}"
    
    return PresignedUploadUrlResponse(
        upload_url=upload_url,
        storage_key=storage_key,
        expires_in=3600,
    )


@router.post("/", response_model=FileSchema)
async def create_file(
    file: FileCreate,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
    user_id: str = Depends(get_current_user_id),
):
    """Create file metadata after upload"""
    # Verify project
    project = (
        db.query(BuildProject)
        .filter(BuildProject.id == file.project_id, BuildProject.tenant_id == tenant_id)
        .first()
    )
    
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    db_file = File(**file.model_dump(), tenant_id=tenant_id)
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    
    return db_file


@router.get("/", response_model=List[FileSchema])
async def list_files(
    request: Request,
    project_id: UUID,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
):
    """List files for a project"""
    files = (
        db.query(File)
        .filter(File.project_id == project_id, File.tenant_id == tenant_id)
        .all()
    )
    return files


@router.get("/{file_id}/download-url", response_model=PresignedDownloadUrlResponse)
async def get_download_url(
    file_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
):
    """Get presigned download URL"""
    file = (
        db.query(File)
        .filter(File.id == file_id, File.tenant_id == tenant_id)
        .first()
    )
    
    if not file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    
    # In production, generate presigned URL with boto3
    download_url = f"https://s3.example.com/download?key={file.storage_key}"
    
    return PresignedDownloadUrlResponse(
        download_url=download_url,
        expires_in=3600,
    )
