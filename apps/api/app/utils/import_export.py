"""
CSV/XLSX Import/Export Utilities for Backend
Provides parsing and export functionality for materials and schedule data
"""

import csv
import io
from typing import List, Dict, Any, Optional, Tuple
from decimal import Decimal
from datetime import datetime

from app.schemas.material import MaterialLineItemCreate, MaterialCategory, UnitOfMeasure
from app.schemas.schedule import ScheduleMilestoneCreate, MilestonePhase


class ImportError(Exception):
    """Raised when import validation fails"""
    pass


class MaterialCsvImporter:
    """Import material line items from CSV"""
    
    REQUIRED_HEADERS = ["category", "description", "quantity", "unit", "unit_cost"]
    OPTIONAL_HEADERS = ["wastage_factor", "vendor", "notes", "csi_code"]
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def parse_csv(self, csv_content: str, project_id: str) -> List[MaterialLineItemCreate]:
        """
        Parse CSV content into MaterialLineItemCreate objects
        
        Args:
            csv_content: Raw CSV string
            project_id: Project to import materials to
            
        Returns:
            List of validated MaterialLineItemCreate objects
            
        Raises:
            ImportError: If validation fails
        """
        self.errors = []
        self.warnings = []
        materials = []
        
        try:
            csv_file = io.StringIO(csv_content)
            reader = csv.DictReader(csv_file)
            
            # Validate headers
            if not reader.fieldnames:
                raise ImportError("No headers found in CSV")
            
            missing_headers = set(self.REQUIRED_HEADERS) - set(reader.fieldnames)
            if missing_headers:
                raise ImportError(f"Missing required headers: {', '.join(missing_headers)}")
            
            # Parse rows
            for row_num, row in enumerate(reader, start=2):  # Start at 2 (1 is header)
                try:
                    material = self._parse_row(row, project_id, row_num)
                    materials.append(material)
                except ValueError as e:
                    self.errors.append(f"Row {row_num}: {str(e)}")
        
        except csv.Error as e:
            raise ImportError(f"CSV parsing error: {str(e)}")
        
        if self.errors:
            raise ImportError(f"Validation failed with {len(self.errors)} errors:\n" + "\n".join(self.errors[:10]))
        
        return materials
    
    def _parse_row(self, row: Dict[str, str], project_id: str, row_num: int) -> MaterialLineItemCreate:
        """Parse single CSV row into MaterialLineItemCreate"""
        
        # Validate category
        category = row.get("category", "").strip().upper()
        try:
            MaterialCategory(category)
        except ValueError:
            raise ValueError(f"Invalid category '{category}'. Must be one of: {', '.join([c.value for c in MaterialCategory])}")
        
        # Validate unit
        unit = row.get("unit", "").strip().upper()
        try:
            UnitOfMeasure(unit)
        except ValueError:
            raise ValueError(f"Invalid unit '{unit}'. Must be one of: {', '.join([u.value for u in UnitOfMeasure])}")
        
        # Parse numeric fields
        try:
            quantity = Decimal(row["quantity"])
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
        except (ValueError, KeyError):
            raise ValueError("Invalid quantity value")
        
        try:
            unit_cost = Decimal(row["unit_cost"])
            if unit_cost < 0:
                raise ValueError("Unit cost cannot be negative")
        except (ValueError, KeyError):
            raise ValueError("Invalid unit_cost value")
        
        # Parse optional wastage factor
        wastage_factor = Decimal("0.0")
        if row.get("wastage_factor"):
            try:
                wastage_factor = Decimal(row["wastage_factor"])
                if not (0 <= wastage_factor <= 1):
                    raise ValueError("Wastage factor must be between 0 and 1")
            except ValueError:
                self.warnings.append(f"Row {row_num}: Invalid wastage_factor, using 0")
        
        return MaterialLineItemCreate(
            project_id=project_id,
            category=category,
            description=row["description"].strip(),
            quantity=quantity,
            unit=unit,
            wastage_factor=wastage_factor,
            unit_cost=unit_cost,
            vendor=row.get("vendor", "").strip() or None,
            notes=row.get("notes", "").strip() or None,
            csi_code=row.get("csi_code", "").strip() or None,
        )


class ScheduleCsvImporter:
    """Import schedule milestones from CSV"""
    
    REQUIRED_HEADERS = ["phase", "description", "baseline_start_date", "baseline_end_date"]
    OPTIONAL_HEADERS = ["actual_start_date", "actual_end_date", "notes"]
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def parse_csv(self, csv_content: str, project_id: str) -> List[ScheduleMilestoneCreate]:
        """Parse CSV content into ScheduleMilestoneCreate objects"""
        self.errors = []
        self.warnings = []
        milestones = []
        
        try:
            csv_file = io.StringIO(csv_content)
            reader = csv.DictReader(csv_file)
            
            if not reader.fieldnames:
                raise ImportError("No headers found in CSV")
            
            missing_headers = set(self.REQUIRED_HEADERS) - set(reader.fieldnames)
            if missing_headers:
                raise ImportError(f"Missing required headers: {', '.join(missing_headers)}")
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    milestone = self._parse_row(row, project_id, row_num)
                    milestones.append(milestone)
                except ValueError as e:
                    self.errors.append(f"Row {row_num}: {str(e)}")
        
        except csv.Error as e:
            raise ImportError(f"CSV parsing error: {str(e)}")
        
        if self.errors:
            raise ImportError(f"Validation failed with {len(self.errors)} errors:\n" + "\n".join(self.errors[:10]))
        
        return milestones
    
    def _parse_row(self, row: Dict[str, str], project_id: str, row_num: int) -> ScheduleMilestoneCreate:
        """Parse single CSV row into ScheduleMilestoneCreate"""
        
        # Validate phase
        phase = row.get("phase", "").strip().upper()
        try:
            MilestonePhase(phase)
        except ValueError:
            raise ValueError(f"Invalid phase '{phase}'. Must be one of: {', '.join([p.value for p in MilestonePhase])}")
        
        # Parse dates
        try:
            baseline_start = datetime.fromisoformat(row["baseline_start_date"])
            baseline_end = datetime.fromisoformat(row["baseline_end_date"])
            
            if baseline_end <= baseline_start:
                raise ValueError("End date must be after start date")
        except (ValueError, KeyError) as e:
            raise ValueError(f"Invalid date format. Use ISO format (YYYY-MM-DD): {str(e)}")
        
        # Parse optional actual dates
        actual_start = None
        actual_end = None
        if row.get("actual_start_date"):
            try:
                actual_start = datetime.fromisoformat(row["actual_start_date"])
            except ValueError:
                self.warnings.append(f"Row {row_num}: Invalid actual_start_date, ignoring")
        
        if row.get("actual_end_date"):
            try:
                actual_end = datetime.fromisoformat(row["actual_end_date"])
            except ValueError:
                self.warnings.append(f"Row {row_num}: Invalid actual_end_date, ignoring")
        
        return ScheduleMilestoneCreate(
            project_id=project_id,
            phase=phase,
            description=row["description"].strip(),
            baseline_start_date=baseline_start,
            baseline_end_date=baseline_end,
            actual_start_date=actual_start,
            actual_end_date=actual_end,
            notes=row.get("notes", "").strip() or None,
        )


def export_materials_to_csv(materials: List[Dict[str, Any]]) -> str:
    """
    Export materials to CSV string
    
    Args:
        materials: List of material dicts (from MaterialSchema.dict())
        
    Returns:
        CSV string
    """
    if not materials:
        return ""
    
    output = io.StringIO()
    headers = [
        "id",
        "category",
        "description",
        "quantity",
        "unit",
        "wastage_factor",
        "total_qty",
        "unit_cost",
        "total_cost",
        "vendor",
        "csi_code",
        "notes",
    ]
    
    writer = csv.DictWriter(output, fieldnames=headers, extrasaction="ignore")
    writer.writeheader()
    
    for material in materials:
        # Convert Decimal to string for CSV
        row = {**material}
        for key in ["quantity", "wastage_factor", "total_qty", "unit_cost", "total_cost"]:
            if key in row and row[key] is not None:
                row[key] = str(row[key])
        writer.writerow(row)
    
    return output.getvalue()


def export_schedule_to_csv(milestones: List[Dict[str, Any]]) -> str:
    """Export schedule milestones to CSV string"""
    if not milestones:
        return ""
    
    output = io.StringIO()
    headers = [
        "id",
        "phase",
        "description",
        "baseline_start_date",
        "baseline_end_date",
        "actual_start_date",
        "actual_end_date",
        "notes",
    ]
    
    writer = csv.DictWriter(output, fieldnames=headers, extrasaction="ignore")
    writer.writeheader()
    
    for milestone in milestones:
        # Convert datetime to ISO format
        row = {**milestone}
        for key in ["baseline_start_date", "baseline_end_date", "actual_start_date", "actual_end_date"]:
            if key in row and row[key] is not None:
                if isinstance(row[key], datetime):
                    row[key] = row[key].date().isoformat()
        writer.writerow(row)
    
    return output.getvalue()
