"""Tests for Home Ledger service actions."""

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.home_ledger.const import DOMAIN
from custom_components.home_ledger.service_actions import (
    ATTR_CONSUMPTION,
    ATTR_END_DATE,
    ATTR_START_DATE,
    ATTR_TOTAL_COST,
    ATTR_UTILITY_TYPE,
    SERVICE_ADD_BILL,
    SERVICE_DELETE_BILL,
    SERVICE_LIST_BILLS,
    SERVICE_UPDATE_BILL,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError


@pytest.fixture
async def init_integration(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
) -> MockConfigEntry:
    """Set up the integration from a config entry."""
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    return config_entry


async def test_add_bill(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
) -> None:
    """Test adding a bill via service action."""
    result = await hass.services.async_call(
        DOMAIN,
        SERVICE_ADD_BILL,
        {
            "config_entry_id": init_integration.entry_id,
            ATTR_UTILITY_TYPE: "electricity",
            ATTR_START_DATE: "2026-01-01",
            ATTR_END_DATE: "2026-01-31",
            ATTR_TOTAL_COST: 143.52,
            ATTR_CONSUMPTION: 412.0,
        },
        blocking=True,
        return_response=True,
    )

    assert "bill" in result
    bill = result["bill"]
    assert bill[ATTR_UTILITY_TYPE] == "electricity"
    assert bill[ATTR_START_DATE] == "2026-01-01"
    assert bill[ATTR_END_DATE] == "2026-01-31"
    assert bill[ATTR_TOTAL_COST] == 143.52
    assert bill[ATTR_CONSUMPTION] == 412.0
    assert "id" in bill


async def test_add_bill_with_custom_id(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
) -> None:
    """Test adding a bill with a custom ID."""
    custom_id = "electricity_january"
    result = await hass.services.async_call(
        DOMAIN,
        SERVICE_ADD_BILL,
        {
            "config_entry_id": init_integration.entry_id,
            "bill_id": custom_id,
            ATTR_UTILITY_TYPE: "electricity",
            ATTR_START_DATE: "2026-01-01",
            ATTR_END_DATE: "2026-01-31",
            ATTR_TOTAL_COST: 100.0,
            ATTR_CONSUMPTION: 250.0,
        },
        blocking=True,
        return_response=True,
    )

    assert result["bill"]["id"] == custom_id


async def test_add_multiple_bills(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
) -> None:
    """Test adding multiple bills."""
    # Add first bill
    result1 = await hass.services.async_call(
        DOMAIN,
        SERVICE_ADD_BILL,
        {
            "config_entry_id": init_integration.entry_id,
            ATTR_UTILITY_TYPE: "electricity",
            ATTR_START_DATE: "2026-01-01",
            ATTR_END_DATE: "2026-01-31",
            ATTR_TOTAL_COST: 100.0,
            ATTR_CONSUMPTION: 200.0,
        },
        blocking=True,
        return_response=True,
    )

    # Add second bill
    result2 = await hass.services.async_call(
        DOMAIN,
        SERVICE_ADD_BILL,
        {
            "config_entry_id": init_integration.entry_id,
            ATTR_UTILITY_TYPE: "gas",
            ATTR_START_DATE: "2026-02-01",
            ATTR_END_DATE: "2026-02-28",
            ATTR_TOTAL_COST: 200.0,
            ATTR_CONSUMPTION: 150.0,
        },
        blocking=True,
        return_response=True,
    )

    assert result1["bill"]["id"] != result2["bill"]["id"]

    # List bills should return both
    list_result = await hass.services.async_call(
        DOMAIN,
        SERVICE_LIST_BILLS,
        {"config_entry_id": init_integration.entry_id},
        blocking=True,
        return_response=True,
    )

    assert len(list_result["bills"]) == 2


async def test_update_bill(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
) -> None:
    """Test updating a bill."""
    # Add a bill first
    add_result = await hass.services.async_call(
        DOMAIN,
        SERVICE_ADD_BILL,
        {
            "config_entry_id": init_integration.entry_id,
            ATTR_UTILITY_TYPE: "electricity",
            ATTR_START_DATE: "2026-01-01",
            ATTR_END_DATE: "2026-01-31",
            ATTR_TOTAL_COST: 100.0,
            ATTR_CONSUMPTION: 200.0,
        },
        blocking=True,
        return_response=True,
    )

    bill_id = add_result["bill"]["id"]

    # Update the bill
    update_result = await hass.services.async_call(
        DOMAIN,
        SERVICE_UPDATE_BILL,
        {
            "config_entry_id": init_integration.entry_id,
            "bill_id": bill_id,
            ATTR_TOTAL_COST: 150.0,
            ATTR_CONSUMPTION: 300.0,
        },
        blocking=True,
        return_response=True,
    )

    assert update_result["bill"][ATTR_TOTAL_COST] == 150.0
    assert update_result["bill"][ATTR_CONSUMPTION] == 300.0
    assert update_result["bill"][ATTR_START_DATE] == "2026-01-01"  # unchanged
    assert update_result["bill"][ATTR_END_DATE] == "2026-01-31"  # unchanged


async def test_delete_bill(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
) -> None:
    """Test deleting a bill."""
    # Add a bill first
    add_result = await hass.services.async_call(
        DOMAIN,
        SERVICE_ADD_BILL,
        {
            "config_entry_id": init_integration.entry_id,
            ATTR_UTILITY_TYPE: "electricity",
            ATTR_START_DATE: "2026-01-01",
            ATTR_END_DATE: "2026-01-31",
            ATTR_TOTAL_COST: 50.0,
            ATTR_CONSUMPTION: 100.0,
        },
        blocking=True,
        return_response=True,
    )

    bill_id = add_result["bill"]["id"]

    # Delete the bill
    delete_result = await hass.services.async_call(
        DOMAIN,
        SERVICE_DELETE_BILL,
        {
            "config_entry_id": init_integration.entry_id,
            "bill_id": bill_id,
        },
        blocking=True,
        return_response=True,
    )

    assert delete_result["bill_id"] == bill_id

    # List should be empty
    list_result = await hass.services.async_call(
        DOMAIN,
        SERVICE_LIST_BILLS,
        {"config_entry_id": init_integration.entry_id},
        blocking=True,
        return_response=True,
    )

    assert len(list_result["bills"]) == 0


async def test_delete_nonexistent_bill(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
) -> None:
    """Test deleting a non-existent bill raises error."""
    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            DOMAIN,
            SERVICE_DELETE_BILL,
            {
                "config_entry_id": init_integration.entry_id,
                "bill_id": "nonexistent",
            },
            blocking=True,
        )
