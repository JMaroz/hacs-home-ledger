"""Coordinator for Home Ledger."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from custom_components.home_ledger.const import DOMAIN, LOGGER
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

if TYPE_CHECKING:
    from custom_components.home_ledger.data import HomeLedgerConfigEntry
    from homeassistant.core import HomeAssistant

STORAGE_KEY = f"{DOMAIN}.bills"
STORAGE_VERSION = 1


@dataclass(frozen=True, kw_only=True)
class HomeLedgerBill:
    """A bill stored by Home Ledger."""

    bill_id: str
    amount: float
    name: str
    paid: bool


@dataclass(frozen=True, kw_only=True)
class HomeLedgerData:
    """Aggregated Home Ledger state exposed to entities."""

    bill_count: int
    bills: tuple[HomeLedgerBill, ...]
    paid_count: int
    paid_total: float
    unpaid_count: int
    unpaid_total: float


class HomeLedgerDataUpdateCoordinator(DataUpdateCoordinator[HomeLedgerData]):
    """Load stored bills and publish aggregate ledger data."""

    config_entry: HomeLedgerConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        entry: HomeLedgerConfigEntry,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            config_entry=entry,
            update_interval=None,
            always_update=False,
        )
        self._store: Store[dict[str, Any]] = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self._bills: dict[str, HomeLedgerBill] = {}

    async def async_load(self) -> None:
        """Load stored bills and publish the initial aggregate data."""
        await self.async_refresh_from_store()

    async def async_refresh_from_store(self) -> None:
        """Reload bills from storage and publish aggregate data."""
        stored = await self._store.async_load()
        raw_bills = stored.get("bills", {}) if stored else {}
        self._bills = {
            bill_id: HomeLedgerBill(
                bill_id=bill_id,
                amount=float(raw_bill.get("amount", 0.0)),
                name=str(raw_bill.get("name", bill_id)),
                paid=bool(raw_bill.get("paid", False)),
            )
            for bill_id, raw_bill in raw_bills.items()
            if isinstance(raw_bill, dict)
        }
        self.async_set_updated_data(self._aggregate())

    async def async_add_bill(self, bill_id: str, name: str, amount: float, *, paid: bool = False) -> None:
        """Add a bill, persist it and publish updated aggregate data."""
        self._bills[bill_id] = HomeLedgerBill(bill_id=bill_id, name=name, amount=amount, paid=paid)
        await self._async_save_and_publish()

    async def async_update_bill(
        self,
        bill_id: str,
        name: str | None = None,
        amount: float | None = None,
        *,
        paid: bool | None = None,
    ) -> None:
        """Update a bill, persist it and publish updated aggregate data."""
        bill = self._bills[bill_id]
        self._bills[bill_id] = HomeLedgerBill(
            bill_id=bill_id,
            name=bill.name if name is None else name,
            amount=bill.amount if amount is None else amount,
            paid=bill.paid if paid is None else paid,
        )
        await self._async_save_and_publish()

    async def async_delete_bill(self, bill_id: str) -> None:
        """Delete a bill, persist it and publish updated aggregate data."""
        del self._bills[bill_id]
        await self._async_save_and_publish()

    def has_bill(self, bill_id: str) -> bool:
        """Return whether a bill exists in runtime data."""
        return bill_id in self._bills

    async def _async_save_and_publish(self) -> None:
        """Persist bills and publish aggregate data."""
        await self._store.async_save(
            {
                "bills": {
                    bill.bill_id: {
                        "amount": bill.amount,
                        "name": bill.name,
                        "paid": bill.paid,
                    }
                    for bill in self._bills.values()
                },
            },
        )
        self.async_set_updated_data(self._aggregate())

    def _aggregate(self) -> HomeLedgerData:
        """Build the aggregate state entities read."""
        bills = tuple(sorted(self._bills.values(), key=lambda bill: bill.bill_id))
        paid_bills = tuple(bill for bill in bills if bill.paid)
        unpaid_bills = tuple(bill for bill in bills if not bill.paid)
        return HomeLedgerData(
            bill_count=len(bills),
            bills=bills,
            paid_count=len(paid_bills),
            paid_total=sum(bill.amount for bill in paid_bills),
            unpaid_count=len(unpaid_bills),
            unpaid_total=sum(bill.amount for bill in unpaid_bills),
        )
