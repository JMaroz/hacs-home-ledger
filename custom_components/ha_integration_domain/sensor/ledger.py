"""Ledger summary sensors."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from custom_components.ha_integration_domain.entity import IntegrationBlueprintEntity
from homeassistant.components.sensor import SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.const import UnitOfEnergy


@dataclass(frozen=True, kw_only=True)
class LedgerSensorEntityDescription(SensorEntityDescription):
    """Describe a ledger summary sensor."""

    value_fn: Callable[[dict[str, Any]], int | float]


ENTITY_DESCRIPTIONS: tuple[LedgerSensorEntityDescription, ...] = (
    LedgerSensorEntityDescription(
        key="total_cost",
        translation_key="total_cost",
        native_unit_of_measurement="€",
        state_class=SensorStateClass.TOTAL,
        value_fn=lambda data: data["total_cost"],
    ),
    LedgerSensorEntityDescription(
        key="total_consumption",
        translation_key="total_consumption",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL,
        value_fn=lambda data: data["total_consumption"],
    ),
    LedgerSensorEntityDescription(
        key="total_months",
        translation_key="total_months",
        state_class=SensorStateClass.TOTAL,
        value_fn=lambda data: data["total_months"],
    ),
    LedgerSensorEntityDescription(
        key="monthly_average",
        translation_key="monthly_average",
        native_unit_of_measurement="€/month",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data["monthly_average"],
    ),
    LedgerSensorEntityDescription(
        key="cost_per_unit",
        translation_key="cost_per_unit",
        native_unit_of_measurement="€/kWh",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data["cost_per_unit"],
    ),
)


class HomeLedgerSensor(SensorEntity, IntegrationBlueprintEntity):
    """Sensor that exposes a ledger summary value."""

    entity_description: LedgerSensorEntityDescription

    @property
    def native_value(self) -> int | float:
        """Return the current summary value."""
        return self.entity_description.value_fn(self.coordinator.data)
