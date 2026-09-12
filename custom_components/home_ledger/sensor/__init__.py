"""Sensor platform for home_ledger."""

from typing import TYPE_CHECKING

from custom_components.home_ledger.sensor.activities import ENTITY_DESCRIPTIONS as ACTIVITY_DESCRIPTIONS, ActivitySensor
from custom_components.home_ledger.sensor.entity import HomeLedgerSensor
from custom_components.home_ledger.sensor.pv_roi import ENTITY_DESCRIPTIONS as PV_ROI_DESCRIPTIONS, PVROISensor
from custom_components.home_ledger.sensor.utilities import ENTITY_DESCRIPTIONS as UTILITY_DESCRIPTIONS

if TYPE_CHECKING:
    from custom_components.home_ledger.data import HomeLedgerConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: HomeLedgerConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    # Utility sensors
    async_add_entities(
        HomeLedgerSensor(entry.runtime_data.coordinator, description) for description in UTILITY_DESCRIPTIONS
    )

    # PV ROI sensors
    async_add_entities(PVROISensor(entry.runtime_data.coordinator, description) for description in PV_ROI_DESCRIPTIONS)

    # Activity sensors
    async_add_entities(
        ActivitySensor(entry.runtime_data.coordinator, description) for description in ACTIVITY_DESCRIPTIONS
    )
