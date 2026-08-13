"""Handlers for bill service actions."""

from datetime import date
from typing import TYPE_CHECKING, Any, cast
from uuid import uuid4

from custom_components.home_ledger.const import DOMAIN
from homeassistant.config_entries import ConfigEntryState
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.storage import Store

if TYPE_CHECKING:
    from custom_components.home_ledger.data import HomeLedgerConfigEntry
    from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse

ATTR_AMOUNT = "amount"
ATTR_BILL_ID = "bill_id"
ATTR_CONFIG_ENTRY_ID = "config_entry_id"
ATTR_DUE_DATE = "due_date"
ATTR_NAME = "name"
ATTR_PAID = "paid"
ATTR_RECURRENCE = "recurrence"

STORAGE_VERSION = 1

Bill = dict[str, Any]
BillStoreData = dict[str, list[Bill]]


async def async_handle_add_bill(hass: HomeAssistant, call: ServiceCall) -> ServiceResponse:
    """Add a bill and return the stored bill."""
    entry = _async_get_loaded_entry(hass, call.data[ATTR_CONFIG_ENTRY_ID])
    bill = _bill_from_call(call, bill_id=call.data.get(ATTR_BILL_ID) or uuid4().hex)

    bills = await _async_load_bills(hass, entry)
    if any(existing[ATTR_BILL_ID] == bill[ATTR_BILL_ID] for existing in bills):
        raise ServiceValidationError(
            translation_domain=DOMAIN,
            translation_key="bill_already_exists",
            translation_placeholders={"bill_id": bill[ATTR_BILL_ID]},
        )

    bills.append(bill)
    await _async_save_bills(hass, entry, bills)
    _async_update_coordinator_bills(entry, bills)
    return {"bill": bill}


async def async_handle_update_bill(hass: HomeAssistant, call: ServiceCall) -> ServiceResponse:
    """Update an existing bill and return the stored bill."""
    entry = _async_get_loaded_entry(hass, call.data[ATTR_CONFIG_ENTRY_ID])
    bill_id: str = call.data[ATTR_BILL_ID]
    bills = await _async_load_bills(hass, entry)
    index = _bill_index(bills, bill_id)
    current = bills[index]
    updated = {
        **current,
        **_bill_updates_from_call(call),
    }

    bills[index] = updated
    await _async_save_bills(hass, entry, bills)
    _async_update_coordinator_bills(entry, bills)
    return {"bill": updated}


async def async_handle_delete_bill(hass: HomeAssistant, call: ServiceCall) -> ServiceResponse:
    """Delete an existing bill."""
    entry = _async_get_loaded_entry(hass, call.data[ATTR_CONFIG_ENTRY_ID])
    bill_id: str = call.data[ATTR_BILL_ID]
    bills = await _async_load_bills(hass, entry)
    index = _bill_index(bills, bill_id)
    deleted = bills.pop(index)

    await _async_save_bills(hass, entry, bills)
    _async_update_coordinator_bills(entry, bills)
    return {"bill": deleted}


async def async_handle_list_bills(hass: HomeAssistant, call: ServiceCall) -> ServiceResponse:
    """Return every stored bill."""
    entry = _async_get_loaded_entry(hass, call.data[ATTR_CONFIG_ENTRY_ID])
    bills = await _async_load_bills(hass, entry)
    return cast("ServiceResponse", {"bills": bills})


def _async_get_loaded_entry(hass: HomeAssistant, entry_id: str) -> HomeLedgerConfigEntry:
    """Resolve a config entry id to a loaded entry."""
    entry = hass.config_entries.async_get_entry(entry_id)
    if entry is None or entry.domain != DOMAIN:
        raise ServiceValidationError(
            translation_domain=DOMAIN,
            translation_key="entry_not_found",
            translation_placeholders={"target": entry_id},
        )
    if entry.state is not ConfigEntryState.LOADED:
        raise ServiceValidationError(
            translation_domain=DOMAIN,
            translation_key="entry_not_loaded",
            translation_placeholders={"target": entry.title},
        )
    return entry


def _bill_from_call(call: ServiceCall, bill_id: str) -> Bill:
    return {
        ATTR_BILL_ID: bill_id,
        ATTR_NAME: call.data[ATTR_NAME],
        ATTR_AMOUNT: call.data[ATTR_AMOUNT],
        ATTR_DUE_DATE: _date_to_storage(call.data[ATTR_DUE_DATE]),
        ATTR_PAID: call.data[ATTR_PAID],
        ATTR_RECURRENCE: call.data.get(ATTR_RECURRENCE),
    }


def _bill_updates_from_call(call: ServiceCall) -> Bill:
    updates: Bill = {}
    for attr in (ATTR_NAME, ATTR_AMOUNT, ATTR_DUE_DATE, ATTR_PAID, ATTR_RECURRENCE):
        if attr in call.data:
            updates[attr] = _date_to_storage(call.data[attr]) if attr == ATTR_DUE_DATE else call.data[attr]
    return updates


def _date_to_storage(value: date | str) -> str:
    if isinstance(value, date):
        return value.isoformat()
    return value


def _bill_index(bills: list[Bill], bill_id: str) -> int:
    for index, bill in enumerate(bills):
        if bill[ATTR_BILL_ID] == bill_id:
            return index
    raise ServiceValidationError(
        translation_domain=DOMAIN,
        translation_key="bill_not_found",
        translation_placeholders={"bill_id": bill_id},
    )


async def _async_load_bills(hass: HomeAssistant, entry: HomeLedgerConfigEntry) -> list[Bill]:
    data = await _store(hass, entry).async_load()
    return list(data["bills"]) if data is not None else []


async def _async_save_bills(hass: HomeAssistant, entry: HomeLedgerConfigEntry, bills: list[Bill]) -> None:
    await _store(hass, entry).async_save({"bills": bills})


def _store(hass: HomeAssistant, entry: HomeLedgerConfigEntry) -> Store[BillStoreData]:
    return Store(hass, STORAGE_VERSION, f"{DOMAIN}.{entry.entry_id}.bills")


def _async_update_coordinator_bills(entry: HomeLedgerConfigEntry, bills: list[Bill]) -> None:
    coordinator = entry.runtime_data.coordinator
    data = dict(coordinator.data or {})
    data["bills"] = bills
    coordinator.async_set_updated_data(data)
