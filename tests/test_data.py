"""Tests for bill aggregation."""

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.home_ledger.data import HomeLedgerBillStorageManager
from homeassistant.core import HomeAssistant


async def test_bill_storage_aggregates_persisted_bills(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """The storage manager calculates totals from persisted bills."""
    manager = HomeLedgerBillStorageManager(hass, mock_config_entry.entry_id)

    aggregates = await manager.async_replace_bills(
        [
            {"amount": "10.50", "currency": "EUR", "due_date": "2026-01-01", "paid": True},
            {"amount": "5.25", "currency": "EUR", "due_date": "2026-01-02", "paid": False},
        ]
    )

    assert aggregates.bill_count == 2
    assert aggregates.currency == "EUR"
    assert aggregates.paid_amount == 10.5
    assert aggregates.unpaid_amount == 5.25
    assert aggregates.total_amount == 15.75
