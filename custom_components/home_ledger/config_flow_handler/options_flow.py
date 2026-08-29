"""Options flow for home_ledger."""

from typing import Any
from uuid import uuid4
from datetime import date

import voluptuous as vol

from custom_components.home_ledger.models import Bill, UtilityType
from custom_components.home_ledger.service_actions import (
    ATTR_CONSUMPTION,
    ATTR_START_DATE,
    ATTR_END_DATE,
    ATTR_TOTAL_COST,
    ATTR_UTILITY_TYPE,
)
from homeassistant import config_entries

UTILITY_TYPE_VALUES = [ut.value for ut in UtilityType]

STEP_ADD_BILL_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_UTILITY_TYPE): vol.In(UTILITY_TYPE_VALUES),
        vol.Required(ATTR_START_DATE): vol.All(vol.Coerce(str), lambda x: date.fromisoformat(x)),
        vol.Required(ATTR_END_DATE): vol.All(vol.Coerce(str), lambda x: date.fromisoformat(x)),
        vol.Required(ATTR_TOTAL_COST): vol.All(vol.Coerce(float), vol.Range(min=0)),
        vol.Required(ATTR_CONSUMPTION): vol.All(vol.Coerce(float), vol.Range(min=0)),
        vol.Optional("bill_id"): str,
    },
)


class HomeLedgerOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Home Ledger — add a bill."""

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Show the add-bill form."""
        if user_input is not None:
            store = self.config_entry.runtime_data.bill_storage

            bill_id = user_input.get("bill_id") or uuid4().hex

            bill = Bill(
                id=bill_id,
                utility_type=user_input[ATTR_UTILITY_TYPE],
                start_date=user_input[ATTR_START_DATE],
                end_date=user_input[ATTR_END_DATE],
                total_cost=user_input[ATTR_TOTAL_COST],
                consumption=user_input[ATTR_CONSUMPTION],
            )

            await store.add_bill(bill)
            await self.config_entry.runtime_data.coordinator.async_refresh_bills()

            return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="init",
            data_schema=STEP_ADD_BILL_SCHEMA,
        )
