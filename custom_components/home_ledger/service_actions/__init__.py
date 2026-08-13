"""Service action registration for home_ledger."""

from typing import TYPE_CHECKING

import voluptuous as vol

from custom_components.home_ledger.const import DOMAIN
from homeassistant.config_entries import ConfigEntryState
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv

from .ledger import (
    ATTR_AMOUNT,
    ATTR_BILL_ID,
    ATTR_NAME,
    ATTR_PAID,
    async_handle_add_bill,
    async_handle_delete_bill,
    async_handle_update_bill,
)

if TYPE_CHECKING:
    from custom_components.home_ledger.data import HomeLedgerConfigEntry
    from homeassistant.core import HomeAssistant, ServiceCall

ATTR_CONFIG_ENTRY_ID = "config_entry_id"
SERVICE_ADD_BILL = "add_bill"
SERVICE_DELETE_BILL = "delete_bill"
SERVICE_UPDATE_BILL = "update_bill"

_BASE_SCHEMA = {
    vol.Required(ATTR_CONFIG_ENTRY_ID): cv.string,
    vol.Required(ATTR_BILL_ID): cv.string,
}

ADD_BILL_SCHEMA = vol.Schema(
    {
        **_BASE_SCHEMA,
        vol.Required(ATTR_NAME): cv.string,
        vol.Required(ATTR_AMOUNT): vol.Coerce(float),
        vol.Optional(ATTR_PAID, default=False): cv.boolean,
    },
)
UPDATE_BILL_SCHEMA = vol.Schema(
    {
        **_BASE_SCHEMA,
        vol.Optional(ATTR_NAME): cv.string,
        vol.Optional(ATTR_AMOUNT): vol.Coerce(float),
        vol.Optional(ATTR_PAID): cv.boolean,
    },
)
DELETE_BILL_SCHEMA = vol.Schema(_BASE_SCHEMA)


async def async_setup_services(hass: HomeAssistant) -> None:
    """Register the integration's service actions once, at component level."""

    async def handle_add_bill(call: ServiceCall) -> None:
        await async_handle_add_bill(_async_get_loaded_entry(hass, call.data[ATTR_CONFIG_ENTRY_ID]), call)

    async def handle_update_bill(call: ServiceCall) -> None:
        await async_handle_update_bill(_async_get_loaded_entry(hass, call.data[ATTR_CONFIG_ENTRY_ID]), call)

    async def handle_delete_bill(call: ServiceCall) -> None:
        await async_handle_delete_bill(_async_get_loaded_entry(hass, call.data[ATTR_CONFIG_ENTRY_ID]), call)

    services = (
        (SERVICE_ADD_BILL, handle_add_bill, ADD_BILL_SCHEMA),
        (SERVICE_UPDATE_BILL, handle_update_bill, UPDATE_BILL_SCHEMA),
        (SERVICE_DELETE_BILL, handle_delete_bill, DELETE_BILL_SCHEMA),
    )
    for service, handler, schema in services:
        if not hass.services.has_service(DOMAIN, service):
            hass.services.async_register(DOMAIN, service, handler, schema=schema)


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
