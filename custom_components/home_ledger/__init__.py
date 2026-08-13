"""Custom integration to integrate home_ledger with Home Assistant."""

from typing import TYPE_CHECKING

from custom_components.home_ledger.const import DOMAIN, LOGGER
from custom_components.home_ledger.coordinator import HomeLedgerDataUpdateCoordinator
from custom_components.home_ledger.data import HomeLedgerBillStorageManager, HomeLedgerData
from custom_components.home_ledger.service_actions import async_setup_services
from homeassistant.const import Platform
import homeassistant.helpers.config_validation as cv
from homeassistant.loader import async_get_loaded_integration

if TYPE_CHECKING:
    from custom_components.home_ledger.data import HomeLedgerConfigEntry
    from homeassistant.core import HomeAssistant

PLATFORMS: list[Platform] = []

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """
    Register the service actions.

    Returns:
        True once the actions are registered.

    """
    await async_setup_services(hass)
    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: HomeLedgerConfigEntry,
) -> bool:
    """
    Set up a config entry.

    Returns:
        True once the local runtime has loaded and every platform is forwarded.

    """
    bill_storage = HomeLedgerBillStorageManager(hass, entry.entry_id)
    await bill_storage.async_load()

    coordinator = HomeLedgerDataUpdateCoordinator(
        hass=hass,
        logger=LOGGER,
        name=DOMAIN,
        config_entry=entry,
        update_interval=None,
        always_update=False,
    )

    entry.runtime_data = HomeLedgerData(
        bill_storage=bill_storage,
        integration=async_get_loaded_integration(hass, entry.domain),
        coordinator=coordinator,
    )

    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: HomeLedgerConfigEntry,
) -> bool:
    """
    Unload a config entry.

    Returns:
        True if every platform unloaded cleanly.

    """
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: HomeLedgerConfigEntry,
) -> None:
    """Reload the config entry after its data or options changed."""
    await hass.config_entries.async_reload(entry.entry_id)
