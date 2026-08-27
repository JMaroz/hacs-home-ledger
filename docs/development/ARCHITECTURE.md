# Architecture Overview

This document describes the technical architecture of the Home Ledger custom component for Home Assistant.

## Directory Structure

```text
custom_components/home_ledger/
├── __init__.py              # Integration setup, wires store → coordinator → platforms
├── calculations.py          # Pure functions: totals, averages, cost-per-unit
├── config_flow.py           # Config flow discovery shim
├── const.py                 # DOMAIN, LOGGER
├── coordinator/
│   ├── __init__.py          # Exports HomeLedgerDataUpdateCoordinator
│   └── base.py              # Local coordinator (no polling)
├── data.py                  # HomeLedgerAggregates, HomeLedgerData, HomeLedgerConfigEntry
├── entity/
│   ├── __init__.py          # Exports HomeLedgerEntity
│   └── base.py              # Base entity with DeviceInfo
├── icons.json               # Entity and service action icons
├── manifest.json            # Integration metadata
├── models.py                # Bill dataclass, UtilityType enum, validation
├── services.yaml            # Service action definitions
├── storage.py               # HomeLedgerStore wrapping HA Store
├── config_flow_handler/
│   ├── __init__.py          # Package exports
│   ├── config_flow.py       # Config flow + options flow wiring
│   └── options_flow.py      # Add bills via Settings UI
├── sensor/
│   ├── __init__.py          # Platform setup
│   ├── entity.py            # HomeLedgerSensor entity class
│   └── utilities.py         # 16 sensor descriptions
├── service_actions/
│   └── __init__.py          # CRUD service actions, registered in async_setup()
└── translations/
    └── en.json              # English translations
```

## Core Components

### Bill Storage

**File:** `storage.py`

Wraps `homeassistant.helpers.storage.Store` to persist bills on disk. Bills are stored as a list of dicts under the key `bills`. The store provides:

- `add_bill(bill)` — append and persist
- `update_bill(bill_id, changes)` — patch fields and persist
- `delete_bill(bill_id)` — remove and persist
- `list_bills()` — return all bills as `Bill` objects
- Listener pattern — coordinator registers for change notifications

### Data Coordinator

**File:** `coordinator/base.py`

`HomeLedgerDataUpdateCoordinator` extends `DataUpdateCoordinator` with `update_interval=None`. There is nothing to poll — data changes only when the user mutates bills.

Aggregates are recalculated on demand via `async_refresh_bills()`, which calls `async_set_updated_data()` to push new values to all entities instantly.

### Aggregates

**File:** `data.py`

`HomeLedgerData.calculate_aggregates()` runs all pure calculation functions against the current bill list and returns a frozen `HomeLedgerAggregates` dataclass. This is what the coordinator hands to every entity.

### Sensor Platform

**Files:** `sensor/utilities.py`, `sensor/entity.py`

16 sensor descriptions defined declaratively as tuples. Each has a `value_fn` that reads one field from `HomeLedgerAggregates`. The entity class dispatches to `value_fn` in its `native_value` property.

Categories:
- **Total cost** — cumulative EUR per utility + combined
- **Total consumption** — cumulative kWh / m³ per utility
- **Average monthly cost** — EUR/month across all bills of that utility
- **Average monthly consumption** — unit/month across all bills
- **Cost per unit** — EUR/kWh or EUR/m³

### Service Actions

**File:** `service_actions/__init__.py`

Four service actions registered in `async_setup()` (not `async_setup_entry`):

- `add_bill` — create, returns stored bill
- `update_bill` — partial update, returns stored bill
- `delete_bill` — remove, returns bill ID
- `list_bills` — return all bills (response-only)

All use voluptuous schemas for validation and `ServiceValidationError` for user-facing errors.

### Config Flow

**File:** `config_flow_handler/config_flow.py`

Minimal single-entry flow. No credentials required. User clicks Submit and a config entry is created.

### Options Flow

**File:** `config_flow_handler/options_flow.py`

Provides an in-UI way to add bills via **Settings → Devices & services → Home Ledger → Options**. The form has five fields: utility type, months covered, total cost, consumption, and an optional bill ID. On submit, a `Bill` is created, stored, and the coordinator is refreshed.

This is an alternative to the `add_bill` service action — both write to the same store.

## Data Flow

```text
┌─────────────────┐
│  Config Entry   │ ← Created by config flow (no credentials)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  HomeLedgerStore│ ← HA Store on disk
└────────┬────────┘
         │  add / update / delete via:
         │    • service actions (automations, scripts)
         │    • options flow (Settings UI)
         ▼
┌─────────────────┐
│   Coordinator   │ ← async_refresh_bills() after each mutation
└────────┬────────┘
         │  HomeLedgerAggregates
         ▼
┌─────────────────┐
│  16 Sensors     │ ← each reads one field from aggregates
└─────────────────┘
```

## Extension Points

To add new functionality:

### Adding a New Sensor

1. Add a field to `HomeLedgerAggregates` in `data.py`
2. Add a calculation function in `calculations.py`
3. Call it from `HomeLedgerData.calculate_aggregates()`
4. Add a `HomeLedgerSensorEntityDescription` to the appropriate tuple in `sensor/utilities.py`
5. Add translation key to `translations/en.json`

### Adding a New Service Action

1. Define schema and handler in `service_actions/__init__.py`
2. Register in `async_setup_services()` (called from `async_setup()`)
3. Add service definition to `services.yaml`
4. Add translations to `translations/en.json`

### Adding a New Utility Type

1. Add value to `UtilityType` enum in `models.py`
2. Add unit mapping to `UTILITY_UNITS` in `models.py`
3. Add sensor descriptions for the new type in `sensor/utilities.py`
4. Update `services.yaml` enum values

## Testing Strategy

- **Unit tests:** Pure calculation functions (`test_calculations.py`), Bill model (`test_models.py`)
- **Integration tests:** Config flow (`test_config_flow.py`), setup and service actions (`test_init.py`, `test_service_actions.py`)
- **Fixtures:** Shared in `tests/conftest.py` — `config_entry`, `init_integration`

Tests mirror the source structure under `tests/`.

## Dependencies

- **Runtime:** Home Assistant 2026.8.0+ (from `hacs.json`)
- **No external libraries** — only HA core modules (Store, Coordinator, Entity)
- **Dev tools:** ruff (linting), pyright (type checking), pytest + pytest-homeassistant-custom-component
