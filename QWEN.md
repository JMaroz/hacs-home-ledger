# Home Ledger — Project Context

## Project Overview

**Home Ledger** is a Home Assistant custom integration for tracking household utility bills (electricity, gas, water) and computing cost/consumption aggregates. It is installed via HACS and stores all data locally using Home Assistant's storage system — no external API or credentials required.

**Identity (use these exactly, never a variant):**

- **Domain:** `home_ledger`
- **Title:** Home Ledger
- **Repository:** `andmaroz89/hacs-home-ledger`
- **Class prefix:** `HomeLedger`

**Key architecture:**

- **Storage layer** (`storage.py`) — persists bills via HA's `Store` helper
- **Data models** (`models.py`) — `Bill` dataclass with validation, `UtilityType` enum
- **Coordinator** (`coordinator/base.py`) — `DataUpdateCoordinator` that calculates aggregates from bills
- **Runtime data** (`data.py`) — `HomeLedgerData` (entry.runtime_data) and `HomeLedgerAggregates`
- **Sensor entities** (`sensor/`) — 16 sensors for costs, consumption, averages, and cost-per-unit
- **Service actions** (`service_actions/`) — `add_bill`, `update_bill`, `delete_bill`, `list_bills`
- **Config flow** (`config_flow_handler/`) — config entry + options flow, no credentials needed

**Layering:** Entities → Coordinator → Storage. Entities read `coordinator.data` and never reach past it.

## Building and Running

### Development scripts (always use these, never raw commands)

```bash
./script/develop                  # Start local Home Assistant instance
./script/ha status                # Check HA instance state
./script/ha entries               # Check config entry status
./script/ha states                # List integration entities
./script/ha diagnostics           # Download diagnostics
./script/ha logs --level error    # View error logs
./script/ha flow start            # Walk config flow without browser

# Validation (fix mode — auto-fixes what it can):
./script/lint                     # Ruff fix + YAML/shell/markdown checks
./script/type-check               # Pyright (manual loop, no auto-fix)
./script/hassfest                 # Validate manifest, translations, services.yaml
./script/test [--cov-html]        # Run pytest suite

# Release:
./script/version <version>        # Bump version
./script/release-notes            # Generate changelog
```

**Validation loop:** Run `script/lint` and `script/type-check` until both exit 0. Fix what remains manually. No separate `-check` run needed after fix-mode scripts.

### Home Assistant instance

- Started by `./script/develop` (takes over, kills existing)
- Config in `config/`, logs in `config/home-assistant.log`
- **Never read `config/.storage/` while HA is running** — use `script/ha` instead
- After changing Python files, `manifest.json`, `services.yaml`, or translations — restart the instance

## Development Conventions

### Python style

- 4 spaces, 120 columns, double quotes
- Full type hints, async for all I/O
- Google docstring convention
- Python 3.14+ required

### Code organization

- `custom_components/home_ledger/` — integration code
  - `api/` — API client (absent here, no external API)
  - `coordinator/` — data update coordinator
  - `config_flow_handler/` — config flow + options + schemas/validators
  - `entity/` — base entity classes
  - `entity_utils/` — entity helpers
  - `sensor/` — sensor platform (one entity class per file)
  - `service_actions/` — service action implementations
  - `utils/` — integration-wide utilities
- `tests/` — mirrors integration structure
- `docs/development/` — architecture, decisions, rationale
- `docs/user/` — user documentation

### Key rules

- **Register service actions in `async_setup()`**, not `async_setup_entry()`
- **Entity metadata from `EntityDescription` + `translation_key`** — never hardcoded `name=` or `icon=`
- **Unique IDs:** serial numbers, MACs, device IDs — never IPs, hostnames, usernames, emails
- **Coordinator failures:** raise `ConfigEntryAuthFailed`, `UpdateFailed`, `ConfigEntryNotReady`, or `ConfigEntryError`
- **Diagnostics must call `async_redact_data()`** for credentials and personal data
- **YAML configuration is deprecated** — config flow only
- **Changing `entry.data` shape** requires `VERSION`/`MINOR_VERSION` bump + `async_migrate_entry()`
- **Comments default to none** — only for workarounds, constraints, or deviations the code cannot express

### Commits

- Conventional Commits format (`feat:`, `fix:`, `docs:`, `refactor:`, etc.)
- **Never commit automatically** — only on explicit request
- Each commit needs fresh instruction; previous permission is not standing

### Breaking changes

- Warn before changing entity IDs, unique IDs, config entry data, state values, units, device classes, service signatures
- Before `1.0.0`, breaking is usually acceptable; after `1.0.0`, prefer migration path
- Never write `async_migrate_entry` or bump `VERSION`/`MINOR_VERSION` unprompted

## Testing

- `script/test` runs the test suite
- `script/test --cov-html` for coverage report
- `script/test --snapshot-update` to update snapshots
- Tests mirror the integration structure under `tests/`
- Use `pytest-homeassistant-custom-component` fixtures
- `enable_custom_integrations` fixture required for integration tests

## Dependencies

- No external PyPI dependencies (manifest `requirements` is empty)
- Home Assistant 2026.8.0 minimum
- Python 3.14+ required

## AI Agents

This project has extensive AI agent instructions in `.agents/`. The routing table in `AGENTS.md` maps tasks to skills and style rules. Key skills:

- `ha-entity-platform` — entity platforms and individual entities
- `ha-service-action` — service actions
- `ha-config-flow` — config flow, options, reauth, discovery
- `ha-coordinator-debug` — coordinator, API client, debugging
- `ha-breaking-changes` — anything that could break existing installs
- `ha-testing` — test writing and maintenance
- `ha-release` — versioning, changelog, commit messages
- `blueprint-tooling` — validation scripts, template sync

## Reference Links

- [Home Assistant Developer Docs](https://developers.home-assistant.io/)
- [Integration Quality Scale](https://developers.home-assistant.io/docs/integration_quality_scale_index)
- [Architecture Docs](https://developers.home-assistant.io/docs/architecture_index)
