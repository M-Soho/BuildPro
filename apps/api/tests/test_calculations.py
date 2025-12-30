import pytest
from decimal import Decimal
from app.utils.calculations import (
    ConstructionCalculator,
    CalculationError,
    UnitConverter,
    validate_unit,
    validate_positive,
    validate_percentage,
)
from app.models.material import UnitOfMeasure


class TestFloorArea:
    def test_basic_area(self):
        result = ConstructionCalculator.floor_area(10, 20)
        assert result == Decimal('200.00')
    
    def test_decimal_area(self):
        result = ConstructionCalculator.floor_area(10.5, 20.75)
        assert result == Decimal('217.88')
    
    def test_negative_length(self):
        with pytest.raises(CalculationError):
            ConstructionCalculator.floor_area(-10, 20)
    
    def test_zero_width(self):
        with pytest.raises(CalculationError):
            ConstructionCalculator.floor_area(10, 0)


class TestVolume:
    def test_basic_volume(self):
        result = ConstructionCalculator.volume(10, 20, 8)
        assert result == Decimal('1600.00')
    
    def test_decimal_volume(self):
        result = ConstructionCalculator.volume(10.5, 20.5, 8.25)
        assert result == Decimal('1775.44')
    
    def test_negative_dimension(self):
        with pytest.raises(CalculationError):
            ConstructionCalculator.volume(10, 20, -5)


class TestTakeoffCalculations:
    def test_no_wastage(self):
        result = ConstructionCalculator.takeoff_total_qty(100, 0)
        assert result == Decimal('100.000')
    
    def test_with_wastage_10_percent(self):
        result = ConstructionCalculator.takeoff_total_qty(100, 0.10)
        assert result == Decimal('110.000')
    
    def test_with_wastage_15_percent(self):
        result = ConstructionCalculator.takeoff_total_qty(50.5, 0.15)
        assert result == Decimal('58.075')
    
    def test_negative_quantity(self):
        with pytest.raises(CalculationError):
            ConstructionCalculator.takeoff_total_qty(-10, 0.10)
    
    def test_invalid_wastage_factor(self):
        with pytest.raises(CalculationError):
            ConstructionCalculator.takeoff_total_qty(100, 1.5)


class TestTotalCost:
    def test_basic_cost(self):
        result = ConstructionCalculator.total_cost(100, 5.50)
        assert result == Decimal('550.00')
    
    def test_decimal_cost(self):
        result = ConstructionCalculator.total_cost(110.5, 12.75)
        assert result == Decimal('1408.88')
    
    def test_rounding(self):
        result = ConstructionCalculator.total_cost(10.333, 3.999)
        assert result == Decimal('41.30')  # Proper rounding
    
    def test_negative_cost(self):
        with pytest.raises(CalculationError):
            ConstructionCalculator.total_cost(100, -5)


class TestCostPerSqFt:
    def test_basic_cost_per_sqft(self):
        result = ConstructionCalculator.cost_per_sqft(250000, 2000)
        assert result == Decimal('125.00')
    
    def test_decimal_cost_per_sqft(self):
        result = ConstructionCalculator.cost_per_sqft(275500, 2150)
        assert result == Decimal('128.14')
    
    def test_zero_area(self):
        with pytest.raises(CalculationError):
            ConstructionCalculator.cost_per_sqft(250000, 0)
    
    def test_negative_cost(self):
        with pytest.raises(CalculationError):
            ConstructionCalculator.cost_per_sqft(-100, 2000)


class TestEarnedValue:
    def test_zero_percent_complete(self):
        result = ConstructionCalculator.earned_value(100000, 0)
        assert result == Decimal('0.00')
    
    def test_fifty_percent_complete(self):
        result = ConstructionCalculator.earned_value(100000, 50)
        assert result == Decimal('50000.00')
    
    def test_full_complete(self):
        result = ConstructionCalculator.earned_value(100000, 100)
        assert result == Decimal('100000.00')
    
    def test_decimal_percent(self):
        result = ConstructionCalculator.earned_value(100000, 33.33)
        assert result == Decimal('33330.00')
    
    def test_invalid_percent(self):
        with pytest.raises(CalculationError):
            ConstructionCalculator.earned_value(100000, 150)


class TestCostVariance:
    def test_under_budget(self):
        result = ConstructionCalculator.cost_variance(50000, 45000)
        assert result == Decimal('5000.00')
    
    def test_over_budget(self):
        result = ConstructionCalculator.cost_variance(50000, 55000)
        assert result == Decimal('-5000.00')
    
    def test_on_budget(self):
        result = ConstructionCalculator.cost_variance(50000, 50000)
        assert result == Decimal('0.00')


class TestScheduleVariance:
    def test_ahead_of_schedule(self):
        # Baseline: 2024-12-31, Actual: 2024-12-25
        result = ConstructionCalculator.schedule_variance_days(
            "2024-12-31", "2024-12-25"
        )
        assert result == 6  # 6 days ahead
    
    def test_behind_schedule(self):
        # Baseline: 2024-12-31, Actual: 2025-01-05
        result = ConstructionCalculator.schedule_variance_days(
            "2024-12-31", "2025-01-05"
        )
        assert result == -5  # 5 days behind
    
    def test_on_schedule(self):
        result = ConstructionCalculator.schedule_variance_days(
            "2024-12-31", "2024-12-31"
        )
        assert result == 0


class TestUnitConverter:
    def test_same_unit(self):
        result = UnitConverter.convert(100, UnitOfMeasure.SF, UnitOfMeasure.SF)
        assert result == Decimal('100')
    
    def test_square_to_sqft(self):
        result = UnitConverter.convert(5, UnitOfMeasure.SQ, UnitOfMeasure.SF)
        assert result == Decimal('500')  # 5 squares = 500 SF
    
    def test_invalid_conversion(self):
        with pytest.raises(CalculationError):
            UnitConverter.convert(100, UnitOfMeasure.LF, UnitOfMeasure.GAL)


class TestValidation:
    def test_validate_unit_valid(self):
        assert validate_unit("SF") is True
        assert validate_unit("LF") is True
    
    def test_validate_unit_invalid(self):
        assert validate_unit("INVALID") is False
    
    def test_validate_positive(self):
        validate_positive(10)  # Should not raise
        with pytest.raises(CalculationError):
            validate_positive(-5)
    
    def test_validate_percentage(self):
        validate_percentage(50)  # Should not raise
        validate_percentage(0)  # Should not raise
        validate_percentage(100)  # Should not raise
        
        with pytest.raises(CalculationError):
            validate_percentage(-10)
        
        with pytest.raises(CalculationError):
            validate_percentage(150)


class TestRoundingBehavior:
    """Test that rounding follows ROUND_HALF_UP (banker's rounding)"""
    
    def test_round_half_up(self):
        # 10.335 should round to 10.34 (not 10.33)
        result = ConstructionCalculator._round(Decimal('10.335'), 2)
        assert result == Decimal('10.34')
    
    def test_round_down(self):
        result = ConstructionCalculator._round(Decimal('10.334'), 2)
        assert result == Decimal('10.33')
    
    def test_round_three_places(self):
        result = ConstructionCalculator._round(Decimal('10.3456'), 3)
        assert result == Decimal('10.346')
