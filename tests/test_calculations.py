"""Pure tests for ledger calculations."""

from decimal import Decimal

import pytest

from custom_components.ha_integration_domain.calculations import (
    cost_per_unit,
    monthly_average,
    total_consumption,
    total_cost,
    total_months,
)

BILLS = [
    {"utility": "electricity", "cost": 60, "consumption": 120, "months": 2},
    {"utility": "gas", "cost": 30, "consumption": 60, "months": 1},
]


@pytest.mark.unit
def test_total_cost() -> None:
    """Total cost sums every bill."""
    assert total_cost(BILLS) == Decimal(90)


@pytest.mark.unit
def test_total_consumption() -> None:
    """Total consumption sums every bill."""
    assert total_consumption(BILLS) == Decimal(180)


@pytest.mark.unit
def test_total_months() -> None:
    """Total months sums the months field."""
    assert total_months(BILLS) == 3


@pytest.mark.unit
def test_monthly_average_uses_months() -> None:
    """Monthly average is based on covered months, not bill count."""
    assert monthly_average(BILLS) == Decimal(30)


@pytest.mark.unit
def test_cost_per_unit() -> None:
    """Cost per unit divides total cost by total consumption."""
    assert cost_per_unit(BILLS) == Decimal("0.5")


@pytest.mark.unit
def test_zero_consumption_does_not_divide_by_zero() -> None:
    """Zero consumption produces a zero unit cost."""
    assert cost_per_unit([{"utility": "water", "cost": 10, "consumption": 0, "months": 1}]) == Decimal(0)
