"""Local data coordinator for home_ledger."""

from typing import TYPE_CHECKING

from custom_components.home_ledger.data import HomeLedgerAggregates
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

if TYPE_CHECKING:
    from custom_components.home_ledger.data import HomeLedgerConfigEntry


class HomeLedgerDataUpdateCoordinator(DataUpdateCoordinator[HomeLedgerAggregates]):
    """Calculate bill aggregates and notify listeners when they change."""

    config_entry: HomeLedgerConfigEntry

    async def _async_update_data(self) -> HomeLedgerAggregates:
        """Return aggregates calculated from persisted bills."""
        return self.config_entry.runtime_data.calculate_aggregates()

    async def async_refresh_bills(self) -> HomeLedgerAggregates:
        """Recalculate aggregates after bill changes and notify listeners."""
        aggregates = self.config_entry.runtime_data.calculate_aggregates()
        self.async_set_updated_data(aggregates)
        return aggregates
