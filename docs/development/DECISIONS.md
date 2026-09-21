# Architectural and Design Decisions

This document records significant architectural and design decisions made during the development of this integration.

## Format

Each decision is documented with:

- **Date:** When the decision was made
- **Context:** Why this decision was necessary
- **Decision:** What was decided
- **Rationale:** Why this approach was chosen
- **Consequences:** Expected impacts and trade-offs

> [!NOTE]
> Guidance on _when_ a decision is worth recording here, and a copy-ready entry template, lives in the
> [`ha-planning`](../../.agents/skills/ha-planning/SKILL.md) agent skill.

---

## Decision Log

### Local-Only Storage via HA Store

**Date:** 2026-08-27 (Consolidation)

**Context:** Home Ledger tracks household utility bills. No external API or device is involved — all data is entered manually by the user.

**Decision:** Use `homeassistant.helpers.storage.Store` for persistent bill storage. No API client, no cloud dependency.

**Rationale:**

- All data originates from user input via service actions
- No device to poll, no credentials to manage
- `Store` handles serialization, migration, and HA lifecycle automatically
- Zero network dependency = zero availability issues

**Consequences:**

- Bills survive HA restarts without additional work
- Single-point-of-truth on one HA instance (no sync across instances)
- Storage schema must be versioned for future migration

---

### Bill Frozen Dataclass with UtilityType Enum

**Date:** 2026-08-27 (Consolidation)

**Context:** Bills need a structured representation that validates on creation and serializes cleanly to storage.

**Decision:** `Bill` is a frozen dataclass with `UtilityType` (StrEnum: electricity, gas, water). Validation runs in `__post_init__`. Serialization via `as_storage_dict()` / `from_storage_dict()`.

**Rationale:**

- Frozen = immutable, no accidental mutation after creation
- `__post_init__` catches bad data at construction time, not at save time
- StrEnum serializes cleanly to JSON without custom encoders
- `as_storage_dict()` keeps storage format decoupled from internal fields

**Consequences:**

- "Update" creates a new `Bill` (or patches the storage dict directly)
- Adding a field requires updating both the dataclass and the storage migration

---

### Coordinator with No Polling Interval

**Date:** 2026-08-27 (Consolidation)

**Context:** Data changes only when the user explicitly adds, updates, or deletes a bill. There is nothing to poll.

**Decision:** `HomeLedgerDataUpdateCoordinator` extends `DataUpdateCoordinator` with `update_interval=None`. Aggregates are recalculated on demand via `async_refresh_bills()`, called after each CRUD operation.

**Rationale:**

- Polling an unchanged local store wastes cycles
- HA's coordinator is still useful for its listener/notification pattern
- `async_set_updated_data()` pushes new aggregates to all entities immediately

**Consequences:**

- No automatic periodic refresh (not needed)
- Entities update instantly after any service action
- `async_refresh_bills()` must be called explicitly after every bill mutation

---

### Service-Action CRUD + Options Flow for Bill Entry

**Date:** 2026-08-29 (Redesign)

**Context:** Users manage bills by adding, updating, and deleting records. A simple "months" integer was too imprecise for real-world billing cycles (e.g., partial months).

**Decision:** Replace the `months` field with a required date range (`start_date` and `end_date`). Retain both service actions and an options flow for entry.

**Rationale:**

- **Precision:** Using dates allows calculating an exact daily rate, which is the most accurate way to determine monthly averages.
- **Flexibility:** Handles any billing cycle (weekly, monthly, bimonthly) without user calculation.
- **Consistency:** Both UI and API paths use the same `Bill` model.

**Consequences:**

- **Breaking Change:** Existing bill data is incompatible.
- **Calculation Change:** Averages now use the formula `(total / days) * 30.44`.
- **UX Change:** Users must now provide specific dates instead of a number of months.

---

### SensorDescription + Value Function Pattern

**Date:** 2026-08-27 (Consolidation)

**Context:** 16 sensor entities are derived from aggregated bill data. Each reads a single field from `HomeLedgerAggregates`.

**Decision:** Each sensor is defined as a `HomeLedgerSensorEntityDescription` with a `value_fn` lambda that extracts one field from the aggregates dataclass.

**Rationale:**

- Declarative: one tuple per category (cost, consumption, average, cost-per-unit)
- No per-sensor API calls — all data comes from coordinator
- `translation_key` drives entity names (no hardcoded strings)
- Adding a new sensor = adding one description to the tuple

**Consequences:**

- `value_fn` signature must match `HomeLedgerAggregates` fields
- Sensor descriptions live in `sensor/utilities.py`, entity class in `sensor/entity.py`

---

## Future Considerations

### Multi-Config-Entry Support

**Status:** Not yet implemented

Current architecture assumes a single config entry per HA instance. If users want separate ledgers (e.g., rental properties), the storage key and coordinator will need scoping by entry ID.

### Diagnostics

**Status:** Not yet implemented

Add `diagnostics.py` with `async_redact_data()` to dump bill data for troubleshooting. No credentials to redact, but bills may contain user-preferred IDs.

### Config Entry Migration

**Status:** Not yet implemented

If `entry.data` shape changes (e.g., adding settings), `async_migrate_entry()` and `VERSION`/`MINOR_VERSION` bump will be needed.

### Repair Issues for Invalid Bills

**Status:** Not yet implemented

Detect and surface repair issues for orphaned bills, impossible consumption values, or future-dated bill periods.

---

## Decision Review

These decisions should be reviewed periodically (suggested: quarterly or when major features are added) to ensure they still serve the integration's needs.
