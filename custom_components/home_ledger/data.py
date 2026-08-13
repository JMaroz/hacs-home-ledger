"""
Runtime data types for home_ledger.

Access pattern: entry.runtime_data.client / entry.runtime_data.coordinator
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import HomeLedgerApiClient
    from .coordinator import HomeLedgerDataUpdateCoordinator


type HomeLedgerConfigEntry = ConfigEntry[HomeLedgerData]


@dataclass
class HomeLedgerData:
    """Runtime data stored on the config entry after a successful setup."""

    client: HomeLedgerApiClient
    coordinator: HomeLedgerDataUpdateCoordinator
    integration: Integration
