"""Tests for Home Ledger Bill model."""

from datetime import date

import pytest

from custom_components.home_ledger.models import Bill, UtilityType


class TestBill:
    """Tests for the Bill dataclass."""

    def test_create_bill(self) -> None:
        bill = Bill(
            id="test-1",
            utility_type="electricity",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
            total_cost=143.52,
            consumption=412.0,
        )
        assert bill.id == "test-1"
        assert bill.utility_type == UtilityType.ELECTRICITY
        assert bill.start_date == date(2026, 1, 1)
        assert bill.end_date == date(2026, 1, 31)
        assert bill.total_cost == 143.52
        assert bill.consumption == 412.0

    def test_bill_unit_of_measurement(self) -> None:
        assert (
            Bill(
                id="1",
                utility_type="electricity",
                start_date=date(2026, 1, 1),
                end_date=date(2026, 1, 31),
                total_cost=10,
                consumption=100,
            ).unit_of_measurement
            == "kWh"
        )
        assert (
            Bill(
                id="1",
                utility_type="gas",
                start_date=date(2026, 1, 1),
                end_date=date(2026, 1, 31),
                total_cost=10,
                consumption=100,
            ).unit_of_measurement
            == "m\u00b3"
        )
        assert (
            Bill(
                id="1",
                utility_type="water",
                start_date=date(2026, 1, 1),
                end_date=date(2026, 1, 31),
                total_cost=10,
                consumption=100,
            ).unit_of_measurement
            == "m\u00b3"
        )

    def test_bill_is_frozen(self) -> None:
        bill = Bill(
            id="1",
            utility_type="electricity",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
            total_cost=10,
            consumption=100,
        )
        with pytest.raises(AttributeError):
            bill.id = "changed"  # type: ignore[misc]

    def test_storage_roundtrip(self) -> None:
        bill = Bill(
            id="test-1",
            utility_type="gas",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 3, 31),
            total_cost=287.40,
            consumption=143.2,
        )
        storage_dict = bill.as_storage_dict()
        restored = Bill.from_storage_dict(storage_dict)
        assert bill == restored

    def test_invalid_id_empty(self) -> None:
        with pytest.raises(ValueError, match="id must be a non-empty string"):
            Bill(
                id="",
                utility_type="electricity",
                start_date=date(2026, 1, 1),
                end_date=date(2026, 1, 31),
                total_cost=10,
                consumption=100,
            )

    def test_invalid_id_whitespace(self) -> None:
        with pytest.raises(ValueError, match="id must be a non-empty string"):
            Bill(
                id="   ",
                utility_type="electricity",
                start_date=date(2026, 1, 1),
                end_date=date(2026, 1, 31),
                total_cost=10,
                consumption=100,
            )

    def test_invalid_dates_order(self) -> None:
        with pytest.raises(ValueError, match="end_date must be after start_date"):
            Bill(
                id="1",
                utility_type="electricity",
                start_date=date(2026, 1, 31),
                end_date=date(2026, 1, 1),
                total_cost=10,
                consumption=100,
            )

    def test_invalid_dates_same(self) -> None:
        with pytest.raises(ValueError, match="end_date must be after start_date"):
            Bill(
                id="1",
                utility_type="electricity",
                start_date=date(2026, 1, 1),
                end_date=date(2026, 1, 1),
                total_cost=10,
                consumption=100,
            )

    def test_invalid_total_cost_negative(self) -> None:
        with pytest.raises(ValueError, match="total_cost must be a non-negative number"):
            Bill(
                id="1",
                utility_type="electricity",
                start_date=date(2026, 1, 1),
                end_date=date(2026, 1, 31),
                total_cost=-10,
                consumption=100,
            )

    def test_invalid_consumption_negative(self) -> None:
        with pytest.raises(ValueError, match="consumption must be a non-negative number"):
            Bill(
                id="1",
                utility_type="electricity",
                start_date=date(2026, 1, 1),
                end_date=date(2026, 1, 31),
                total_cost=10,
                consumption=-100,
            )

    def test_invalid_utility_type(self) -> None:
        with pytest.raises(ValueError, match="utility_type must be one of"):
            Bill(
                id="1",
                utility_type="invalid",
                start_date=date(2026, 1, 1),
                end_date=date(2026, 1, 31),
                total_cost=10,
                consumption=100,
            )  # type: ignore[arg-type]

    def test_zero_cost_and_consumption(self) -> None:
        bill = Bill(
            id="1",
            utility_type="electricity",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
            total_cost=0,
            consumption=0,
        )
        assert bill.total_cost == 0
        assert bill.consumption == 0

    def test_all_utility_types(self) -> None:
        for ut in UtilityType:
            bill = Bill(
                id="1",
                utility_type=ut,
                start_date=date(2026, 1, 1),
                end_date=date(2026, 1, 31),
                total_cost=10,
                consumption=100,
            )
            assert bill.utility_type == ut
