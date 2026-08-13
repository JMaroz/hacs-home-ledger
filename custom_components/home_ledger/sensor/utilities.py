"""Utility ledger sensor descriptions for home_ledger."""

from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import CURRENCY_EURO, UnitOfEnergy, UnitOfVolume
from homeassistant.helpers.typing import StateType

from .entity import HomeLedgerSensorEntityDescription

UTILITY_TYPES = ("electricity", "gas", "water")
UTILITY_MONTH_COUNT_KEY = "utility_month_count"


def _sum_values(data: dict[str, Any], keys: tuple[str, ...]) -> StateType:
    total: float = 0
    for key in keys:
        value = data.get(key)
        if value is None:
            return None
        total += value
    return total


def _average_monthly(data: dict[str, Any], total_key: str) -> StateType:
    total = data.get(total_key)
    month_count = data.get(UTILITY_MONTH_COUNT_KEY)
    if total is None or not month_count:
        return None
    return total / month_count


def _cost_per_unit(data: dict[str, Any], utility_type: str) -> StateType:
    total_cost = data.get(f"total_{utility_type}_cost")
    total_consumption = data.get(f"total_{utility_type}_consumption")
    if total_cost is None or not total_consumption:
        return None
    return total_cost / total_consumption


COST_DESCRIPTIONS: tuple[HomeLedgerSensorEntityDescription, ...] = (
    *(
        HomeLedgerSensorEntityDescription(
            key=f"total_{utility_type}_cost",
            translation_key=f"total_{utility_type}_cost",
            device_class=SensorDeviceClass.MONETARY,
            native_unit_of_measurement=CURRENCY_EURO,
            state_class=SensorStateClass.TOTAL,
            suggested_display_precision=2,
            value_fn=lambda data, utility_type=utility_type: data.get(f"total_{utility_type}_cost"),
        )
        for utility_type in UTILITY_TYPES
    ),
    HomeLedgerSensorEntityDescription(
        key="total_utility_cost",
        translation_key="total_utility_cost",
        device_class=SensorDeviceClass.MONETARY,
        native_unit_of_measurement=CURRENCY_EURO,
        state_class=SensorStateClass.TOTAL,
        suggested_display_precision=2,
        value_fn=lambda data: _sum_values(
            data,
            ("total_electricity_cost", "total_gas_cost", "total_water_cost"),
        ),
    ),
)

CONSUMPTION_DESCRIPTIONS: tuple[HomeLedgerSensorEntityDescription, ...] = (
    HomeLedgerSensorEntityDescription(
        key="total_electricity_consumption",
        translation_key="total_electricity_consumption",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL,
        suggested_display_precision=2,
        value_fn=lambda data: data.get("total_electricity_consumption"),
    ),
    *(
        HomeLedgerSensorEntityDescription(
            key=f"total_{utility_type}_consumption",
            translation_key=f"total_{utility_type}_consumption",
            device_class=SensorDeviceClass.VOLUME,
            native_unit_of_measurement=UnitOfVolume.CUBIC_METERS,
            state_class=SensorStateClass.TOTAL,
            suggested_display_precision=2,
            value_fn=lambda data, utility_type=utility_type: data.get(f"total_{utility_type}_consumption"),
        )
        for utility_type in ("gas", "water")
    ),
)

AVERAGE_COST_DESCRIPTIONS: tuple[HomeLedgerSensorEntityDescription, ...] = tuple(
    HomeLedgerSensorEntityDescription(
        key=f"{utility_type}_average_monthly_cost",
        translation_key=f"{utility_type}_average_monthly_cost",
        device_class=SensorDeviceClass.MONETARY,
        native_unit_of_measurement=CURRENCY_EURO,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=lambda data, utility_type=utility_type: _average_monthly(data, f"total_{utility_type}_cost"),
    )
    for utility_type in UTILITY_TYPES
)

AVERAGE_CONSUMPTION_DESCRIPTIONS: tuple[HomeLedgerSensorEntityDescription, ...] = (
    HomeLedgerSensorEntityDescription(
        key="electricity_average_monthly_consumption",
        translation_key="electricity_average_monthly_consumption",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=lambda data: _average_monthly(data, "total_electricity_consumption"),
    ),
    *(
        HomeLedgerSensorEntityDescription(
            key=f"{utility_type}_average_monthly_consumption",
            translation_key=f"{utility_type}_average_monthly_consumption",
            device_class=SensorDeviceClass.VOLUME,
            native_unit_of_measurement=UnitOfVolume.CUBIC_METERS,
            state_class=SensorStateClass.MEASUREMENT,
            suggested_display_precision=2,
            value_fn=lambda data, utility_type=utility_type: _average_monthly(
                data,
                f"total_{utility_type}_consumption",
            ),
        )
        for utility_type in ("gas", "water")
    ),
)

COST_PER_UNIT_DESCRIPTIONS: tuple[HomeLedgerSensorEntityDescription, ...] = (
    HomeLedgerSensorEntityDescription(
        key="electricity_cost_per_unit",
        translation_key="electricity_cost_per_unit",
        device_class=SensorDeviceClass.MONETARY,
        native_unit_of_measurement=f"{CURRENCY_EURO}/{UnitOfEnergy.KILO_WATT_HOUR}",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=lambda data: _cost_per_unit(data, "electricity"),
    ),
    *(
        HomeLedgerSensorEntityDescription(
            key=f"{utility_type}_cost_per_unit",
            translation_key=f"{utility_type}_cost_per_unit",
            device_class=SensorDeviceClass.MONETARY,
            native_unit_of_measurement=f"{CURRENCY_EURO}/{UnitOfVolume.CUBIC_METERS}",
            state_class=SensorStateClass.MEASUREMENT,
            suggested_display_precision=2,
            value_fn=lambda data, utility_type=utility_type: _cost_per_unit(data, utility_type),
        )
        for utility_type in ("gas", "water")
    ),
)

ENTITY_DESCRIPTIONS = (
    *COST_DESCRIPTIONS,
    *CONSUMPTION_DESCRIPTIONS,
    *AVERAGE_COST_DESCRIPTIONS,
    *AVERAGE_CONSUMPTION_DESCRIPTIONS,
    *COST_PER_UNIT_DESCRIPTIONS,
)
