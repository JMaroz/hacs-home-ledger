"""Tests for the Home Ledger config flow."""

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.home_ledger.const import DOMAIN
from homeassistant.config_entries import SOURCE_USER
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType


async def test_user_flow_creates_single_home_ledger_entry(hass: HomeAssistant) -> None:
    """The user flow creates the single Home Ledger entry without credentials."""
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_USER})

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(result["flow_id"], {})

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Home Ledger"
    assert result["data"] == {}
    assert result["result"].unique_id == "home_ledger"


async def test_user_flow_aborts_when_entry_exists(hass: HomeAssistant) -> None:
    """The user flow aborts when Home Ledger is already configured."""
    MockConfigEntry(domain=DOMAIN, title="Home Ledger", unique_id="home_ledger", data={}).add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_USER})

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
