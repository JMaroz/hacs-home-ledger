"""Pure calculation helpers for Home Ledger bills."""

from collections.abc import Iterable, Mapping

type Bill = Mapping[str, object]
type Number = int | float


def calculate_total_cost(bills: Iterable[Bill], utility_type: str | None = None) -> float:
    """Calculate the total cost for the selected bills."""
    return sum(_as_number(bill.get("cost", bill.get("total_cost", 0))) for bill in _matching_bills(bills, utility_type))


def calculate_total_consumption(bills: Iterable[Bill], utility_type: str) -> float:
    """Calculate the total consumption for one utility type."""
    return sum(_as_number(bill.get("consumption", 0)) for bill in _matching_bills(bills, utility_type))


def calculate_total_months(bills: Iterable[Bill], utility_type: str) -> float:
    """Calculate the covered months for one utility type."""
    return sum(_as_number(bill.get("months", 0)) for bill in _matching_bills(bills, utility_type))


def calculate_average_monthly_cost(bills: Iterable[Bill], utility_type: str) -> float | None:
    """Calculate the average monthly cost for one utility type."""
    matching_bills = list(_matching_bills(bills, utility_type))
    total_months = calculate_total_months(matching_bills, utility_type)
    if total_months == 0:
        return None
    return calculate_total_cost(matching_bills, utility_type) / total_months


def calculate_average_monthly_consumption(bills: Iterable[Bill], utility_type: str) -> float | None:
    """Calculate the average monthly consumption for one utility type."""
    matching_bills = list(_matching_bills(bills, utility_type))
    total_months = calculate_total_months(matching_bills, utility_type)
    if total_months == 0:
        return None
    return calculate_total_consumption(matching_bills, utility_type) / total_months


def calculate_cost_per_unit(bills: Iterable[Bill], utility_type: str) -> float | None:
    """Calculate cost per consumed unit for one utility type."""
    matching_bills = list(_matching_bills(bills, utility_type))
    total_consumption = calculate_total_consumption(matching_bills, utility_type)
    if total_consumption == 0:
        return None
    return calculate_total_cost(matching_bills, utility_type) / total_consumption


def _matching_bills(bills: Iterable[Bill], utility_type: str | None) -> Iterable[Bill]:
    for bill in bills:
        if utility_type is None or bill.get("utility_type") == utility_type:
            yield bill


def _as_number(value: object) -> Number:
    if isinstance(value, int | float):
        return value
    return 0
