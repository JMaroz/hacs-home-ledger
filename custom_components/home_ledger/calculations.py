"""Pure calculation helpers for Home Ledger bills."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from custom_components.home_ledger.models import Bill

DAYS_IN_MONTH = 30.44


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


def calculate_total_days(
    bills: list[Bill],
    utility_type: str,
) -> int:
    """Calculate total days covered by bills for one utility type."""
    return sum((bill.end_date - bill.start_date).days + 1 for bill in bills if bill.utility_type == utility_type)


def calculate_average_monthly_cost(
    bills: list[Bill],
    utility_type: str,
) -> float | None:
    """Calculate the average monthly cost for one utility type."""
    total_cost = calculate_total_cost(bills, utility_type)
    total_days = calculate_total_days(bills, utility_type)
    if total_days == 0:
        return None
    return (total_cost / total_days) * DAYS_IN_MONTH


def calculate_average_monthly_consumption(
    bills: list[Bill],
    utility_type: str,
) -> float | None:
    """Calculate the average monthly consumption for one utility type."""
    total_consumption = calculate_total_consumption(bills, utility_type)
    total_days = calculate_total_days(bills, utility_type)
    if total_days == 0:
        return None
    return (total_consumption / total_days) * DAYS_IN_MONTH


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


def calculate_pv_savings(
    production: float,
    cost_per_unit: float,
    grid_export: float | None = None,
    export_tariff: float = 0.0,
) -> float:
    """Calculate the monetary savings from PV production."""
    if grid_export is not None:
        self_consumed = max(0.0, production - grid_export)
        return (self_consumed * cost_per_unit) + (grid_export * export_tariff)

    return production * cost_per_unit


def calculate_roi_payback(
    net_investment: float,
    annual_savings: float,
) -> float | None:
    """Calculate the payback period in years."""
    if annual_savings <= 0:
        return None
    return net_investment / annual_savings
