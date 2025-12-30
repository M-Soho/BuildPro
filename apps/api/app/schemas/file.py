from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.file import FileType


class FileBase(BaseModel):
    filename: str
    file_type: FileType
    mime_type: Optional[str] = None


class FileCreate(FileBase):
    project_id: UUID
    storage_key: str
    size_bytes: Optional[int] = None


class File(FileBase):
    id: UUID
    tenant_id: UUID
    project_id: UUID
    storage_key: str
    storage_url: Optional[str] = None
    size_bytes: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Presigned URL responses
class PresignedUploadUrlResponse(BaseModel):
    upload_url: str
    storage_key: str
    expires_in: int  # seconds


class PresignedDownloadUrlResponse(BaseModel):
    download_url: str
    expires_in: int  # seconds
