"""Local data coordinator for home_ledger."""

from typing import TYPE_CHECKING

from custom_components.home_ledger.const import (
    CONF_SENSOR_GRID_EXPORT,
    CONF_SENSOR_GSE_EXPORT_TARIFF,
    CONF_SENSOR_HOUSE_CONSUMPTION,
    CONF_SENSOR_PV_PRODUCTION,
)
from custom_components.home_ledger.data import HomeLedgerAggregates
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

if TYPE_CHECKING:
    from custom_components.home_ledger.data import HomeLedgerConfigEntry


class HomeLedgerDataUpdateCoordinator(DataUpdateCoordinator[HomeLedgerAggregates]):
    """Calculate bill aggregates and notify listeners when they change."""

    config_entry: HomeLedgerConfigEntry

    async def _async_update_data(self) -> HomeLedgerAggregates:
        """Return aggregates calculated from persisted bills."""
        aggregates = self.config_entry.runtime_data.calculate_aggregates()

        # Update PV ROI data if configured
        options = self.config_entry.options

        pv_prod_entity = options.get(CONF_SENSOR_PV_PRODUCTION)
        if pv_prod_entity:
            # Read current states from HA
            pv_prod = self.hass.states.get(pv_prod_entity)
            house_cons_entity = options.get(CONF_SENSOR_HOUSE_CONSUMPTION)
            house_cons = self.hass.states.get(house_cons_entity) if house_cons_entity else None

            grid_exp_entity = options.get(CONF_SENSOR_GRID_EXPORT)
            grid_exp = self.hass.states.get(grid_exp_entity) if grid_exp_entity else None

            export_tariff_entity = options.get(CONF_SENSOR_GSE_EXPORT_TARIFF)
            export_tariff_state = self.hass.states.get(export_tariff_entity) if export_tariff_entity else None

            try:
                production = float(pv_prod.state) if pv_prod else 0.0
                consumption = float(house_cons.state) if house_cons else 0.0
                export = float(grid_exp.state) if grid_exp else None
                export_tariff_override = (
                    float(export_tariff_state.state)
                    if export_tariff_state and export_tariff_state.state not in ("unknown", "unavailable")
                    else None
                )

                self.config_entry.runtime_data.pv_roi = self.config_entry.runtime_data.calculate_pv_roi(
                    options=dict(options),
                    pv_production=production,
                    house_consumption=consumption,
                    grid_export=export,
                    export_tariff_override=export_tariff_override,
                )
            except ValueError, TypeError:
                self.config_entry.runtime_data.pv_roi = None

        # Update activity data
        self.config_entry.runtime_data.update_activities(self.hass.config.path("home_ledger/activities"))

        return aggregates

    async def async_refresh_bills(self) -> HomeLedgerAggregates:
        """Recalculate aggregates after bill changes and notify listeners."""
        aggregates = self.config_entry.runtime_data.calculate_aggregates()
        self.async_set_updated_data(aggregates)
        return aggregates
