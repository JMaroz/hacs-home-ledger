"""Config flow for home_ledger."""

from typing import Any

import voluptuous as vol

from custom_components.home_ledger.config_flow_handler.options_flow import HomeLedgerOptionsFlowHandler
from custom_components.home_ledger.const import DOMAIN
from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback

_ENTRY_TITLE = "Home Ledger"
_INSTALLATION_UNIQUE_ID = "home_ledger"


class HomeLedgerConfigFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the config flow for home_ledger."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Return the options flow handler."""
        return HomeLedgerOptionsFlowHandler()

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle a flow started by the user."""
        if self._async_current_entries():
            return self.async_abort(reason="already_configured")

        await self.async_set_unique_id(_INSTALLATION_UNIQUE_ID)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            return self.async_create_entry(
                title=_ENTRY_TITLE,
                data={},
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),
        )
