"""Tests for Home Ledger calculation functions."""

from datetime import date

import pytest

from custom_components.home_ledger.calculations import (
    calculate_average_monthly_consumption,
    calculate_average_monthly_cost,
    calculate_cost_per_unit,
    calculate_pv_savings,
    calculate_total_consumption,
    calculate_total_cost,
    calculate_total_days,
)
from custom_components.home_ledger.models import Bill


def _bill(
    utility_type: str = "electricity",
    start_date: date = date(2026, 1, 1),
    end_date: date = date(2026, 1, 31),
    total_cost: float = 100.0,
    consumption: float = 200.0,
) -> Bill:
    """Create a test bill."""
    return Bill(
        id="test",
        utility_type=utility_type,
        start_date=start_date,
        end_date=end_date,
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


class TestCalculateTotalDays:
    """Tests for calculate_total_days."""

    def test_empty_list(self) -> None:
        assert calculate_total_days([], "electricity") == 0

    def test_single_bill(self) -> None:
        # Jan 1 to Jan 31 = 31 days
        bills = [_bill(start_date=date(2026, 1, 1), end_date=date(2026, 1, 31))]
        assert calculate_total_days(bills, "electricity") == 31

    def test_multiple_bills(self) -> None:
        bills = [
            _bill(start_date=date(2026, 1, 1), end_date=date(2026, 1, 10)),  # 10 days
            _bill(start_date=date(2026, 1, 11), end_date=date(2026, 1, 20)),  # 10 days
        ]
        assert calculate_total_days(bills, "electricity") == 20


class TestCalculateAverageMonthlyCost:
    """Tests for calculate_average_monthly_cost."""

    def test_empty_list(self) -> None:
        assert calculate_average_monthly_cost([], "electricity") is None

    def test_single_bill(self) -> None:
        # 30 days, cost 300 -> 10/day -> 10 * 30.44 = 304.4
        bills = [_bill(start_date=date(2026, 1, 1), end_date=date(2026, 1, 30), total_cost=300.0)]
        assert calculate_average_monthly_cost(bills, "electricity") == pytest.approx(304.4, 0.01)

    def test_multiple_bills(self) -> None:
        # Total cost = 300, total days = 30 -> 10/day -> 304.4
        bills = [
            _bill(start_date=date(2026, 1, 1), end_date=date(2026, 1, 15), total_cost=150.0),
            _bill(start_date=date(2026, 1, 16), end_date=date(2026, 1, 30), total_cost=150.0),
        ]
        assert calculate_average_monthly_cost(bills, "electricity") == pytest.approx(304.4, 0.01)


class TestCalculateAverageMonthlyConsumption:
    """Tests for calculate_average_monthly_consumption."""

    def test_empty_list(self) -> None:
        assert calculate_average_monthly_consumption([], "electricity") is None

    def test_single_bill(self) -> None:
        # 30 days, cons 300 -> 10/day -> 10 * 30.44 = 304.4
        bills = [_bill(start_date=date(2026, 1, 1), end_date=date(2026, 1, 30), consumption=300.0)]
        assert calculate_average_monthly_consumption(bills, "electricity") == pytest.approx(304.4, 0.01)

    def test_multiple_bills(self) -> None:
        bills = [
            _bill(start_date=date(2026, 1, 1), end_date=date(2026, 1, 15), consumption=150.0),
            _bill(start_date=date(2026, 1, 16), end_date=date(2026, 1, 30), consumption=150.0),
        ]
        assert calculate_average_monthly_consumption(bills, "electricity") == pytest.approx(304.4, 0.01)


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


class TestCalculatePVSavings:
    """Tests for calculate_pv_savings with GSE compensation."""

    def test_pv_savings_without_export(self) -> None:
        assert calculate_pv_savings(production=100.0, cost_per_unit=0.25) == 25.0

    def test_pv_savings_with_export_none_mode(self) -> None:
        # Production 100, export 40 -> self-consumed 60 @ 0.25 = 15.0 (export earning 0)
        savings = calculate_pv_savings(
            production=100.0,
            cost_per_unit=0.25,
            grid_export=40.0,
            gse_mode="none",
        )
        assert savings == 15.0

    def test_pv_savings_with_ssp_mode(self) -> None:
        # Self-consumed 60 @ 0.25 = 15.0, exported 40 @ 0.10 = 4.0 -> total 19.0
        savings = calculate_pv_savings(
            production=100.0,
            cost_per_unit=0.25,
            grid_export=40.0,
            export_tariff=0.10,
            gse_mode="ssp",
        )
        assert savings == 19.0

    def test_pv_savings_with_rid_mode(self) -> None:
        # Self-consumed 60 @ 0.25 = 15.0, exported 40 @ 0.12 = 4.8 -> total 19.8
        savings = calculate_pv_savings(
            production=100.0,
            cost_per_unit=0.25,
            grid_export=40.0,
            export_tariff=0.12,
            gse_mode="rid",
        )
        assert savings == 19.8
