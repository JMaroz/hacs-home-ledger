"""Runtime data and persisted bill storage for home_ledger."""

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import TYPE_CHECKING, Any

from custom_components.home_ledger.const import DOMAIN
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

if TYPE_CHECKING:
    from custom_components.home_ledger.coordinator import HomeLedgerDataUpdateCoordinator
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.loader import Integration

STORAGE_KEY = f"{DOMAIN}.bills"
STORAGE_VERSION = 1


type HomeLedgerConfigEntry = ConfigEntry[HomeLedgerData]
type HomeLedgerBill = dict[str, Any]


@dataclass(frozen=True)
class HomeLedgerAggregates:
    """Aggregated values calculated from persisted bills."""

    bill_count: int
    currency: str | None
    overdue_count: int
    paid_amount: float
    paid_count: int
    total_amount: float
    unpaid_amount: float
    unpaid_count: int
    updated_at: str


class HomeLedgerBillStorageManager:
    """Persist and summarize bills for one Home Ledger config entry."""

    def __init__(self, hass: HomeAssistant, entry_id: str) -> None:
        """Initialize the bill storage manager."""
        self._store: Store[list[HomeLedgerBill]] = Store(hass, STORAGE_VERSION, f"{STORAGE_KEY}.{entry_id}")
        self._bills: list[HomeLedgerBill] = []

    @property
    def bills(self) -> tuple[HomeLedgerBill, ...]:
        """Return the persisted bills loaded in memory."""
        return tuple(self._bills)

    async def async_load(self) -> None:
        """Load the persisted bills into memory."""
        self._bills = list(await self._store.async_load() or [])

    async def async_replace_bills(self, bills: list[HomeLedgerBill]) -> HomeLedgerAggregates:
        """Replace the persisted bills and return fresh aggregate data."""
        self._bills = list(bills)
        await self._store.async_save(self._bills)
        return self.calculate_aggregates()

    def calculate_aggregates(self) -> HomeLedgerAggregates:
        """Calculate aggregate values from the loaded bills."""
        today = dt_util.utcnow().date().isoformat()
        currencies = {str(bill["currency"]) for bill in self._bills if bill.get("currency")}
        paid_amount = Decimal(0)
        total_amount = Decimal(0)
        paid_count = 0
        overdue_count = 0

        for bill in self._bills:
            amount = _decimal_from_bill(bill)
            total_amount += amount
            if bill.get("paid") is True:
                paid_count += 1
                paid_amount += amount
            elif isinstance(bill.get("due_date"), str) and bill["due_date"] < today:
                overdue_count += 1

        unpaid_amount = total_amount - paid_amount
        unpaid_count = len(self._bills) - paid_count

        return HomeLedgerAggregates(
            bill_count=len(self._bills),
            currency=currencies.pop() if len(currencies) == 1 else None,
            overdue_count=overdue_count,
            paid_amount=float(paid_amount),
            paid_count=paid_count,
            total_amount=float(total_amount),
            unpaid_amount=float(unpaid_amount),
            unpaid_count=unpaid_count,
            updated_at=dt_util.utcnow().isoformat(),
        )


def _decimal_from_bill(bill: HomeLedgerBill) -> Decimal:
    """Return the bill amount as a Decimal."""
    try:
        return Decimal(str(bill.get("amount", "0")))
    except InvalidOperation:
        return Decimal(0)


@dataclass
class HomeLedgerData:
    """Runtime data stored on the config entry after a successful setup."""

    bill_storage: HomeLedgerBillStorageManager
    coordinator: HomeLedgerDataUpdateCoordinator
    integration: Integration

    @property
    def aggregates(self) -> HomeLedgerAggregates | None:
        """Return the latest aggregate data calculated by the coordinator."""
        return self.coordinator.data
