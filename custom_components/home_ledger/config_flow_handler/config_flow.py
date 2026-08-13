"""Config flow for home_ledger."""

from typing import Any

from custom_components.home_ledger.const import DOMAIN
from homeassistant import config_entries

from .schemas import get_user_schema

_ENTRY_TITLE = "Home Ledger"
_INSTALLATION_UNIQUE_ID = "home_ledger"


class HomeLedgerConfigFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the config flow for home_ledger."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """
        Handle a flow started by the user.

        Returns:
            The form, the abort for an existing entry, or the created config entry.

        """
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
            data_schema=get_user_schema(),
        )


__all__ = ["HomeLedgerConfigFlowHandler"]
