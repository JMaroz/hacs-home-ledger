"""Service action registration for home_ledger."""

from collections.abc import Callable, Coroutine
from typing import TYPE_CHECKING

import voluptuous as vol

from custom_components.home_ledger.const import DOMAIN
from homeassistant.core import SupportsResponse
from homeassistant.helpers import config_validation as cv

from .bills import (
    ATTR_AMOUNT,
    ATTR_BILL_ID,
    ATTR_CONFIG_ENTRY_ID,
    ATTR_DUE_DATE,
    ATTR_NAME,
    ATTR_PAID,
    ATTR_RECURRENCE,
    async_handle_add_bill,
    async_handle_delete_bill,
    async_handle_list_bills,
    async_handle_update_bill,
)
from .refresh_data import async_handle_refresh_data

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse

SERVICE_ADD_BILL = "add_bill"
SERVICE_DELETE_BILL = "delete_bill"
SERVICE_LIST_BILLS = "list_bills"
SERVICE_REFRESH_DATA = "refresh_data"
SERVICE_UPDATE_BILL = "update_bill"

POSITIVE_AMOUNT = vol.All(vol.Coerce(float), vol.Range(min=0, min_included=False))

ADD_BILL_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_CONFIG_ENTRY_ID): cv.string,
        vol.Optional(ATTR_BILL_ID): cv.string,
        vol.Required(ATTR_NAME): cv.string,
        vol.Required(ATTR_AMOUNT): POSITIVE_AMOUNT,
        vol.Required(ATTR_DUE_DATE): cv.date,
        vol.Optional(ATTR_PAID, default=False): cv.boolean,
        vol.Optional(ATTR_RECURRENCE): cv.string,
    },
)

UPDATE_BILL_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_CONFIG_ENTRY_ID): cv.string,
        vol.Required(ATTR_BILL_ID): cv.string,
        vol.Optional(ATTR_NAME): cv.string,
        vol.Optional(ATTR_AMOUNT): POSITIVE_AMOUNT,
        vol.Optional(ATTR_DUE_DATE): cv.date,
        vol.Optional(ATTR_PAID): cv.boolean,
        vol.Optional(ATTR_RECURRENCE): cv.string,
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

REFRESH_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_CONFIG_ENTRY_ID): cv.string,
    },
)


async def async_setup_services(hass: HomeAssistant) -> None:
    """Register the integration's service actions once, at component level."""

    async def handle_add_bill(call: ServiceCall) -> ServiceResponse:
        return await async_handle_add_bill(hass, call)

    async def handle_update_bill(call: ServiceCall) -> ServiceResponse:
        return await async_handle_update_bill(hass, call)

    async def handle_delete_bill(call: ServiceCall) -> ServiceResponse:
        return await async_handle_delete_bill(hass, call)

    async def handle_list_bills(call: ServiceCall) -> ServiceResponse:
        return await async_handle_list_bills(hass, call)

    async def handle_refresh_data(call: ServiceCall) -> ServiceResponse:
        return await async_handle_refresh_data(hass, call)

    _async_register_service(hass, SERVICE_ADD_BILL, handle_add_bill, ADD_BILL_SCHEMA, SupportsResponse.OPTIONAL)
    _async_register_service(
        hass, SERVICE_UPDATE_BILL, handle_update_bill, UPDATE_BILL_SCHEMA, SupportsResponse.OPTIONAL
    )
    _async_register_service(
        hass, SERVICE_DELETE_BILL, handle_delete_bill, DELETE_BILL_SCHEMA, SupportsResponse.OPTIONAL
    )
    _async_register_service(hass, SERVICE_LIST_BILLS, handle_list_bills, LIST_BILLS_SCHEMA, SupportsResponse.ONLY)
    _async_register_service(
        hass, SERVICE_REFRESH_DATA, handle_refresh_data, REFRESH_DATA_SCHEMA, SupportsResponse.OPTIONAL
    )


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
