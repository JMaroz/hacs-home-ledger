"""Tests for Home Ledger calculation helpers."""

from custom_components.home_ledger.calculations import (
    calculate_average_monthly_consumption,
    calculate_average_monthly_cost,
    calculate_cost_per_unit,
    calculate_total_consumption,
    calculate_total_cost,
    calculate_total_months,
)

BILLS = [
    {"utility_type": "electricity", "cost": 120.0, "consumption": 300.0, "months": 2},
    {"utility_type": "electricity", "cost": 90.0, "consumption": 150.0, "months": 1},
    {"utility_type": "gas", "cost": 80.0, "consumption": 40.0, "months": 2},
]


def test_calculate_total_cost_supports_all_or_one_utility_type() -> None:
    """Total cost can include all utility types or only one utility type."""
    assert calculate_total_cost(BILLS) == 290.0
    assert calculate_total_cost(BILLS, "electricity") == 210.0


def test_calculate_totals_for_one_utility_type() -> None:
    """Consumption and month totals only include the requested utility type."""
    assert calculate_total_consumption(BILLS, "electricity") == 450.0
    assert calculate_total_months(BILLS, "electricity") == 3


def test_calculate_monthly_averages_use_total_months() -> None:
    """Monthly averages divide by covered months, not bill count."""
    assert calculate_average_monthly_cost(BILLS, "electricity") == 70.0
    assert calculate_average_monthly_consumption(BILLS, "electricity") == 150.0


def test_calculate_cost_per_unit_returns_none_without_consumption() -> None:
    """Cost per unit is unavailable when total consumption is zero."""
    bills = [{"utility_type": "water", "cost": 25.0, "consumption": 0, "months": 1}]

    assert calculate_cost_per_unit(bills, "water") is None


def test_calculate_cost_per_unit() -> None:
    """Cost per unit divides total cost by total consumption."""
    assert calculate_cost_per_unit(BILLS, "electricity") == 210.0 / 450.0
