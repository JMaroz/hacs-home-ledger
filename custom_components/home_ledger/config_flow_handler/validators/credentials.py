"""Config flow validation for the local ledger."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


async def validate_credentials(hass: HomeAssistant, username: str, password: str) -> None:
    """Validate the setup input for a local Home Ledger entry."""


__all__ = ["validate_credentials"]
