"""Tests for Home Ledger calculation functions."""

from custom_components.home_ledger.calculations import (
    calculate_average_monthly_consumption,
    calculate_average_monthly_cost,
    calculate_cost_per_unit,
    calculate_total_consumption,
    calculate_total_cost,
    calculate_total_months,
)
from custom_components.home_ledger.models import Bill


def _bill(
    utility_type: str = "electricity",
    months: int = 1,
    total_cost: float = 100.0,
    consumption: float = 200.0,
) -> Bill:
    """Create a test bill."""
    return Bill(
        id="test",
        utility_type=utility_type,
        months=months,
        total_cost=total_cost,
        consumption=consumption,
    )


class TestCalculateTotalCost:
    """Tests for calculate_total_cost."""

    def test_empty_list(self) -> None:
        assert calculate_total_cost([], "electricity") == 0

    def test_single_bill(self) -> None:
        bills = [_bill(total_cost=100.0)]
        assert calculate_total_cost(bills, "electricity") == 100.0

    def test_multiple_bills_same_type(self) -> None:
        bills = [
            _bill(total_cost=100.0),
            _bill(total_cost=200.0),
        ]
        assert calculate_total_cost(bills, "electricity") == 300.0

    def test_multiple_bills_different_types(self) -> None:
        bills = [
            _bill(utility_type="electricity", total_cost=100.0),
            _bill(utility_type="gas", total_cost=200.0),
            _bill(utility_type="water", total_cost=50.0),
        ]
        assert calculate_total_cost(bills, "electricity") == 100.0
        assert calculate_total_cost(bills, "gas") == 200.0
        assert calculate_total_cost(bills, "water") == 50.0

    def test_all_types(self) -> None:
        bills = [
            _bill(utility_type="electricity", total_cost=100.0),
            _bill(utility_type="gas", total_cost=200.0),
        ]
        assert calculate_total_cost(bills) == 300.0


class TestCalculateTotalConsumption:
    """Tests for calculate_total_consumption."""

    def test_empty_list(self) -> None:
        assert calculate_total_consumption([], "electricity") == 0

    def test_single_bill(self) -> None:
        bills = [_bill(consumption=412.0)]
        assert calculate_total_consumption(bills, "electricity") == 412.0

    def test_multiple_bills(self) -> None:
        bills = [
            _bill(consumption=412.0),
            _bill(consumption=300.0),
        ]
        assert calculate_total_consumption(bills, "electricity") == 712.0

    def test_different_types_not_summed(self) -> None:
        bills = [
            _bill(utility_type="electricity", consumption=412.0),
            _bill(utility_type="gas", consumption=100.0),
        ]
        assert calculate_total_consumption(bills, "electricity") == 412.0
        assert calculate_total_consumption(bills, "gas") == 100.0


class TestCalculateTotalMonths:
    """Tests for calculate_total_months."""

    def test_empty_list(self) -> None:
        assert calculate_total_months([], "electricity") == 0

    def test_single_bill(self) -> None:
        bills = [_bill(months=2)]
        assert calculate_total_months(bills, "electricity") == 2

    def test_multiple_bills(self) -> None:
        bills = [
            _bill(months=2),
            _bill(months=3),
            _bill(months=1),
        ]
        assert calculate_total_months(bills, "electricity") == 6


class TestCalculateAverageMonthlyCost:
    """Tests for calculate_average_monthly_cost."""

    def test_empty_list(self) -> None:
        assert calculate_average_monthly_cost([], "electricity") is None

    def test_single_bill(self) -> None:
        bills = [_bill(months=2, total_cost=100.0)]
        assert calculate_average_monthly_cost(bills, "electricity") == 50.0

    def test_multiple_bills(self) -> None:
        bills = [
            _bill(months=2, total_cost=100.0),
            _bill(months=2, total_cost=120.0),
            _bill(months=1, total_cost=60.0),
        ]
        # Total cost = 280, total months = 5, average = 56
        assert calculate_average_monthly_cost(bills, "electricity") == 56.0


class TestCalculateAverageMonthlyConsumption:
    """Tests for calculate_average_monthly_consumption."""

    def test_empty_list(self) -> None:
        assert calculate_average_monthly_consumption([], "electricity") is None

    def test_single_bill(self) -> None:
        bills = [_bill(months=2, consumption=400.0)]
        assert calculate_average_monthly_consumption(bills, "electricity") == 200.0

    def test_multiple_bills(self) -> None:
        bills = [
            _bill(months=2, consumption=400.0),
            _bill(months=3, consumption=600.0),
        ]
        # Total consumption = 1000, total months = 5, average = 200
        assert calculate_average_monthly_consumption(bills, "electricity") == 200.0


class TestCalculateCostPerUnit:
    """Tests for calculate_cost_per_unit."""

    def test_empty_list(self) -> None:
        assert calculate_cost_per_unit([], "electricity") is None

    def test_zero_consumption(self) -> None:
        bills = [_bill(consumption=0)]
        assert calculate_cost_per_unit(bills, "electricity") is None

    def test_single_bill(self) -> None:
        bills = [_bill(total_cost=100.0, consumption=200.0)]
        assert calculate_cost_per_unit(bills, "electricity") == 0.5

    def test_multiple_bills(self) -> None:
        bills = [
            _bill(total_cost=100.0, consumption=200.0),
            _bill(total_cost=200.0, consumption=400.0),
        ]
        # Total cost = 300, total consumption = 600, cost per unit = 0.5
        assert calculate_cost_per_unit(bills, "electricity") == 0.5
