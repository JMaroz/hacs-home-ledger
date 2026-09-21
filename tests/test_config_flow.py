"""Tests for the Home Ledger config flow."""

from datetime import date

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


async def test_options_flow_add_bill(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
) -> None:
    """Test adding a bill via the options flow."""
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(config_entry.entry_id)
    assert result["type"] == FlowResultType.MENU
    assert result["step_id"] == "init"
    assert result["menu_options"] == ["add_bill", "pv_roi"]

    result2 = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {"next_step_id": "add_bill"},
    )
    assert result2["type"] == FlowResultType.FORM
    assert result2["step_id"] == "add_bill"

    result3 = await hass.config_entries.options.async_configure(
        result2["flow_id"],
        {
            "utility_type": "electricity",
            "start_date": "2026-01-01",
            "end_date": "2026-01-31",
            "total_cost": 143.52,
            "consumption": 412.0,
        },
    )
    assert result3["type"] == FlowResultType.CREATE_ENTRY

    # Verify bill was stored
    store = config_entry.runtime_data.bill_storage
    bills = store.list_bills()
    assert len(bills) == 1
    assert bills[0].utility_type == "electricity"
    assert bills[0].start_date == date(2026, 1, 1)
    assert bills[0].end_date == date(2026, 1, 31)
    assert bills[0].total_cost == 143.52
    assert bills[0].consumption == 412.0


async def test_options_flow_add_bill_with_custom_id(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
) -> None:
    """Test adding a bill with a custom ID via the options flow."""
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(config_entry.entry_id)
    assert result["type"] == FlowResultType.MENU

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {"next_step_id": "add_bill"},
    )
    assert result["type"] == FlowResultType.FORM

    result2 = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            "utility_type": "gas",
            "start_date": "2026-01-01",
            "end_date": "2026-01-31",
            "total_cost": 85.0,
            "consumption": 120.0,
            "bill_id": "gas_january",
        },
    )
    assert result2["type"] == FlowResultType.CREATE_ENTRY

    # Verify bill was stored with custom ID
    store = config_entry.runtime_data.bill_storage
    bills = store.list_bills()
    assert len(bills) == 1
    assert bills[0].id == "gas_january"
    assert bills[0].utility_type == "gas"


async def test_options_flow_pv_roi_persists_options(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
) -> None:
    """Test that PV ROI settings are saved as config entry options."""
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(config_entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {"next_step_id": "pv_roi"},
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "pv_roi"

    user_input = {
        "pv_investment": 10000.0,
        "pv_incentives": 1000.0,
        "pv_incentives_type": "lump_sum",
        "pv_incentives_years": 10,
        "pv_installation_date": "2024-01-01",
        "sensor_pv_production": "sensor.pv_production",
        "sensor_house_consumption": "sensor.house_consumption",
    }
    result = await hass.config_entries.options.async_configure(result["flow_id"], user_input)
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["data"] == user_input
