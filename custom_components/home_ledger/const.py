"""Constants for home_ledger."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "home_ledger"

# PV ROI Constants
CONF_PV_INVESTMENT = "pv_investment"
CONF_PV_INCENTIVES = "pv_incentives"
CONF_PV_INCENTIVES_TYPE = "pv_incentives_type"
CONF_PV_INCENTIVES_YEARS = "pv_incentives_years"
CONF_PV_INSTALLATION_DATE = "pv_installation_date"
CONF_SENSOR_PV_PRODUCTION = "sensor_pv_production"
CONF_SENSOR_HOUSE_CONSUMPTION = "sensor_house_consumption"
CONF_SENSOR_BATTERY_ENERGY = "sensor_battery_energy"
CONF_SENSOR_GRID_EXPORT = "sensor_grid_export"

# Incentive types
INCENTIVES_TYPE_LUMP_SUM = "lump_sum"
INCENTIVES_TYPE_DISTRIBUTED = "distributed"
