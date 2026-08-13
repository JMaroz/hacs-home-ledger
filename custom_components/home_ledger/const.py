"""Constants for home_ledger."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "home_ledger"

CONF_UPDATE_INTERVAL_HOURS = "update_interval_hours"
DEFAULT_UPDATE_INTERVAL_HOURS = 1.0
