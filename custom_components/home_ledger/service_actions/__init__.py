"""Service action registration for home_ledger."""

from collections.abc import Callable, Coroutine
from typing import TYPE_CHECKING
from uuid import uuid4

import voluptuous as vol

from custom_components.home_ledger.const import DOMAIN
from custom_components.home_ledger.models import Bill, UtilityType
from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.core import SupportsResponse
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse

SERVICE_ADD_BILL = "add_bill"
SERVICE_DELETE_BILL = "delete_bill"
SERVICE_LIST_BILLS = "list_bills"
SERVICE_UPDATE_BILL = "update_bill"

ATTR_BILL_ID = "bill_id"
ATTR_CONFIG_ENTRY_ID = "config_entry_id"
ATTR_CONSUMPTION = "consumption"
ATTR_MONTHS = "months"
ATTR_TOTAL_COST = "total_cost"
ATTR_UTILITY_TYPE = "utility_type"

POSITIVE_INT = vol.All(vol.Coerce(int), vol.Range(min=1))
NON_NEGATIVE_FLOAT = vol.All(vol.Coerce(float), vol.Range(min=0))

UTILITY_TYPE_VALUES = [ut.value for ut in UtilityType]

ADD_BILL_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_CONFIG_ENTRY_ID): cv.string,
        vol.Optional(ATTR_BILL_ID): cv.string,
        vol.Required(ATTR_UTILITY_TYPE): vol.In(UTILITY_TYPE_VALUES),
        vol.Required(ATTR_MONTHS): POSITIVE_INT,
        vol.Required(ATTR_TOTAL_COST): NON_NEGATIVE_FLOAT,
        vol.Required(ATTR_CONSUMPTION): NON_NEGATIVE_FLOAT,
    },
)

UPDATE_BILL_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_CONFIG_ENTRY_ID): cv.string,
        vol.Required(ATTR_BILL_ID): cv.string,
        vol.Optional(ATTR_UTILITY_TYPE): vol.In(UTILITY_TYPE_VALUES),
        vol.Optional(ATTR_MONTHS): POSITIVE_INT,
        vol.Optional(ATTR_TOTAL_COST): NON_NEGATIVE_FLOAT,
        vol.Optional(ATTR_CONSUMPTION): NON_NEGATIVE_FLOAT,
    },
)

DELETE_BILL_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_CONFIG_ENTRY_ID): cv.string,
        vol.Required(ATTR_BILL_ID): cv.string,
    },
)

LIST_BILLS_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_CONFIG_ENTRY_ID): cv.string,
    },
)


async def async_setup_services(hass: HomeAssistant) -> None:
    """Register the integration's service actions once, at component level."""

    async def handle_add_bill(call: ServiceCall) -> ServiceResponse:
        return await _async_handle_add_bill(hass, call)

    async def handle_update_bill(call: ServiceCall) -> ServiceResponse:
        return await _async_handle_update_bill(hass, call)

    async def handle_delete_bill(call: ServiceCall) -> ServiceResponse:
        return await _async_handle_delete_bill(hass, call)

    async def handle_list_bills(call: ServiceCall) -> ServiceResponse:
        return await _async_handle_list_bills(hass, call)

    _async_register_service(hass, SERVICE_ADD_BILL, handle_add_bill, ADD_BILL_SCHEMA, SupportsResponse.OPTIONAL)
    _async_register_service(
        hass, SERVICE_UPDATE_BILL, handle_update_bill, UPDATE_BILL_SCHEMA, SupportsResponse.OPTIONAL
    )
    _async_register_service(
        hass, SERVICE_DELETE_BILL, handle_delete_bill, DELETE_BILL_SCHEMA, SupportsResponse.OPTIONAL
    )
    _async_register_service(hass, SERVICE_LIST_BILLS, handle_list_bills, LIST_BILLS_SCHEMA, SupportsResponse.ONLY)


def _async_register_service(
    hass: HomeAssistant,
    service: str,
    handler: Callable[[ServiceCall], Coroutine[object, object, ServiceResponse]],
    schema: vol.Schema,
    supports_response: SupportsResponse,
) -> None:
    if not hass.services.has_service(DOMAIN, service):
        hass.services.async_register(
            DOMAIN,
            service,
            handler,
            schema=schema,
            supports_response=supports_response,
        )


def _async_get_loaded_entry(hass: HomeAssistant, entry_id: str) -> ConfigEntry:
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


async def _async_handle_add_bill(hass: HomeAssistant, call: ServiceCall) -> ServiceResponse:
    """Add a bill and return the stored bill."""
    entry = _async_get_loaded_entry(hass, call.data[ATTR_CONFIG_ENTRY_ID])
    store = entry.runtime_data.bill_storage

    bill_id = call.data.get(ATTR_BILL_ID) or uuid4().hex
    bill = Bill(
        id=bill_id,
        utility_type=call.data[ATTR_UTILITY_TYPE],
        months=call.data[ATTR_MONTHS],
        total_cost=call.data[ATTR_TOTAL_COST],
        consumption=call.data[ATTR_CONSUMPTION],
    )

    stored = await store.add_bill(bill)
    await entry.runtime_data.coordinator.async_refresh_bills()
    return {"bill": stored.as_storage_dict()}


async def _async_handle_update_bill(hass: HomeAssistant, call: ServiceCall) -> ServiceResponse:
    """Update an existing bill and return the stored bill."""
    entry = _async_get_loaded_entry(hass, call.data[ATTR_CONFIG_ENTRY_ID])
    store = entry.runtime_data.bill_storage
    bill_id: str = call.data[ATTR_BILL_ID]

    changes: dict[str, object] = {}
    for attr in (ATTR_UTILITY_TYPE, ATTR_MONTHS, ATTR_TOTAL_COST, ATTR_CONSUMPTION):
        if attr in call.data:
            changes[attr] = call.data[attr]

    try:
        updated = await store.update_bill(bill_id, changes)
    except KeyError as err:
        raise ServiceValidationError(
            translation_domain=DOMAIN,
            translation_key="bill_not_found",
            translation_placeholders={"bill_id": bill_id},
        ) from err

    await entry.runtime_data.coordinator.async_refresh_bills()
    return {"bill": updated.as_storage_dict()}


async def _async_handle_delete_bill(hass: HomeAssistant, call: ServiceCall) -> ServiceResponse:
    """Delete an existing bill."""
    entry = _async_get_loaded_entry(hass, call.data[ATTR_CONFIG_ENTRY_ID])
    store = entry.runtime_data.bill_storage
    bill_id: str = call.data[ATTR_BILL_ID]

    deleted = await store.delete_bill(bill_id)
    if not deleted:
        raise ServiceValidationError(
            translation_domain=DOMAIN,
            translation_key="bill_not_found",
            translation_placeholders={"bill_id": bill_id},
        )

    await entry.runtime_data.coordinator.async_refresh_bills()
    return {"bill_id": bill_id}


async def _async_handle_list_bills(hass: HomeAssistant, call: ServiceCall) -> ServiceResponse:
    """Return every stored bill."""
    entry = _async_get_loaded_entry(hass, call.data[ATTR_CONFIG_ENTRY_ID])
    store = entry.runtime_data.bill_storage
    return {"bills": [bill.as_storage_dict() for bill in store.list_bills()]}
