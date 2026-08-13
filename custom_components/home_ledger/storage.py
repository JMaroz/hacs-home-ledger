"""Persistent bill storage for Home Ledger."""

from copy import deepcopy
from typing import Any
from uuid import uuid4

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

STORAGE_KEY = "home_ledger.bills"
STORAGE_VERSION = 1


type HomeLedgerBill = dict[str, Any]


class HomeLedgerStore:
    """Manage Home Ledger bills in Home Assistant storage."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the bill store."""
        self._store: Store[dict[str, Any]] = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self._data: dict[str, Any] = {"version": STORAGE_VERSION, "bills": []}

    async def async_load(self) -> None:
        """Load bills from Home Assistant storage."""
        stored_data = await self._store.async_load()
        if stored_data is None:
            return

        self._data = self._migrate_storage_data(stored_data)

    async def async_save(self) -> None:
        """Save bills to Home Assistant storage."""
        await self._store.async_save(deepcopy(self._data))

    async def add_bill(self, bill: HomeLedgerBill) -> HomeLedgerBill:
        """Add a bill and persist the updated bill list."""
        stored_bill = deepcopy(bill)
        stored_bill.setdefault("id", uuid4().hex)

        self._data["bills"].append(stored_bill)
        await self.async_save()
        return deepcopy(stored_bill)

    async def update_bill(self, bill_id: str, changes: HomeLedgerBill) -> HomeLedgerBill:
        """Update a bill and persist the updated bill list."""
        for index, bill in enumerate(self._data["bills"]):
            if bill.get("id") != bill_id:
                continue

            updated_bill = {**bill, **changes, "id": bill_id}
            self._data["bills"][index] = updated_bill
            await self.async_save()
            return deepcopy(updated_bill)

        raise KeyError(bill_id)

    async def delete_bill(self, bill_id: str) -> bool:
        """Delete a bill and persist the updated bill list."""
        for index, bill in enumerate(self._data["bills"]):
            if bill.get("id") != bill_id:
                continue

            del self._data["bills"][index]
            await self.async_save()
            return True

        return False

    def list_bills(self) -> list[HomeLedgerBill]:
        """Return persisted bills."""
        return deepcopy(self._data["bills"])

    def _migrate_storage_data(self, stored_data: dict[str, Any]) -> dict[str, Any]:
        if stored_data.get("version") == STORAGE_VERSION:
            return deepcopy(stored_data)

        return {"version": STORAGE_VERSION, "bills": list(stored_data.get("bills", []))}
