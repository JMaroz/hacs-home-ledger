"""Service action registration for ha_integration_domain."""

from typing import TYPE_CHECKING

import voluptuous as vol

from custom_components.ha_integration_domain.const import DOMAIN
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import ServiceResponse, SupportsResponse
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv

from .ledger import (
    ATTR_BILL_ID,
    ATTR_CONFIG_ENTRY_ID,
    ATTR_CONSUMPTION,
    ATTR_COST,
    ATTR_MONTHS,
    ATTR_UTILITY,
    async_handle_add_bill,
    async_handle_delete_bill,
    async_handle_update_bill,
)

if TYPE_CHECKING:
    from custom_components.ha_integration_domain.data import IntegrationBlueprintConfigEntry
    from homeassistant.core import HomeAssistant, ServiceCall

SERVICE_ADD_BILL = "add_bill"
SERVICE_DELETE_BILL = "delete_bill"
SERVICE_UPDATE_BILL = "update_bill"
UTILITY_VALUES = ["electricity", "gas", "water"]

ENTRY_SCHEMA = {vol.Required(ATTR_CONFIG_ENTRY_ID): cv.string}
BILL_FIELDS = {
    vol.Required(ATTR_UTILITY): vol.In(UTILITY_VALUES),
    vol.Required(ATTR_COST): vol.Coerce(float),
    vol.Required(ATTR_CONSUMPTION): vol.Coerce(float),
    vol.Required(ATTR_MONTHS): vol.All(vol.Coerce(int), vol.Range(min=1)),
}
ADD_BILL_SCHEMA = vol.Schema({**ENTRY_SCHEMA, **BILL_FIELDS})
DELETE_BILL_SCHEMA = vol.Schema({**ENTRY_SCHEMA, vol.Required(ATTR_BILL_ID): cv.string})
UPDATE_BILL_SCHEMA = vol.Schema(
    {
        **ENTRY_SCHEMA,
        vol.Required(ATTR_BILL_ID): cv.string,
        vol.Optional(ATTR_UTILITY): vol.In(UTILITY_VALUES),
        vol.Optional(ATTR_COST): vol.Coerce(float),
        vol.Optional(ATTR_CONSUMPTION): vol.Coerce(float),
        vol.Optional(ATTR_MONTHS): vol.All(vol.Coerce(int), vol.Range(min=1)),
    }
)


def _get_loaded_entry(hass: HomeAssistant, target: str) -> IntegrationBlueprintConfigEntry:
    """Return a loaded config entry for a service call."""
    entry = hass.config_entries.async_get_entry(target)
    if entry is None or entry.domain != DOMAIN:
        raise ServiceValidationError(translation_domain=DOMAIN, translation_key="entry_not_found")
    if entry.state is not ConfigEntryState.LOADED:
        raise ServiceValidationError(translation_domain=DOMAIN, translation_key="entry_not_loaded")
    return entry


async def async_setup_services(hass: HomeAssistant) -> None:
    """Register the integration's service actions once, at component level."""

    async def handle_add_bill(call: ServiceCall) -> ServiceResponse:
        entry = _get_loaded_entry(hass, call.data[ATTR_CONFIG_ENTRY_ID])
        return await async_handle_add_bill(entry, call)

    async def handle_update_bill(call: ServiceCall) -> None:
        entry = _get_loaded_entry(hass, call.data[ATTR_CONFIG_ENTRY_ID])
        await async_handle_update_bill(entry, call)

    async def handle_delete_bill(call: ServiceCall) -> None:
        entry = _get_loaded_entry(hass, call.data[ATTR_CONFIG_ENTRY_ID])
        await async_handle_delete_bill(entry, call)

    if not hass.services.has_service(DOMAIN, SERVICE_ADD_BILL):
        hass.services.async_register(
            DOMAIN,
            SERVICE_ADD_BILL,
            handle_add_bill,
            schema=ADD_BILL_SCHEMA,
            supports_response=SupportsResponse.OPTIONAL,
        )
    if not hass.services.has_service(DOMAIN, SERVICE_UPDATE_BILL):
        hass.services.async_register(DOMAIN, SERVICE_UPDATE_BILL, handle_update_bill, schema=UPDATE_BILL_SCHEMA)
    if not hass.services.has_service(DOMAIN, SERVICE_DELETE_BILL):
        hass.services.async_register(DOMAIN, SERVICE_DELETE_BILL, handle_delete_bill, schema=DELETE_BILL_SCHEMA)
