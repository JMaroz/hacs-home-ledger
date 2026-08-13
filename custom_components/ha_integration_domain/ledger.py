"""Persistent bill ledger for the integration."""

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any
from uuid import uuid4

from homeassistant.core import HomeAssistant

from .calculations import cost_per_unit, monthly_average, total_consumption, total_cost, total_months

Bill = dict[str, str | int | float]


@dataclass
class HomeLedger:
    """Store utility bills and calculated totals."""

    hass: HomeAssistant
    entry_id: str
    bills: list[Bill] = field(default_factory=list)

    @property
    def path(self) -> Path:
        """Return the storage path for this entry."""
        return Path(self.hass.config.path(f".storage/{self.entry_id}_home_ledger.json"))

    async def async_load(self) -> None:
        """Load bills from disk."""

        def load() -> list[Bill]:
            if not self.path.exists():
                return []
            return json.loads(self.path.read_text(encoding="utf-8"))["bills"]

        self.bills = await self.hass.async_add_executor_job(load)

    async def async_save(self) -> None:
        """Persist bills to disk."""

        def save() -> None:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps({"bills": self.bills}, indent=2), encoding="utf-8")

        await self.hass.async_add_executor_job(save)

    async def async_add_bill(self, utility: str, cost: float, consumption: float, months: int) -> str:
        """Add a bill and return its identifier."""
        bill_id = uuid4().hex
        self.bills.append(
            {"id": bill_id, "utility": utility, "cost": cost, "consumption": consumption, "months": months}
        )
        await self.async_save()
        return bill_id

    async def async_update_bill(self, bill_id: str, updates: dict[str, Any]) -> None:
        """Update a bill by identifier."""
        for bill in self.bills:
            if bill["id"] == bill_id:
                bill.update({key: value for key, value in updates.items() if value is not None})
                await self.async_save()
                return
        raise KeyError(bill_id)

    async def async_delete_bill(self, bill_id: str) -> None:
        """Delete a bill by identifier."""
        self.bills = [bill for bill in self.bills if bill["id"] != bill_id]
        await self.async_save()

    def data(self) -> dict[str, Any]:
        """Return coordinator data for sensors."""
        return {
            "model": "Home Ledger",
            "serial_number": self.entry_id,
            "sw_version": "0.0.0",
            "bills": list(self.bills),
            "total_cost": float(total_cost(self.bills)),
            "total_consumption": float(total_consumption(self.bills)),
            "total_months": total_months(self.bills),
            "monthly_average": float(monthly_average(self.bills)),
            "cost_per_unit": float(cost_per_unit(self.bills)),
        }
