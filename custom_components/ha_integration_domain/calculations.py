"""Pure bill calculations for the home ledger."""

from collections.abc import Iterable
from decimal import Decimal

Bill = dict[str, str | int | float]


def total_cost(bills: Iterable[Bill]) -> Decimal:
    """Return the sum of every bill cost."""
    return sum((Decimal(str(bill["cost"])) for bill in bills), Decimal(0))


def total_consumption(bills: Iterable[Bill]) -> Decimal:
    """Return the sum of every bill consumption value."""
    return sum((Decimal(str(bill["consumption"])) for bill in bills), Decimal(0))


def total_months(bills: Iterable[Bill]) -> int:
    """Return the number of months covered by all bills."""
    return sum(int(bill["months"]) for bill in bills)


def monthly_average(bills: Iterable[Bill]) -> Decimal:
    """Return the average cost per covered month."""
    bill_list = list(bills)
    months = total_months(bill_list)
    if months == 0:
        return Decimal(0)
    return total_cost(bill_list) / Decimal(months)


def cost_per_unit(bills: Iterable[Bill]) -> Decimal:
    """Return the average cost per consumption unit."""
    bill_list = list(bills)
    consumption = total_consumption(bill_list)
    if consumption == 0:
        return Decimal(0)
    return total_cost(bill_list) / consumption
