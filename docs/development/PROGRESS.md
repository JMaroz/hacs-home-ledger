# Development Progress

This document tracks what has been completed and what remains for Home Ledger.

> Last updated: 2026-08-27

---

## Completed

### Consolidation (commit `c612a7a`)

- [x] Consolidated 15 parallel Codex branches into a single coherent codebase
- [x] Removed AirQuant entities (binary_sensor, fan, button, switch, select, number)
- [x] Removed API client, diagnostics, repairs, credential schemas
- [x] Updated manifest.json: `integration_type: "service"`, `iot_class: "calculated"`
- [x] Updated services.yaml, translations/en.json, icons.json
- [x] Updated README.md with actual entity names and service actions

### Core Modules

- [x] `models.py` — `Bill` frozen dataclass, `UtilityType` enum, validation, serialization
- [x] `calculations.py` — pure functions for total cost, consumption, months, averages, cost-per-unit
- [x] `storage.py` — `HomeLedgerStore` wrapping HA `Store`, CRUD, listener pattern
- [x] `data.py` — `HomeLedgerAggregates`, `HomeLedgerData` with `calculate_aggregates()`
- [x] `coordinator/base.py` — local coordinator (`update_interval=None`, manual push)

### Entities

- [x] 16 sensor entities across 4 categories:
  - Total cost: electricity, gas, water, combined
  - Total consumption: electricity, gas, water
  - Average monthly cost: electricity, gas, water
  - Average monthly consumption: electricity, gas, water
  - Cost per unit: electricity, gas, water
- [x] `sensor/entity.py` — `HomeLedgerSensorEntity` with `value_fn` dispatch
- [x] `sensor/utilities.py` — declarative sensor descriptions

### Service Actions

- [x] `add_bill` — create bill, auto-generate or custom ID
- [x] `update_bill` — partial update of any field
- [x] `delete_bill` — remove by ID
- [x] `list_bills` — return all stored bills
- [x] Registered in `async_setup()` (quality scale rule `action-setup`)

### Config Flow & Options Flow

- [x] Single config entry, no credentials required
- [x] `config_flow_handler/config_flow.py` — minimal user step + options flow wiring
- [x] `config_flow_handler/options_flow.py` — add bills via Settings UI (5 fields)
- [x] Options flow translations in `en.json`

### User-Facing Documentation

- [x] `docs/user/GETTING_STARTED.md` — installation, setup, first bill, first dashboard card
- [x] `docs/user/CONFIGURATION.md` — service actions, entity categories, config entry ID
- [x] `docs/user/EXAMPLES.md` — automations and dashboard card examples
- [x] `docs/development/ARCHITECTURE.md` — directory structure, data flow, extension points

### Quality

- [x] Ruff linting: 0 errors
- [x] Pyright type checking: 0 errors
- [x] 51 tests passing:
  - `test_models.py` — 14 tests
  - `test_calculations.py` — 22 tests
  - `test_config_flow.py` — 4 tests (config + options flow)
  - `test_init.py` — 5 tests
  - `test_service_actions.py` — 6 tests

### Live Validation

- [x] Integration loaded on live HA instance
- [x] 16 sensors registered and state values correct
- [x] Bill persisted to `config/.storage/home_ledger.bills`
- [x] Coordinator refreshes correctly after service action calls

---

## Pending

### Features

- [ ] Diagnostics (`diagnostics.py`) — redacted bill dump for troubleshooting
- [ ] Multi-config-entry support — scoped storage key per entry
- [ ] Config entry migration (`async_migrate_entry`) — for future schema changes
- [ ] Repair issues — detect invalid bills, orphaned data, future-dated periods

### Quality & Validation

- [ ] HACS submission validation — verify manifest.json, hacs.json compliance
- [ ] `script/hassfest` — validate translations, services.yaml, manifest
- [ ] Snapshot tests for sensor state values

### Nice-to-Have

- [ ] CSV/JSON import for bulk bill entry
- [ ] Recurring bill auto-generation (monthly template)
- [ ] Dashboard card templates
- [ ] Multi-language translations (currently en.json only)
