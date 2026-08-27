# Development Progress

This document tracks what has been completed and what remains for Home Ledger.

> Last updated: 2026-08-27

---

## Completed

### Consolidation (commit `c612a7a`)

- [x] Consolidated 15 parallel Codex branches into a single coherent codebase
- [x] Removed AirQuant entities (binary_sensor, fan, button, switch, select, number)
- [x] Removed API client, diagnostics, repairs, options flow, credential schemas
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

### Config Flow

- [x] Single config entry, no credentials required
- [x] `config_flow_handler/config_flow.py` — minimal user step

### Quality

- [x] Ruff linting: 0 errors
- [x] Pyright type checking: 0 errors
- [x] 49 tests passing:
  - `test_models.py` — 14 tests
  - `test_calculations.py` — 22 tests
  - `test_config_flow.py` — 2 tests
  - `test_init.py` — 5 tests
  - `test_service_actions.py` — 6 tests

---

## Pending

### User-Facing Documentation

- [ ] Rewrite `docs/user/GETTING_STARTED.md` — remove generic boilerplate (host/IP/API key)
- [ ] Rewrite `docs/user/CONFIGURATION.md` — document service actions, entity categories
- [ ] Rewrite `docs/user/EXAMPLES.md` — use actual entity names, real automation examples
- [ ] Update `docs/development/ARCHITECTURE.md` — reflect removed API client, new data flow

### Features

- [ ] Diagnostics (`diagnostics.py`) — redacted bill dump for troubleshooting
- [ ] Multi-config-entry support — scoped storage key per entry
- [ ] Config entry migration (`async_migrate_entry`) — for future schema changes
- [ ] Repair issues — detect invalid bills, orphaned data, future-dated periods

### Quality & Validation

- [ ] HACS submission validation — verify manifest.json, hacs.json compliance
- [ ] Real-device testing — manual QA on a running HA instance
- [ ] `script/hassfest` — validate translations, services.yaml, manifest
- [ ] Snapshot tests for sensor state values

### Nice-to-Have

- [ ] CSV/JSON import for bulk bill entry
- [ ] Recurring bill auto-generation (monthly template)
- [ ] Dashboard card templates
- [ ] Multi-language translations (currently en.json only)
