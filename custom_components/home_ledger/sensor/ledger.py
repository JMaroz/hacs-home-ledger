"""Ledger sensor descriptions for home_ledger."""

from collections.abc import Callable
from dataclasses import dataclass

from custom_components.home_ledger.coordinator import HomeLedgerData
from custom_components.home_ledger.entity import HomeLedgerEntity
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.const import CURRENCY_DOLLAR
from homeassistant.helpers.typing import StateType


@dataclass(frozen=True, kw_only=True)
class HomeLedgerSensorEntityDescription(SensorEntityDescription):
    """Describes a sensor and how to read it from coordinator data."""

    value_fn: Callable[[HomeLedgerData], StateType]


ENTITY_DESCRIPTIONS: tuple[HomeLedgerSensorEntityDescription, ...] = (
    HomeLedgerSensorEntityDescription(
        key="bill_count",
        translation_key="bill_count",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value_fn=lambda data: data.bill_count,
    ),
    HomeLedgerSensorEntityDescription(
        key="unpaid_count",
        translation_key="unpaid_count",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value_fn=lambda data: data.unpaid_count,
    ),
    HomeLedgerSensorEntityDescription(
        key="unpaid_total",
        translation_key="unpaid_total",
        device_class=SensorDeviceClass.MONETARY,
        native_unit_of_measurement=CURRENCY_DOLLAR,
        state_class=SensorStateClass.TOTAL,
        suggested_display_precision=2,
        value_fn=lambda data: data.unpaid_total,
    ),
    HomeLedgerSensorEntityDescription(
        key="paid_total",
        translation_key="paid_total",
        device_class=SensorDeviceClass.MONETARY,
        native_unit_of_measurement=CURRENCY_DOLLAR,
        state_class=SensorStateClass.TOTAL,
        suggested_display_precision=2,
        value_fn=lambda data: data.paid_total,
    ),
)


class HomeLedgerSensor(SensorEntity, HomeLedgerEntity):
    """Sensor backed by one value in the coordinator payload."""

    entity_description: HomeLedgerSensorEntityDescription

    @property
    def native_value(self) -> StateType:
        """Return the value read from coordinator data."""
        return self.entity_description.value_fn(self.coordinator.data)
