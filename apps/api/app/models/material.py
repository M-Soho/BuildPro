from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Enum as SQLEnum, Index, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum
from app.db.base import Base


class MaterialCategory(str, enum.Enum):
    FRAMING = "FRAMING"
    CONCRETE = "CONCRETE"
    ELECTRICAL = "ELECTRICAL"
    PLUMBING = "PLUMBING"
    HVAC = "HVAC"
    ROOFING = "ROOFING"
    SIDING = "SIDING"
    DRYWALL = "DRYWALL"
    FLOORING = "FLOORING"
    FIXTURES = "FIXTURES"
    OTHER = "OTHER"


class UnitOfMeasure(str, enum.Enum):
    LF = "LF"  # Linear Feet
    SF = "SF"  # Square Feet
    CF = "CF"  # Cubic Feet
    EA = "EA"  # Each
    LB = "LB"  # Pound
    TON = "TON"
    GAL = "GAL"  # Gallon
    SQ = "SQ"  # Square (100 SF)


class MaterialLineItem(Base):
    __tablename__ = "material_line_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("build_projects.id", ondelete="CASCADE"), nullable=False)
    
    category = Column(SQLEnum(MaterialCategory), nullable=False)
    description = Column(String(500), nullable=False)
    
    quantity = Column(Numeric(12, 3), nullable=False, default=0)
    unit = Column(SQLEnum(UnitOfMeasure), nullable=False)
    wastage_factor = Column(Numeric(5, 4), nullable=False, default=0)  # 0.0000 to 1.0000
    
    # Computed fields (server-side)
    total_qty = Column(Numeric(12, 3), nullable=False, default=0)
    unit_cost = Column(Numeric(10, 2), nullable=False, default=0)
    total_cost = Column(Numeric(12, 2), nullable=False, default=0)
    
    notes = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    project = relationship("BuildProject", back_populates="materials")

    # Indexes
    __table_args__ = (
        Index("ix_material_project", "project_id"),
        Index("ix_material_project_deleted", "project_id", "deleted_at"),
        Index("ix_material_category", "category"),
    )

    def __repr__(self):
        return f"<MaterialLineItem {self.description}>"
