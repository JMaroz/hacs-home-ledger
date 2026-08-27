"""Custom integration to integrate home_ledger with Home Assistant.

For more details about this integration, please refer to:
https://github.com/andmaroz89/hacs-home-ledger
"""

from typing import TYPE_CHECKING

from custom_components.home_ledger.const import DOMAIN, LOGGER
from custom_components.home_ledger.coordinator import HomeLedgerDataUpdateCoordinator
from custom_components.home_ledger.data import HomeLedgerData
from custom_components.home_ledger.service_actions import async_setup_services
from custom_components.home_ledger.storage import HomeLedgerStore
from homeassistant.const import Platform
import homeassistant.helpers.config_validation as cv

if TYPE_CHECKING:
    from custom_components.home_ledger.data import HomeLedgerConfigEntry
    from homeassistant.core import HomeAssistant

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Register the service actions."""
    await async_setup_services(hass)
    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: HomeLedgerConfigEntry,
) -> bool:
    """Set up a config entry."""
    store = HomeLedgerStore(hass)
    await store.async_load()

    coordinator = HomeLedgerDataUpdateCoordinator(
        hass=hass,
        logger=LOGGER,
        name=DOMAIN,
        config_entry=entry,
        update_interval=None,
        always_update=False,
    )

    entry.runtime_data = HomeLedgerData(
        bill_storage=store,
        coordinator=coordinator,
    )

    def _on_bills_changed() -> None:
        hass.async_create_task(coordinator.async_refresh_bills())

    store.add_listener(_on_bills_changed)

    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: HomeLedgerConfigEntry,
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
