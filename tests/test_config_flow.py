"""Tests for the Home Ledger config flow."""

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.home_ledger.const import DOMAIN
from homeassistant.config_entries import SOURCE_USER
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType


async def test_config_flow_single_entry(hass: HomeAssistant) -> None:
    """Test that only one entry can be created."""
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_USER})
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    result2 = await hass.config_entries.flow.async_configure(result["flow_id"], {})
    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["title"] == "Home Ledger"
    assert result2["data"] == {}


async def test_config_flow_already_configured(hass: HomeAssistant) -> None:
    """Test that the flow aborts if already configured."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Home Ledger",
        unique_id="home_ledger",
        data={},
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_USER})
    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "already_configured"
