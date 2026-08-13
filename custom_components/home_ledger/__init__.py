"""Custom integration to integrate Home Ledger with Home Assistant."""

from typing import TYPE_CHECKING

from homeassistant.const import Platform
import homeassistant.helpers.config_validation as cv
from homeassistant.loader import async_get_loaded_integration

from .const import DOMAIN
from .coordinator import HomeLedgerDataUpdateCoordinator
from .data import HomeLedgerData
from .service_actions import async_setup_services

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import HomeLedgerConfigEntry

PLATFORMS: list[Platform] = [Platform.SENSOR]

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
    coordinator = HomeLedgerDataUpdateCoordinator(hass, entry)

    entry.runtime_data = HomeLedgerData(
        integration=async_get_loaded_integration(hass, entry.domain),
        coordinator=coordinator,
    )

    await coordinator.async_load()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: HomeLedgerConfigEntry,
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: HomeLedgerConfigEntry,
) -> None:
    """Reload the config entry after its data or options changed."""
    await hass.config_entries.async_reload(entry.entry_id)
