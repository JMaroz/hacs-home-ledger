"""Shared fixtures for the home_ledger tests."""

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.home_ledger.const import DOMAIN
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> None:
    """Load the custom integration in every test."""


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Return a config entry for the integration."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="Home Ledger",
        data={CONF_USERNAME: "home", CONF_PASSWORD: "ledger"},
        unique_id="home-ledger",
    )
