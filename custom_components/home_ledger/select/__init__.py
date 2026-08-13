"""Select platform for home_ledger."""

from typing import TYPE_CHECKING

from .fan_speed import ENTITY_DESCRIPTIONS, HomeLedgerFanSpeedSelect

# Acts on the device: the coordinator does not limit outbound calls.
PARALLEL_UPDATES = 1

if TYPE_CHECKING:
    from custom_components.home_ledger.data import HomeLedgerConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback


async def async_setup_entry(
    hass: HomeAssistant,
    entry: HomeLedgerConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the select platform."""
    async_add_entities(
        HomeLedgerFanSpeedSelect(entry.runtime_data.coordinator, description)
        for description in ENTITY_DESCRIPTIONS
    )
