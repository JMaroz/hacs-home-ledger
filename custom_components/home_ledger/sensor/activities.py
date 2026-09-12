"""Activity sensors for home_ledger."""

from typing import Any

from custom_components.home_ledger.entity import HomeLedgerEntity
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.const import EntityCategory


class ActivitySensor(HomeLedgerEntity, SensorEntity):
    """Sensor that exposes activity data from the coordinator."""

    entity_description: ActivitySensorEntityDescription

    @property
    def native_value(self) -> Any:
        """Return the native value of the sensor."""
        data = self.coordinator.config_entry.runtime_data.activities
        return getattr(data, self.entity_description.key)


class ActivitySensorEntityDescription(SensorEntityDescription):
    """Description of an activity sensor."""

    def __init__(
        self,
        key: str,
        translation_key: str,
        device_class: SensorDeviceClass | None = None,
        state_class: SensorStateClass | None = None,
        native_unit_of_measurement: str | None = None,
        entity_category: EntityCategory = EntityCategory.DIAGNOSTIC,
    ):
        """Initialize an activity sensor description."""
        super().__init__(
            key=key,
            translation_key=translation_key,
            device_class=device_class,
            state_class=state_class,
            native_unit_of_measurement=native_unit_of_measurement,
            entity_category=entity_category,
        )


ENTITY_DESCRIPTIONS = (
    ActivitySensorEntityDescription(
        key="last_activity_title",
        translation_key="last_activity_title",
        state_class=None,
        native_unit_of_measurement=None,
    ),
    ActivitySensorEntityDescription(
        key="total_activities",
        translation_key="total_activities",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=None,
    ),
)
