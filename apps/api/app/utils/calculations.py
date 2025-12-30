"""
Calculation engine for construction project calculations.
All calculations enforce validation rules and use proper rounding.
"""
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional
from app.models.material import UnitOfMeasure


class CalculationError(Exception):
    """Raised when a calculation fails validation"""
    pass


class ConstructionCalculator:
    """Core calculation engine for construction metrics"""
    
    @staticmethod
    def _to_decimal(value: float | Decimal | int) -> Decimal:
        """Convert value to Decimal with proper precision"""
        if isinstance(value, Decimal):
            return value
        return Decimal(str(value))
    
    @staticmethod
    def _round(value: Decimal, places: int = 2) -> Decimal:
        """Round to specified decimal places using HALF_UP"""
        quantizer = Decimal(10) ** -places
        return value.quantize(quantizer, rounding=ROUND_HALF_UP)
    
    # Area Calculations
    @classmethod
    def floor_area(cls, length_ft: float, width_ft: float) -> Decimal:
        """
        Calculate floor area in square feet
        Formula: length * width
        """
        if length_ft <= 0 or width_ft <= 0:
            raise CalculationError("Length and width must be positive")
        
        length = cls._to_decimal(length_ft)
        width = cls._to_decimal(width_ft)
        area = length * width
        
        return cls._round(area, 2)
    
    # Volume Calculations
    @classmethod
    def volume(cls, length_ft: float, width_ft: float, height_ft: float) -> Decimal:
        """
        Calculate volume in cubic feet
        Formula: length * width * height
        """
        if length_ft <= 0 or width_ft <= 0 or height_ft <= 0:
            raise CalculationError("Dimensions must be positive")
        
        length = cls._to_decimal(length_ft)
        width = cls._to_decimal(width_ft)
        height = cls._to_decimal(height_ft)
        volume = length * width * height
        
        return cls._round(volume, 2)
    
    # Material Takeoff Calculations
    @classmethod
    def takeoff_total_qty(
        cls,
        quantity: float,
        wastage_factor: float = 0.0,
    ) -> Decimal:
        """
        Calculate total quantity including wastage
        Formula: quantity * (1 + wastage_factor)
        
        Args:
            quantity: Base quantity
            wastage_factor: Wastage as decimal (0.10 = 10%)
        """
        if quantity < 0:
            raise CalculationError("Quantity cannot be negative")
        if wastage_factor < 0 or wastage_factor > 1:
            raise CalculationError("Wastage factor must be between 0 and 1")
        
        qty = cls._to_decimal(quantity)
        wastage = cls._to_decimal(wastage_factor)
        total_qty = qty * (Decimal('1') + wastage)
        
        return cls._round(total_qty, 3)
    
    @classmethod
    def total_cost(cls, total_qty: float, unit_cost: float) -> Decimal:
        """
        Calculate total cost
        Formula: total_qty * unit_cost
        """
        if total_qty < 0 or unit_cost < 0:
            raise CalculationError("Quantity and cost cannot be negative")
        
        qty = cls._to_decimal(total_qty)
        cost = cls._to_decimal(unit_cost)
        total = qty * cost
        
        return cls._round(total, 2)
    
    # Cost Metrics
    @classmethod
    def cost_per_sqft(cls, total_cost: float, area_sqft: float) -> Decimal:
        """
        Calculate cost per square foot
        Formula: total_cost / area_sqft
        """
        if area_sqft <= 0:
            raise CalculationError("Area must be positive")
        if total_cost < 0:
            raise CalculationError("Cost cannot be negative")
        
        cost = cls._to_decimal(total_cost)
        area = cls._to_decimal(area_sqft)
        cost_per_sqft = cost / area
        
        return cls._round(cost_per_sqft, 2)
    
    # Earned Value Management
    @classmethod
    def earned_value(cls, budget: float, percent_complete: float) -> Decimal:
        """
        Calculate simple earned value
        Formula: budget * (percent_complete / 100)
        
        Args:
            budget: Total budget
            percent_complete: Completion percentage (0-100)
        """
        if budget < 0:
            raise CalculationError("Budget cannot be negative")
        if percent_complete < 0 or percent_complete > 100:
            raise CalculationError("Percent complete must be between 0 and 100")
        
        budget_dec = cls._to_decimal(budget)
        percent = cls._to_decimal(percent_complete) / Decimal('100')
        ev = budget_dec * percent
        
        return cls._round(ev, 2)
    
    @classmethod
    def cost_variance(cls, earned_value: float, actual_cost: float) -> Decimal:
        """
        Calculate cost variance
        Formula: earned_value - actual_cost
        Positive = under budget, Negative = over budget
        """
        ev = cls._to_decimal(earned_value)
        ac = cls._to_decimal(actual_cost)
        cv = ev - ac
        
        return cls._round(cv, 2)
    
    @classmethod
    def schedule_variance_days(
        cls,
        baseline_end: str,
        actual_end: Optional[str],
        current_date: Optional[str] = None,
    ) -> int:
        """
        Calculate schedule variance in days
        If actual_end is None, use current_date
        Positive = ahead of schedule, Negative = behind schedule
        """
        from datetime import datetime, date
        
        baseline = datetime.fromisoformat(baseline_end).date()
        
        if actual_end:
            actual = datetime.fromisoformat(actual_end).date()
        elif current_date:
            actual = datetime.fromisoformat(current_date).date()
        else:
            actual = date.today()
        
        variance = (baseline - actual).days
        return variance


# Unit conversion helpers
class UnitConverter:
    """Convert between different units of measure"""
    
    CONVERSIONS = {
        # To Square Feet
        (UnitOfMeasure.SQ, UnitOfMeasure.SF): Decimal('100'),  # 1 SQ = 100 SF
        
        # Linear to Area (assuming 1 ft width)
        (UnitOfMeasure.LF, UnitOfMeasure.SF): Decimal('1'),
    }
    
    @classmethod
    def convert(
        cls,
        value: float,
        from_unit: UnitOfMeasure,
        to_unit: UnitOfMeasure,
    ) -> Decimal:
        """Convert value from one unit to another"""
        if from_unit == to_unit:
            return Decimal(str(value))
        
        conversion_key = (from_unit, to_unit)
        if conversion_key not in cls.CONVERSIONS:
            raise CalculationError(
                f"No conversion available from {from_unit} to {to_unit}"
            )
        
        val = Decimal(str(value))
        factor = cls.CONVERSIONS[conversion_key]
        return val * factor


# Validation helpers
ALLOWED_UNITS = [unit.value for unit in UnitOfMeasure]


def validate_unit(unit: str) -> bool:
    """Validate that unit is in allowed list"""
    return unit in ALLOWED_UNITS


def validate_positive(value: float, field_name: str = "value") -> None:
    """Validate that value is positive"""
    if value < 0:
        raise CalculationError(f"{field_name} must be non-negative")


def validate_percentage(value: float, field_name: str = "percentage") -> None:
    """Validate that value is a valid percentage (0-100)"""
    if value < 0 or value > 100:
        raise CalculationError(f"{field_name} must be between 0 and 100")
