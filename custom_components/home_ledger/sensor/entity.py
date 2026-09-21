"""Sensor entity for home_ledger."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from custom_components.home_ledger.entity import HomeLedgerEntity
from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.helpers.typing import StateType


@dataclass(frozen=True, kw_only=True)
class HomeLedgerSensorEntityDescription(SensorEntityDescription):
    """Describes a sensor and how to read it from coordinator data."""

    value_fn: Callable[[Any], StateType]
    extra_attributes_fn: Callable[[Any], dict[str, Any] | None] | None = None


class HomeLedgerSensor(SensorEntity, HomeLedgerEntity):
    """Sensor backed by one value in the coordinator payload."""

    entity_description: HomeLedgerSensorEntityDescription

    @property
    def native_value(self) -> StateType:
        """Return the value read from coordinator data."""
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return extra state attributes."""
        if self.entity_description.extra_attributes_fn is None:
            return None
        return self.entity_description.extra_attributes_fn(self.coordinator.data)
