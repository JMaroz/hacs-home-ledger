"""Tests for the Home Ledger integration setup."""

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.home_ledger.const import DOMAIN
from custom_components.home_ledger.service_actions import (
    ATTR_CONSUMPTION,
    ATTR_MONTHS,
    ATTR_TOTAL_COST,
    ATTR_UTILITY_TYPE,
    SERVICE_ADD_BILL,
    SERVICE_LIST_BILLS,
)
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr


async def test_entry_loads_successfully(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
) -> None:
    """Test that the integration loads successfully."""
    config_entry.add_to_hass(hass)
    result = await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    assert result is True
    assert config_entry.state is ConfigEntryState.LOADED


async def test_entry_creates_device(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
) -> None:
    """Test that the integration creates a device."""
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    devices = dr.async_entries_for_config_entry(dr.async_get(hass), config_entry.entry_id)
    assert len(devices) == 1
    assert devices[0].name == "Home Ledger"
    assert devices[0].manufacturer == "Home Ledger"
    assert devices[0].model == "Home Ledger"


async def test_entry_unloads_successfully(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
) -> None:
    """Test that the integration unloads successfully."""
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    assert await hass.config_entries.async_unload(config_entry.entry_id)
    await hass.async_block_till_done()

    assert config_entry.state is ConfigEntryState.NOT_LOADED


async def test_persistence_after_reload(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
) -> None:
    """Test that bills persist after integration reload."""
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    # Add a bill
    await hass.services.async_call(
        DOMAIN,
        SERVICE_ADD_BILL,
        {
            "config_entry_id": config_entry.entry_id,
            ATTR_UTILITY_TYPE: "electricity",
            ATTR_MONTHS: 2,
            ATTR_TOTAL_COST: 143.52,
            ATTR_CONSUMPTION: 412.0,
        },
        blocking=True,
    )

    # Reload the integration
    await hass.config_entries.async_reload(config_entry.entry_id)
    await hass.async_block_till_done()

    # Verify the bill is still there via list_bills
    result = await hass.services.async_call(
        DOMAIN,
        SERVICE_LIST_BILLS,
        {"config_entry_id": config_entry.entry_id},
        blocking=True,
        return_response=True,
    )

    assert len(result["bills"]) == 1
    assert result["bills"][0][ATTR_UTILITY_TYPE] == "electricity"
    assert result["bills"][0][ATTR_TOTAL_COST] == 143.52


async def test_sensors_update_after_bill_change(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
) -> None:
    """Test that sensors update when bills are added."""
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    # Add a bill
    await hass.services.async_call(
        DOMAIN,
        SERVICE_ADD_BILL,
        {
            "config_entry_id": config_entry.entry_id,
            ATTR_UTILITY_TYPE: "electricity",
            ATTR_MONTHS: 2,
            ATTR_TOTAL_COST: 143.52,
            ATTR_CONSUMPTION: 412.0,
        },
        blocking=True,
    )
    await hass.async_block_till_done()

    # Check sensor updated - find the entity by looking at all states
    found = False
    for state in hass.states.async_all():
        if "total_electricity_cost" in state.entity_id:
            assert state.state == "143.52"
            found = True
            break
    assert found, "Could not find sensor with total_electricity_cost in entity_id"
