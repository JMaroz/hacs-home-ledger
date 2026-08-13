"""Service action handlers for ledger bills."""

from typing import Any

from custom_components.ha_integration_domain.data import IntegrationBlueprintConfigEntry
from homeassistant.core import ServiceCall, ServiceResponse

ATTR_BILL_ID = "bill_id"
ATTR_CONFIG_ENTRY_ID = "config_entry_id"
ATTR_CONSUMPTION = "consumption"
ATTR_COST = "cost"
ATTR_MONTHS = "months"
ATTR_UTILITY = "utility"


async def async_handle_add_bill(entry: IntegrationBlueprintConfigEntry, call: ServiceCall) -> ServiceResponse:
    """Add a bill to the ledger."""
    bill_id = await entry.runtime_data.ledger.async_add_bill(
        call.data[ATTR_UTILITY],
        call.data[ATTR_COST],
        call.data[ATTR_CONSUMPTION],
        call.data[ATTR_MONTHS],
    )
    await entry.runtime_data.coordinator.async_refresh()
    return {ATTR_BILL_ID: bill_id}


async def async_handle_update_bill(entry: IntegrationBlueprintConfigEntry, call: ServiceCall) -> None:
    """Update a bill in the ledger."""
    updates: dict[str, Any] = {
        ATTR_UTILITY: call.data.get(ATTR_UTILITY),
        ATTR_COST: call.data.get(ATTR_COST),
        ATTR_CONSUMPTION: call.data.get(ATTR_CONSUMPTION),
        ATTR_MONTHS: call.data.get(ATTR_MONTHS),
    }
    await entry.runtime_data.ledger.async_update_bill(call.data[ATTR_BILL_ID], updates)
    await entry.runtime_data.coordinator.async_refresh()


async def async_handle_delete_bill(entry: IntegrationBlueprintConfigEntry, call: ServiceCall) -> None:
    """Delete a bill from the ledger."""
    await entry.runtime_data.ledger.async_delete_bill(call.data[ATTR_BILL_ID])
    await entry.runtime_data.coordinator.async_refresh()
