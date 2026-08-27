"""Runtime data and persisted bill storage for home_ledger."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from custom_components.home_ledger.calculations import (
    calculate_average_monthly_consumption,
    calculate_average_monthly_cost,
    calculate_cost_per_unit,
    calculate_total_consumption,
    calculate_total_cost,
    calculate_total_months,
)
from custom_components.home_ledger.models import UtilityType

if TYPE_CHECKING:
    from custom_components.home_ledger.coordinator import HomeLedgerDataUpdateCoordinator
    from custom_components.home_ledger.storage import HomeLedgerStore
    from homeassistant.config_entries import ConfigEntry


type HomeLedgerConfigEntry = ConfigEntry[HomeLedgerData]


@dataclass(frozen=True)
class HomeLedgerAggregates:
    """Aggregated values calculated from persisted bills."""

    total_electricity_cost: float
    total_gas_cost: float
    total_water_cost: float
    total_utility_cost: float
    total_electricity_consumption: float
    total_gas_consumption: float
    total_water_consumption: float
    electricity_average_monthly_cost: float | None
    gas_average_monthly_cost: float | None
    water_average_monthly_cost: float | None
    electricity_average_monthly_consumption: float | None
    gas_average_monthly_consumption: float | None
    water_average_monthly_consumption: float | None
    electricity_cost_per_unit: float | None
    gas_cost_per_unit: float | None
    water_cost_per_unit: float | None
    total_electricity_months: int
    total_gas_months: int
    total_water_months: int


@dataclass
class HomeLedgerData:
    """Runtime data stored on the config entry after a successful setup."""

    bill_storage: HomeLedgerStore
    coordinator: HomeLedgerDataUpdateCoordinator

    def calculate_aggregates(self) -> HomeLedgerAggregates:
        """Calculate aggregate values from the loaded bills."""
        bills = self.bill_storage.list_bills()

        total_electricity_cost = calculate_total_cost(bills, UtilityType.ELECTRICITY)
        total_gas_cost = calculate_total_cost(bills, UtilityType.GAS)
        total_water_cost = calculate_total_cost(bills, UtilityType.WATER)
        total_utility_cost = total_electricity_cost + total_gas_cost + total_water_cost

        total_electricity_consumption = calculate_total_consumption(bills, UtilityType.ELECTRICITY)
        total_gas_consumption = calculate_total_consumption(bills, UtilityType.GAS)
        total_water_consumption = calculate_total_consumption(bills, UtilityType.WATER)

        return HomeLedgerAggregates(
            total_electricity_cost=total_electricity_cost,
            total_gas_cost=total_gas_cost,
            total_water_cost=total_water_cost,
            total_utility_cost=total_utility_cost,
            total_electricity_consumption=total_electricity_consumption,
            total_gas_consumption=total_gas_consumption,
            total_water_consumption=total_water_consumption,
            electricity_average_monthly_cost=calculate_average_monthly_cost(bills, UtilityType.ELECTRICITY),
            gas_average_monthly_cost=calculate_average_monthly_cost(bills, UtilityType.GAS),
            water_average_monthly_cost=calculate_average_monthly_cost(bills, UtilityType.WATER),
            electricity_average_monthly_consumption=calculate_average_monthly_consumption(
                bills, UtilityType.ELECTRICITY
            ),
            gas_average_monthly_consumption=calculate_average_monthly_consumption(bills, UtilityType.GAS),
            water_average_monthly_consumption=calculate_average_monthly_consumption(bills, UtilityType.WATER),
            electricity_cost_per_unit=calculate_cost_per_unit(bills, UtilityType.ELECTRICITY),
            gas_cost_per_unit=calculate_cost_per_unit(bills, UtilityType.GAS),
            water_cost_per_unit=calculate_cost_per_unit(bills, UtilityType.WATER),
            total_electricity_months=calculate_total_months(bills, UtilityType.ELECTRICITY),
            total_gas_months=calculate_total_months(bills, UtilityType.GAS),
            total_water_months=calculate_total_months(bills, UtilityType.WATER),
        )
