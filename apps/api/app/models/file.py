from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Enum as SQLEnum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum
from app.db.base import Base


class FileType(str, enum.Enum):
    DRAWING = "DRAWING"
    PHOTO = "PHOTO"
    DOCUMENT = "DOCUMENT"
    OTHER = "OTHER"


class File(Base):
    __tablename__ = "files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("build_projects.id", ondelete="CASCADE"), nullable=False)
    
    filename = Column(String(255), nullable=False)
    file_type = Column(SQLEnum(FileType), nullable=False)
    mime_type = Column(String(100))
    size_bytes = Column(Integer)
    
    storage_key = Column(String(500), nullable=False)  # S3 key
    storage_url = Column(String(1000))  # Public URL if applicable
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    project = relationship("BuildProject", back_populates="files")

    # Indexes
    __table_args__ = (
        Index("ix_file_tenant", "tenant_id"),
        Index("ix_file_tenant_project", "tenant_id", "project_id"),
        Index("ix_file_type", "file_type"),
    )

    def __repr__(self):
        return f"<File {self.filename}>"
