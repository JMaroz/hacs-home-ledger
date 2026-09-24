"""Pure calculation helpers for Home Ledger bills."""

from datetime import date, timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from custom_components.home_ledger.models import Bill

DAYS_IN_MONTH = 30.44


def _month_key(dt: date) -> str:
    """Return YYYY-MM string for a date."""
    return f"{dt.year}-{dt.month:02d}"


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


def calculate_monthly_costs(
    bills: list[Bill],
    utility_type: str,
) -> dict[str, float]:
    """Calculate total cost per month (YYYY-MM) for one utility type."""
    monthly: dict[str, float] = {}
    for bill in bills:
        if bill.utility_type != utility_type:
            continue
        # Distribute bill cost across months it spans
        current = bill.start_date
        while current <= bill.end_date:
            key = _month_key(current)
            month_start = date(current.year, current.month, 1)
            if current.month == 12:
                month_end = date(current.year + 1, 1, 1)
            else:
                month_end = date(current.year, current.month + 1, 1)
            bill_days_in_month = (
                min(bill.end_date, month_end - timedelta(days=1))
                - max(bill.start_date, month_start)
                + timedelta(days=1)
            )
            bill_days_in_month = bill_days_in_month.days
            if bill_days_in_month > 0:
                total_bill_days = (bill.end_date - bill.start_date).days + 1
                monthly[key] = monthly.get(key, 0.0) + bill.total_cost * (bill_days_in_month / total_bill_days)
            # Move to next month
            if current.month == 12:
                current = date(current.year + 1, 1, 1)
            else:
                current = date(current.year, current.month + 1, 1)
    return monthly


def calculate_monthly_consumption(
    bills: list[Bill],
    utility_type: str,
) -> dict[str, float]:
    """Calculate total consumption per month (YYYY-MM) for one utility type."""
    monthly: dict[str, float] = {}
    for bill in bills:
        if bill.utility_type != utility_type:
            continue
        current = bill.start_date
        while current <= bill.end_date:
            key = _month_key(current)
            month_start = date(current.year, current.month, 1)
            if current.month == 12:
                month_end = date(current.year + 1, 1, 1)
            else:
                month_end = date(current.year, current.month + 1, 1)
            bill_days_in_month = (
                min(bill.end_date, month_end - timedelta(days=1))
                - max(bill.start_date, month_start)
                + timedelta(days=1)
            )
            bill_days_in_month = bill_days_in_month.days
            if bill_days_in_month > 0:
                total_bill_days = (bill.end_date - bill.start_date).days + 1
                monthly[key] = monthly.get(key, 0.0) + bill.consumption * (bill_days_in_month / total_bill_days)
            if current.month == 12:
                current = date(current.year + 1, 1, 1)
            else:
                current = date(current.year, current.month + 1, 1)
    return monthly


def calculate_pv_savings(
    production: float,
    cost_per_unit: float,
    grid_export: float | None = None,
    export_tariff: float = 0.0,
    gse_mode: str = "none",
) -> float:
    """Calculate the monetary savings and GSE compensation from PV production."""
    if grid_export is not None:
        self_consumed = max(0.0, production - grid_export)
        self_consumption_savings = self_consumed * cost_per_unit
        effective_tariff = export_tariff if gse_mode in ("ssp", "rid") or export_tariff > 0 else 0.0
        export_compensation = grid_export * effective_tariff
        return self_consumption_savings + export_compensation

    return production * cost_per_unit


def calculate_roi_payback(
    net_investment: float,
    annual_savings: float,
) -> float | None:
    """Calculate the payback period in years."""
    if annual_savings <= 0:
        return None
    return net_investment / annual_savings
