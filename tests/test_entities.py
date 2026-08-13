"""Tests for Home Ledger entities and actions."""

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.home_ledger.const import DOMAIN
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError


async def test_entities_read_the_coordinator_payload(
    init_integration: MockConfigEntry,
    hass: HomeAssistant,
) -> None:
    """Every entity takes its state from the coordinator aggregate payload."""
    assert hass.states.get("sensor.demo_bills").state == "0"
    assert hass.states.get("sensor.demo_unpaid_bills").state == "0"
    assert hass.states.get("sensor.demo_unpaid_total").state == "0"
    assert hass.states.get("sensor.demo_paid_total").state == "0"


async def test_bill_actions_save_and_publish_updated_data(
    init_integration: MockConfigEntry,
    hass: HomeAssistant,
) -> None:
    """Bill actions persist data and publish the updated aggregate immediately."""
    entry_id = init_integration.entry_id

    await hass.services.async_call(
        DOMAIN,
        "add_bill",
        {
            "config_entry_id": entry_id,
            "bill_id": "electricity_2026_08",
            "name": "Electricity August 2026",
            "amount": 125.5,
        },
        blocking=True,
    )
    await hass.async_block_till_done()

    assert hass.states.get("sensor.demo_bills").state == "1"
    assert hass.states.get("sensor.demo_unpaid_bills").state == "1"
    assert hass.states.get("sensor.demo_unpaid_total").state == "125.5"

    await hass.services.async_call(
        DOMAIN,
        "update_bill",
        {"config_entry_id": entry_id, "bill_id": "electricity_2026_08", "paid": True},
        blocking=True,
    )
    await hass.async_block_till_done()

    assert hass.states.get("sensor.demo_unpaid_total").state == "0"
    assert hass.states.get("sensor.demo_paid_total").state == "125.5"

    await hass.services.async_call(
        DOMAIN,
        "delete_bill",
        {"config_entry_id": entry_id, "bill_id": "electricity_2026_08"},
        blocking=True,
    )
    await hass.async_block_till_done()

    assert hass.states.get("sensor.demo_bills").state == "0"


async def test_update_missing_bill_raises_translated_error(
    init_integration: MockConfigEntry,
    hass: HomeAssistant,
) -> None:
    """Updating a missing bill raises a translated validation error."""
    with pytest.raises(ServiceValidationError) as err:
        await hass.services.async_call(
            DOMAIN,
            "update_bill",
            {"config_entry_id": init_integration.entry_id, "bill_id": "missing", "paid": True},
            blocking=True,
        )

    assert err.value.translation_key == "bill_not_found"
