"""Persistent bill storage for Home Ledger."""

from collections.abc import Callable
from copy import deepcopy
from typing import Any
from uuid import uuid4

from custom_components.home_ledger.models import Bill
from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

STORAGE_KEY = "home_ledger.bills"
STORAGE_VERSION = 1


class HomeLedgerStore:
    """Manage Home Ledger bills in Home Assistant storage."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the bill store."""
        self._store: Store[dict[str, Any]] = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self._data: dict[str, Any] = {"version": STORAGE_VERSION, "bills": []}
        self._listeners: list[Callable[[], None]] = []

    async def async_load(self) -> None:
        """Load bills from Home Assistant storage."""
        stored_data = await self._store.async_load()
        if stored_data is None:
            return

        self._data = self._migrate_storage_data(stored_data)

    async def async_save(self) -> None:
        """Save bills to Home Assistant storage."""
        await self._store.async_save(deepcopy(self._data))
        self._notify_listeners()

    async def add_bill(self, bill: Bill) -> Bill:
        """Add a bill and persist the updated bill list."""
        stored_bill = bill.as_storage_dict()
        stored_bill.setdefault("id", uuid4().hex)

        self._data["bills"].append(stored_bill)
        await self.async_save()
        return Bill.from_storage_dict(stored_bill)

    async def update_bill(self, bill_id: str, changes: dict[str, Any]) -> Bill:
        """Update a bill and persist the updated bill list."""
        for index, bill in enumerate(self._data["bills"]):
            if bill.get("id") != bill_id:
                continue

            updated_bill = {**bill, **changes, "id": bill_id}
            self._data["bills"][index] = updated_bill
            await self.async_save()
            return Bill.from_storage_dict(updated_bill)

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

    def list_bills(self) -> list[Bill]:
        """Return persisted bills as Bill objects."""
        return [Bill.from_storage_dict(bill) for bill in self._data["bills"]]

    def list_bill_dicts(self) -> list[dict[str, Any]]:
        """Return persisted bills as raw dicts."""
        return deepcopy(self._data["bills"])

    def add_listener(self, listener: Callable[[], None]) -> None:
        """Register a listener for bill changes."""
        self._listeners.append(listener)

    def _notify_listeners(self) -> None:
        """Notify all registered listeners of a bill change."""
        for listener in self._listeners:
            listener()

    def _migrate_storage_data(self, stored_data: dict[str, Any]) -> dict[str, Any]:
        """Migrate stored data to the current version."""
        if stored_data.get("version") == STORAGE_VERSION:
            return deepcopy(stored_data)

        return {"version": STORAGE_VERSION, "bills": list(stored_data.get("bills", []))}
