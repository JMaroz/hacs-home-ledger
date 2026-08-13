"""Sensor platform for home_ledger."""

from typing import TYPE_CHECKING

from .entity import HomeLedgerSensor
from .utilities import ENTITY_DESCRIPTIONS as UTILITY_DESCRIPTIONS

# Read-only platform: the coordinator already serializes the fetch.
PARALLEL_UPDATES = 0

if TYPE_CHECKING:
    from custom_components.home_ledger.data import HomeLedgerConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

ENTITY_DESCRIPTIONS = (*UTILITY_DESCRIPTIONS,)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: HomeLedgerConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    async_add_entities(
        HomeLedgerSensor(entry.runtime_data.coordinator, description) for description in ENTITY_DESCRIPTIONS
    )
