from fastapi import APIRouter, Depends, HTTPException, Request, status, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from uuid import UUID
from datetime import datetime
from decimal import Decimal
import io

from app.db.base import get_db
from app.models.material import MaterialLineItem, MaterialCategory
from app.models.project import BuildProject
from app.schemas.material import (
    MaterialLineItem as MaterialSchema,
    MaterialLineItemCreate,
    MaterialLineItemUpdate,
    MaterialImportRequest,
    MaterialImportResponse,
    MaterialsSummary,
    MaterialCategorySummary,
)
from app.middleware.rbac import get_current_tenant_id, get_current_user_id, require_role
from app.models.user import UserRole
from app.utils.calculations import ConstructionCalculator, CalculationError
from app.utils.audit import AuditLogger, dict_from_model
from app.utils.import_export import MaterialCsvImporter, export_materials_to_csv

router = APIRouter()


def compute_material_totals(material: MaterialLineItem):
    """Compute total_qty and total_cost for a material"""
    try:
        material.total_qty = ConstructionCalculator.takeoff_total_qty(
            float(material.quantity),
            float(material.wastage_factor),
        )
        material.total_cost = ConstructionCalculator.total_cost(
            float(material.total_qty),
            float(material.unit_cost),
        )
    except CalculationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Calculation error: {str(e)}",
        )


@router.post("/", response_model=MaterialSchema, status_code=status.HTTP_201_CREATED)
async def create_material(
    material: MaterialLineItemCreate,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
    user_id: str = Depends(get_current_user_id),
):
    """Create a new material line item"""
    # Verify project belongs to tenant
    project = (
        db.query(BuildProject)
        .filter(
            BuildProject.id == material.project_id,
            BuildProject.tenant_id == tenant_id,
        )
        .first()
    )
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    
    db_material = MaterialLineItem(**material.model_dump())
    
    # Compute totals server-side
    compute_material_totals(db_material)
    
    db.add(db_material)
    db.commit()
    db.refresh(db_material)
    
    # Audit log
    audit = AuditLogger(db, tenant_id, user_id)
    audit.log_create("MaterialLineItem", str(db_material.id), dict_from_model(db_material))
    
    return db_material


@router.get("/", response_model=List[MaterialSchema])
async def list_materials(
    request: Request,
    project_id: UUID,
    category: MaterialCategory = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
):
    """List materials for a project"""
    # Verify project access
    project = (
        db.query(BuildProject)
        .filter(
            BuildProject.id == project_id,
            BuildProject.tenant_id == tenant_id,
        )
        .first()
    )
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    
    query = db.query(MaterialLineItem).filter(
        MaterialLineItem.project_id == project_id,
        MaterialLineItem.deleted_at == None,
    )
    
    if category:
        query = query.filter(MaterialLineItem.category == category)
    
    materials = query.offset(skip).limit(limit).all()
    return materials


@router.get("/{material_id}", response_model=MaterialSchema)
async def get_material(
    material_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
):
    """Get material by ID"""
    material = (
        db.query(MaterialLineItem)
        .join(BuildProject)
        .filter(
            MaterialLineItem.id == material_id,
            BuildProject.tenant_id == tenant_id,
            MaterialLineItem.deleted_at == None,
        )
        .first()
    )
    
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found",
        )
    
    return material


@router.patch("/{material_id}", response_model=MaterialSchema)
async def update_material(
    material_id: UUID,
    material_update: MaterialLineItemUpdate,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
    user_id: str = Depends(get_current_user_id),
):
    """Update material"""
    db_material = (
        db.query(MaterialLineItem)
        .join(BuildProject)
        .filter(
            MaterialLineItem.id == material_id,
            BuildProject.tenant_id == tenant_id,
            MaterialLineItem.deleted_at == None,
        )
        .first()
    )
    
    if not db_material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found",
        )
    
    before = dict_from_model(db_material)
    
    # Update fields
    update_data = material_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_material, field, value)
    
    # Recompute totals
    compute_material_totals(db_material)
    
    db.commit()
    db.refresh(db_material)
    
    # Audit log
    audit = AuditLogger(db, tenant_id, user_id)
    audit.log_update("MaterialLineItem", str(db_material.id), before, dict_from_model(db_material))
    
    return db_material


@router.delete("/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_material(
    material_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
    user_id: str = Depends(get_current_user_id),
):
    """Soft delete material"""
    db_material = (
        db.query(MaterialLineItem)
        .join(BuildProject)
        .filter(
            MaterialLineItem.id == material_id,
            BuildProject.tenant_id == tenant_id,
            MaterialLineItem.deleted_at == None,
        )
        .first()
    )
    
    if not db_material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found",
        )
    
    db_material.deleted_at = datetime.utcnow()
    db.commit()
    
    # Audit log
    audit = AuditLogger(db, tenant_id, user_id)
    audit.log_delete("MaterialLineItem", str(db_material.id), dict_from_model(db_material))
    
    return None


@router.post("/import", response_model=MaterialImportResponse)
async def import_materials(
    import_request: MaterialImportRequest,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
    user_id: str = Depends(get_current_user_id),
):
    """Bulk import materials from CSV/XLSX"""
    # Verify project
    project = (
        db.query(BuildProject)
        .filter(
            BuildProject.id == import_request.project_id,
            BuildProject.tenant_id == tenant_id,
        )
        .first()
    )
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    
    success_count = 0
    error_count = 0
    errors = []
    created_ids = []
    
    for idx, row in enumerate(import_request.materials):
        try:
            # Validate and create material
            material = MaterialLineItem(
                project_id=import_request.project_id,
                category=MaterialCategory(row.category),
                description=row.description,
                quantity=Decimal(str(row.quantity)),
                unit=row.unit,
                wastage_factor=Decimal(str(row.wastage_factor)),
                unit_cost=Decimal(str(row.unit_cost)),
                notes=row.notes,
            )
            
            compute_material_totals(material)
            
            db.add(material)
            db.flush()
            
            created_ids.append(material.id)
            success_count += 1
            
        except Exception as e:
            error_count += 1
            errors.append({
                "row": idx + 1,
                "error": str(e),
                "data": row.model_dump(),
            })
    
    if success_count > 0:
        db.commit()
    
    return MaterialImportResponse(
        success_count=success_count,
        error_count=error_count,
        errors=errors,
        created_ids=created_ids,
    )


@router.get("/summary/{project_id}", response_model=MaterialsSummary)
async def get_materials_summary(
    project_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
):
    """Get materials summary by category"""
    # Verify project
    project = (
        db.query(BuildProject)
        .filter(
            BuildProject.id == project_id,
            BuildProject.tenant_id == tenant_id,
        )
        .first()
    )
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    
    # Get total cost
    total_cost_result = (
        db.query(func.sum(MaterialLineItem.total_cost))
        .filter(
            MaterialLineItem.project_id == project_id,
            MaterialLineItem.deleted_at == None,
        )
        .scalar()
    )
    total_cost = total_cost_result or Decimal('0')
    
    # Get summary by category
    category_summary = (
        db.query(
            MaterialLineItem.category,
            func.sum(MaterialLineItem.total_cost).label("total_cost"),
            func.count(MaterialLineItem.id).label("item_count"),
        )
        .filter(
            MaterialLineItem.project_id == project_id,
            MaterialLineItem.deleted_at == None,
        )
        .group_by(MaterialLineItem.category)
        .all()
    )
    
    by_category = [
        MaterialCategorySummary(
            category=cat,
            total_cost=cost or Decimal('0'),
            item_count=count,
        )
        for cat, cost, count in category_summary
    ]
    
    return MaterialsSummary(
        total_cost=total_cost,
        by_category=by_category,
    )


@router.post("/import-csv/{project_id}", response_model=MaterialImportResponse)
async def import_materials_csv(
    project_id: str,
    file: UploadFile = File(...),
    request: Request = None,
    db: Session = Depends(get_db),
):
    """
    Import materials from CSV file
    
    CSV format:
    category,description,quantity,unit,wastage_factor,unit_cost,vendor,notes
    FRAMING,2x4 Lumber - 8ft,500,EA,0.10,8.50,ABC Lumber,Premium grade
    """
    tenant_id = request.state.tenant_id
    user_id = request.state.user_id
    
    # Read file content
    content = await file.read()
    csv_content = content.decode("utf-8")
    
    # Parse CSV
    importer = MaterialCsvImporter()
    try:
        material_creates = importer.parse_csv(csv_content, project_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Create materials in database
    created_materials = []
    for material_data in material_creates:
        material = MaterialLineItem(
            **material_data.dict(),
            tenant_id=tenant_id,
        )
        
        # Server-side calculation
        compute_material_totals(material)
        
        db.add(material)
        created_materials.append(material)
    
    db.commit()
    
    # Audit log
    audit_logger = AuditLogger(db, tenant_id, user_id)
    audit_logger.log_create("material", {
        "project_id": project_id,
        "bulk_import_count": len(created_materials),
    })
    
    return MaterialImportResponse(
        imported_count=len(created_materials),
        skipped_count=0,
        errors=[],
    )


@router.get("/export-csv/{project_id}")
async def export_materials_csv(
    project_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Export project materials to CSV"""
    tenant_id = request.state.tenant_id
    
    materials = (
        db.query(MaterialLineItem)
        .filter(
            MaterialLineItem.tenant_id == tenant_id,
            MaterialLineItem.project_id == project_id,
            MaterialLineItem.deleted_at.is_(None),
        )
        .all()
    )
    
    # Convert to dicts
    material_dicts = [
        MaterialSchema.from_orm(m).dict() for m in materials
    ]
    
    # Generate CSV
    csv_content = export_materials_to_csv(material_dicts)
    
    # Return as downloadable file
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=materials_{project_id}.csv"
        },
    )
