"""Options flow for home_ledger."""

from typing import Any
from uuid import uuid4

import voluptuous as vol

from custom_components.home_ledger.const import (
    CONF_PV_INCENTIVES,
    CONF_PV_INCENTIVES_TYPE,
    CONF_PV_INCENTIVES_YEARS,
    CONF_PV_INSTALLATION_DATE,
    CONF_PV_INVESTMENT,
    CONF_SENSOR_BATTERY_ENERGY,
    CONF_SENSOR_GRID_EXPORT,
    CONF_SENSOR_HOUSE_CONSUMPTION,
    CONF_SENSOR_PV_PRODUCTION,
    INCENTIVES_TYPE_DISTRIBUTED,
    INCENTIVES_TYPE_LUMP_SUM,
)
from custom_components.home_ledger.models import Bill, UtilityType
from custom_components.home_ledger.service_actions import (
    ATTR_CONSUMPTION,
    ATTR_END_DATE,
    ATTR_START_DATE,
    ATTR_TOTAL_COST,
    ATTR_UTILITY_TYPE,
)
from homeassistant import config_entries
from homeassistant.helpers import selector

UTILITY_TYPE_VALUES = [ut.value for ut in UtilityType]

STEP_ADD_BILL_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_UTILITY_TYPE): selector.SelectSelector(
            selector.SelectSelectorConfig(options=UTILITY_TYPE_VALUES),
        ),
        vol.Required(ATTR_START_DATE): selector.DateSelector(),
        vol.Required(ATTR_END_DATE): selector.DateSelector(),
        vol.Required(ATTR_TOTAL_COST): selector.NumberSelector(
            selector.NumberSelectorConfig(min=0, step=0.01, mode=selector.NumberSelectorMode.BOX),
        ),
        vol.Required(ATTR_CONSUMPTION): selector.NumberSelector(
            selector.NumberSelectorConfig(min=0, step=0.01, mode=selector.NumberSelectorMode.BOX),
        ),
        vol.Optional("bill_id"): selector.TextSelector(),
    },
)

STEP_PV_ROI_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PV_INVESTMENT): selector.NumberSelector(
            selector.NumberSelectorConfig(min=0, mode=selector.NumberSelectorMode.BOX),
        ),
        vol.Optional(CONF_PV_INCENTIVES, default=0.0): selector.NumberSelector(
            selector.NumberSelectorConfig(min=0, mode=selector.NumberSelectorMode.BOX),
        ),
        vol.Required(CONF_PV_INCENTIVES_TYPE): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=[
                    {"label": "Unica soluzione (Conto Termico)", "value": INCENTIVES_TYPE_LUMP_SUM},
                    {"label": "Distribuito negli anni (Detrazioni fiscali)", "value": INCENTIVES_TYPE_DISTRIBUTED},
                ],
                mode=selector.SelectSelectorMode.DROPDOWN,
            ),
        ),
        vol.Optional(CONF_PV_INCENTIVES_YEARS, default=10): selector.NumberSelector(
            selector.NumberSelectorConfig(min=1, max=30, step=1, mode=selector.NumberSelectorMode.BOX),
        ),
        vol.Required(CONF_PV_INSTALLATION_DATE): selector.DateSelector(),
        vol.Required(CONF_SENSOR_PV_PRODUCTION): selector.EntitySelector(
            selector.EntitySelectorConfig(domain="sensor"),
        ),
        vol.Required(CONF_SENSOR_HOUSE_CONSUMPTION): selector.EntitySelector(
            selector.EntitySelectorConfig(domain="sensor"),
        ),
        vol.Optional(CONF_SENSOR_BATTERY_ENERGY): selector.EntitySelector(
            selector.EntitySelectorConfig(domain="sensor"),
        ),
        vol.Optional(CONF_SENSOR_GRID_EXPORT): selector.EntitySelector(
            selector.EntitySelectorConfig(domain="sensor"),
        ),
    },
)


class HomeLedgerOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Home Ledger."""

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Show the main options menu."""
        return self.async_show_menu(
            step_id="init",
            menu_options=["add_bill", "pv_roi"],
            sort=True,
        )

    async def async_step_add_bill(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle adding a new bill."""
        if user_input is not None:
            store = self.config_entry.runtime_data.bill_storage
            bill_id = user_input.get("bill_id") or uuid4().hex
            try:
                bill = Bill(
                    id=bill_id,
                    utility_type=user_input[ATTR_UTILITY_TYPE],
                    start_date=user_input[ATTR_START_DATE],
                    end_date=user_input[ATTR_END_DATE],
                    total_cost=user_input[ATTR_TOTAL_COST],
                    consumption=user_input[ATTR_CONSUMPTION],
                )
                await store.add_bill(bill)
            except ValueError:
                return self.async_show_form(
                    step_id="add_bill",
                    data_schema=STEP_ADD_BILL_SCHEMA,
                    errors={"base": "invalid_dates"},
                )
            await self.config_entry.runtime_data.coordinator.async_refresh_bills()
            return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="add_bill",
            data_schema=STEP_ADD_BILL_SCHEMA,
        )

    async def async_step_pv_roi(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle PV ROI configuration."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="pv_roi",
            data_schema=STEP_PV_ROI_SCHEMA,
        )
