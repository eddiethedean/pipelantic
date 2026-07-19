# What's New in 0.18

**Status: Available in 0.18.**

ETLantic 0.18.0 ships Gate A versioned tabular interchange for compatible
cross-engine dataframe boundaries. It keeps ETLantic contracts as the semantic
authority and records the physical interchange decision in deterministic plans.

## Gate A — versioned tabular interchange

- Plans can carry an immutable `etlantic.interchange/1` descriptor.
- Selection is capability-driven rather than keyed to hard-coded engine pairs.
- Mechanisms include Arrow C Data/C Stream, Arrow IPC, Parquet artifacts, and
  explicit records/native fallbacks.
- Fidelity bounds, ownership, collection, and copy eligibility are validated
  before execution.
- Run reports preserve bounded conversion, copy, and cleanup evidence without
  storing source rows or secret values.
- Public testing helpers cover selection, descriptor validation, evidence, and
  Polars↔Pandas cross-engine execution.

## Compatibility boundary

Gate A is available for the Polars↔Pandas conformance pair. PySpark and SQL
Arrow physical boundaries remain follow-up work. PyArrow remains optional and
is not imported by core unless the relevant integration is used.

The older Arrow-assisted dataframe conversion helper remains available as a
legacy best-effort path. It is not a substitute for a planned
`etlantic.interchange/1` boundary.

DataFusion did not ship in 0.18.0. It remains a non-blocking Gate B / 0.19+
experiment.

## Upgrade

Stored 0.17 plans do not gain interchange descriptors through silent upgrade.
Regenerate plans with 0.18 and review the selected mechanisms and bounds. See
[Migration 0.17 → 0.18](../11_DEVELOPMENT/MIGRATION_0_17_TO_0_18.md).
