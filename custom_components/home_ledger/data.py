"""Runtime data and persisted bill storage for home_ledger."""

from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any

from custom_components.home_ledger.calculations import (
    calculate_average_monthly_consumption,
    calculate_average_monthly_cost,
    calculate_cost_per_unit,
    calculate_pv_savings,
    calculate_roi_payback,
    calculate_total_consumption,
    calculate_total_cost,
    calculate_total_days,
)
from custom_components.home_ledger.const import CONF_PV_INCENTIVES, CONF_PV_INSTALLATION_DATE, CONF_PV_INVESTMENT
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
    total_electricity_days: int
    total_gas_days: int
    total_water_days: int


@dataclass(frozen=True)
class PVROIData:
    """Calculated ROI metrics for the photovoltaic system."""

    total_savings: float
    roi_percentage: float | None
    payback_years: float | None
    break_even_date: date | None


@dataclass(frozen=True)
class ActivityData:
    """Data about the last activity recorded."""

    last_activity_title: str | None
    total_activities: int


@dataclass
class HomeLedgerData:
    """Runtime data stored on the config entry after a successful setup."""

    bill_storage: HomeLedgerStore
    coordinator: HomeLedgerDataUpdateCoordinator
    pv_roi: PVROIData | None = None
    activities: ActivityData = ActivityData(last_activity_title=None, total_activities=0)

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
            total_electricity_days=calculate_total_days(bills, UtilityType.ELECTRICITY),
            total_gas_days=calculate_total_days(bills, UtilityType.GAS),
            total_water_days=calculate_total_days(bills, UtilityType.WATER),
        )

    def calculate_pv_roi(
        self,
        options: dict[str, Any],
        pv_production: float,
        house_consumption: float,
        grid_export: float | None = None,
    ) -> PVROIData | None:
        """Calculate PV ROI metrics."""

        investment = options.get(CONF_PV_INVESTMENT)
        if investment is None:
            return None

        incentives = options.get(CONF_PV_INCENTIVES, 0.0)
        net_investment = max(0.0, investment - incentives)
        install_date = options.get(CONF_PV_INSTALLATION_DATE)

        cost_per_unit = self.coordinator.data.electricity_cost_per_unit
        if cost_per_unit is None:
            return None

        total_savings = calculate_pv_savings(
            production=pv_production,
            cost_per_unit=cost_per_unit,
            grid_export=grid_export,
        )

        # Calculate annual savings for ROI and Payback
        # We use production and installation date to estimate annual production
        if install_date is None:
            return PVROIData(
                total_savings=total_savings,
                roi_percentage=None,
                payback_years=None,
                break_even_date=None,
            )

        days_since_install = (datetime.now(UTC).date() - install_date).days
        if days_since_install <= 0:
            return PVROIData(
                total_savings=total_savings,
                roi_percentage=None,
                payback_years=None,
                break_even_date=None,
            )

        annual_production = (pv_production / days_since_install) * 365.25
        annual_savings = calculate_pv_savings(
            production=annual_production,
            cost_per_unit=cost_per_unit,
            grid_export=None,  # Simplify for annual projection
        )

        payback_years = calculate_roi_payback(net_investment, annual_savings)
        roi_percentage = (annual_savings / net_investment * 100) if net_investment > 0 else None

        break_even_date = None
        if payback_years is not None:
            # Add remaining years to installation date
            # Simplified: just add years to the install date
            try:
                break_even_date = install_date.replace(year=install_date.year + int(payback_years))
            except ValueError:
                # Handle Feb 29th
                break_even_date = install_date + timedelta(days=int(payback_years * 365.25))

        return PVROIData(
            total_savings=total_savings,
            roi_percentage=roi_percentage,
            payback_years=payback_years,
            break_even_date=break_even_date,
        )

    def update_activities(self, activities_path: str) -> None:
        """Scan the activities directory and update aggregate data."""
        path = Path(activities_path)

        try:
            if not path.exists():
                self.activities = ActivityData(last_activity_title=None, total_activities=0)
                return

            files = sorted([f for f in path.iterdir() if f.suffix == ".md"])
            if not files:
                self.activities = ActivityData(last_activity_title=None, total_activities=0)
                return

            # Last activity is the one with the latest filename (YYYY-MM-DD_...)
            latest_file = files[-1]
            with latest_file.open("r", encoding="utf-8") as f:
                first_line = f.readline().strip()
                title = first_line.lstrip("# ").strip() if first_line else "Unknown"

            self.activities = ActivityData(
                last_activity_title=title,
                total_activities=len(files),
            )
        except OSError:
            self.activities = ActivityData(last_activity_title=None, total_activities=0)
