"""Tests for bill ledger service actions and sensor updates."""

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ha_integration_domain.const import DOMAIN
from homeassistant.core import HomeAssistant


async def _add_bill(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    utility: str = "electricity",
    cost: float = 10,
    consumption: float = 5,
    months: int = 1,
) -> str:
    response = await hass.services.async_call(
        DOMAIN,
        "add_bill",
        {
            "config_entry_id": entry.entry_id,
            "utility": utility,
            "cost": cost,
            "consumption": consumption,
            "months": months,
        },
        blocking=True,
        return_response=True,
    )
    return response["bill_id"]


async def test_bill_creation_and_persistence(init_integration: MockConfigEntry, hass: HomeAssistant) -> None:
    """Adding a bill creates a persisted ledger record."""
    bill_id = await _add_bill(hass, init_integration, cost=42, consumption=21, months=2)

    assert init_integration.runtime_data.ledger.bills == [
        {"id": bill_id, "utility": "electricity", "cost": 42.0, "consumption": 21.0, "months": 2}
    ]
    assert init_integration.runtime_data.ledger.path.exists()


async def test_multiple_utilities_share_the_same_history(
    init_integration: MockConfigEntry, hass: HomeAssistant
) -> None:
    """Electricity, gas and water bills are held in one ledger history."""
    for utility in ("electricity", "gas", "water"):
        await _add_bill(hass, init_integration, utility=utility)

    assert [bill["utility"] for bill in init_integration.runtime_data.ledger.bills] == ["electricity", "gas", "water"]


async def test_bill_update_delete_and_sensor_refresh(init_integration: MockConfigEntry, hass: HomeAssistant) -> None:
    """Updating and deleting bills refreshes the exposed summary sensors."""
    bill_id = await _add_bill(hass, init_integration, cost=10, consumption=5, months=1)
    await hass.services.async_call(
        DOMAIN,
        "update_bill",
        {"config_entry_id": init_integration.entry_id, "bill_id": bill_id, "cost": 20, "consumption": 10, "months": 2},
        blocking=True,
    )

    assert hass.states.get("sensor.home_ledger_total_cost").state == "20.0"
    assert hass.states.get("sensor.home_ledger_total_consumption").state == "10.0"
    assert hass.states.get("sensor.home_ledger_total_months").state == "2"
    assert hass.states.get("sensor.home_ledger_monthly_average").state == "10.0"
    assert hass.states.get("sensor.home_ledger_cost_per_unit").state == "2.0"

    await hass.services.async_call(
        DOMAIN,
        "delete_bill",
        {"config_entry_id": init_integration.entry_id, "bill_id": bill_id},
        blocking=True,
    )

    assert init_integration.runtime_data.ledger.bills == []
    assert hass.states.get("sensor.home_ledger_total_cost").state == "0.0"


async def test_persistence_after_reload(init_integration: MockConfigEntry, hass: HomeAssistant) -> None:
    """Persisted bills are loaded again after a config entry reload."""
    await _add_bill(hass, init_integration, utility="water", cost=12, consumption=0, months=3)

    await hass.config_entries.async_reload(init_integration.entry_id)
    await hass.async_block_till_done()

    assert hass.states.get("sensor.home_ledger_total_cost").state == "12.0"
    assert hass.states.get("sensor.home_ledger_total_consumption").state == "0.0"
    assert hass.states.get("sensor.home_ledger_cost_per_unit").state == "0.0"
