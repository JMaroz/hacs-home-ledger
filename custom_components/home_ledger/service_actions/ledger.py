"""Handlers for Home Ledger bill service actions."""

from typing import TYPE_CHECKING

from custom_components.home_ledger.const import DOMAIN
from homeassistant.exceptions import ServiceValidationError

if TYPE_CHECKING:
    from custom_components.home_ledger.data import HomeLedgerConfigEntry
    from homeassistant.core import ServiceCall

ATTR_AMOUNT = "amount"
ATTR_BILL_ID = "bill_id"
ATTR_NAME = "name"
ATTR_PAID = "paid"


async def async_handle_add_bill(entry: HomeLedgerConfigEntry, call: ServiceCall) -> None:
    """Handle the add_bill action."""
    coordinator = entry.runtime_data.coordinator
    bill_id: str = call.data[ATTR_BILL_ID]
    if coordinator.has_bill(bill_id):
        raise ServiceValidationError(
            translation_domain=DOMAIN,
            translation_key="bill_already_exists",
            translation_placeholders={"bill_id": bill_id},
        )
    await coordinator.async_add_bill(
        bill_id=bill_id,
        name=call.data[ATTR_NAME],
        amount=call.data[ATTR_AMOUNT],
        paid=call.data[ATTR_PAID],
    )


async def async_handle_update_bill(entry: HomeLedgerConfigEntry, call: ServiceCall) -> None:
    """Handle the update_bill action."""
    coordinator = entry.runtime_data.coordinator
    bill_id: str = call.data[ATTR_BILL_ID]
    if not coordinator.has_bill(bill_id):
        raise ServiceValidationError(
            translation_domain=DOMAIN,
            translation_key="bill_not_found",
            translation_placeholders={"bill_id": bill_id},
        )
    await coordinator.async_update_bill(
        bill_id=bill_id,
        name=call.data.get(ATTR_NAME),
        amount=call.data.get(ATTR_AMOUNT),
        paid=call.data.get(ATTR_PAID),
    )


async def async_handle_delete_bill(entry: HomeLedgerConfigEntry, call: ServiceCall) -> None:
    """Handle the delete_bill action."""
    coordinator = entry.runtime_data.coordinator
    bill_id: str = call.data[ATTR_BILL_ID]
    if not coordinator.has_bill(bill_id):
        raise ServiceValidationError(
            translation_domain=DOMAIN,
            translation_key="bill_not_found",
            translation_placeholders={"bill_id": bill_id},
        )
    await coordinator.async_delete_bill(bill_id)
