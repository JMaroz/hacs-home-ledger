"""Data update coordinator for ha_integration_domain."""

from typing import TYPE_CHECKING, Any

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

if TYPE_CHECKING:
    from custom_components.ha_integration_domain.data import IntegrationBlueprintConfigEntry


class IntegrationBlueprintDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Publish the current ledger state to every entity."""

    config_entry: IntegrationBlueprintConfigEntry

    async def _async_update_data(self) -> dict[str, Any]:
        """Return the current ledger data."""
        return self.config_entry.runtime_data.ledger.data()
