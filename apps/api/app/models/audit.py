from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum, Index, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
import enum
from app.db.base import Base


class AuditAction(str, enum.Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    READ = "READ"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    action = Column(SQLEnum(AuditAction), nullable=False)
    entity_type = Column(String(100), nullable=False)  # e.g., "BuildProject", "MaterialLineItem"
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    
    changes = Column(JSONB)  # Store before/after values
    meta_data = Column(JSONB)  # Additional context (IP, user agent, etc.)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Indexes
    __table_args__ = (
        Index("ix_audit_tenant", "tenant_id"),
        Index("ix_audit_tenant_user", "tenant_id", "user_id"),
        Index("ix_audit_entity", "entity_type", "entity_id"),
        Index("ix_audit_created", "created_at"),
    )

    def __repr__(self):
        return f"<AuditLog {self.action} {self.entity_type}>"
