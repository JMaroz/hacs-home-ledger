"""Pure calculation helpers for Home Ledger bills."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from custom_components.home_ledger.models import Bill


def calculate_total_cost(
    bills: list[Bill],
    utility_type: str | None = None,
) -> float:
    """Calculate the total cost for the selected bills."""
    return sum(bill.total_cost for bill in bills if utility_type is None or bill.utility_type == utility_type)


def calculate_total_consumption(
    bills: list[Bill],
    utility_type: str,
) -> float:
    """Calculate the total consumption for one utility type."""
    return sum(bill.consumption for bill in bills if bill.utility_type == utility_type)


def calculate_total_months(
    bills: list[Bill],
    utility_type: str,
) -> int:
    """Calculate the covered months for one utility type."""
    return sum(bill.months for bill in bills if bill.utility_type == utility_type)


def calculate_average_monthly_cost(
    bills: list[Bill],
    utility_type: str,
) -> float | None:
    """Calculate the average monthly cost for one utility type."""
    total_cost = calculate_total_cost(bills, utility_type)
    total_months = calculate_total_months(bills, utility_type)
    if total_months == 0:
        return None
    return total_cost / total_months


def calculate_average_monthly_consumption(
    bills: list[Bill],
    utility_type: str,
) -> float | None:
    """Calculate the average monthly consumption for one utility type."""
    total_consumption = calculate_total_consumption(bills, utility_type)
    total_months = calculate_total_months(bills, utility_type)
    if total_months == 0:
        return None
    return total_consumption / total_months


def calculate_cost_per_unit(
    bills: list[Bill],
    utility_type: str,
) -> float | None:
    """Calculate cost per consumed unit for one utility type."""
    total_cost = calculate_total_cost(bills, utility_type)
    total_consumption = calculate_total_consumption(bills, utility_type)
    if total_consumption == 0:
        return None
    return total_cost / total_consumption
