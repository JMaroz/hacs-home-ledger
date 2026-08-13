"""Tests for the sensor entities the integration exposes."""

from unittest.mock import AsyncMock

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.home_ledger.api import HomeLedgerApiClientError
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant


async def test_sensors_read_the_coordinator_payload(
    init_integration: MockConfigEntry,
    hass: HomeAssistant,
) -> None:
    """Every sensor takes its state from the payload the client built."""
    assert hass.states.get("sensor.demo_air_quality_index").state == "60"
    assert hass.states.get("sensor.demo_pm2_5").state == "22.2"


async def test_sensors_go_unavailable_when_the_poll_fails(
    init_integration: MockConfigEntry,
    hass: HomeAssistant,
    mock_api: AsyncMock,
) -> None:
    """A failed refresh makes the sensors unavailable rather than stale."""
    mock_api.side_effect = HomeLedgerApiClientError("boom")

    await init_integration.runtime_data.coordinator.async_refresh()
    await hass.async_block_till_done()

    assert hass.states.get("sensor.demo_air_quality_index").state == STATE_UNAVAILABLE
