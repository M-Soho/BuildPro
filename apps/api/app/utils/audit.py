from sqlalchemy.orm import Session
from app.models.audit import AuditLog, AuditAction
from typing import Optional, Dict, Any
import uuid


class AuditLogger:
    """Utility for writing audit logs"""
    
    def __init__(self, db: Session, tenant_id: str, user_id: Optional[str] = None):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    def log(
        self,
        action: AuditAction,
        entity_type: str,
        entity_id: str,
        changes: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Create an audit log entry"""
        audit_log = AuditLog(
            tenant_id=self.tenant_id,
            user_id=self.user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            changes=changes,
            metadata=metadata,
        )
        self.db.add(audit_log)
        self.db.commit()
        return audit_log
    
    def log_create(self, entity_type: str, entity_id: str, data: Dict[str, Any]):
        """Log a CREATE action"""
        return self.log(
            action=AuditAction.CREATE,
            entity_type=entity_type,
            entity_id=entity_id,
            changes={"after": data},
        )
    
    def log_update(
        self,
        entity_type: str,
        entity_id: str,
        before: Dict[str, Any],
        after: Dict[str, Any],
    ):
        """Log an UPDATE action"""
        return self.log(
            action=AuditAction.UPDATE,
            entity_type=entity_type,
            entity_id=entity_id,
            changes={"before": before, "after": after},
        )
    
    def log_delete(self, entity_type: str, entity_id: str, data: Dict[str, Any]):
        """Log a DELETE action"""
        return self.log(
            action=AuditAction.DELETE,
            entity_type=entity_type,
            entity_id=entity_id,
            changes={"before": data},
        )


def dict_from_model(instance) -> Dict[str, Any]:
    """Convert SQLAlchemy model instance to dict for audit logging"""
    return {
        c.name: str(getattr(instance, c.name))
        for c in instance.__table__.columns
    }
