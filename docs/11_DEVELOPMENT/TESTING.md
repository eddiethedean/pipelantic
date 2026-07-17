# Testing

## Run the current test suite

```bash
uv sync --locked
uv run pytest -q
uv run ruff check .
uv run ruff format --check .
uv run python scripts/check_docs.py
uv run python scripts/build_docs.py
```

Run the narrowest relevant test directory while developing, then the complete
suite before opening a pull request. Current test areas include core validation
and planning plus `tests/dataframe`, `tests/sql`, `tests/spark`,
`tests/orchestration`, `tests/airflow`, and `tests/sparkforge` where present.

Current optional markers are `polars`, `pandas`, `sql`, `spark`, `airflow`,
`keyring`, `sqlmodel`, and `sparkforge`; `pyproject.toml` is authoritative.

```bash
uv sync --group dataframes
uv run pytest -m polars
uv run pytest -m pandas

uv sync --group sql
uv run pytest -m sql

uv sync --group pyspark
uv run pytest -m spark
```

To debug collection or plugin discovery, begin with `pytest --collect-only`,
then run one failing node with `-vv -x`. Never depend on plugin discovery order,
ambient environment variables, production credentials, or shared mutable
runtime state.

## Future requirement: portable transformation conformance (0.14+)

Every compiler runs capability-selected fixtures from
`etlantic.testing.portable_transform_conformance`. Shared fixtures cover IR
canonicalization, null/type/error semantics, deterministic compilation,
multiple outputs, lazy/eager behavior, ownership, hostile bounded input,
redaction, and cross-engine normalized results. Advertising an operation or
function makes its fixture mandatory.

ETLantic testing must prove that typed models, portable contracts,
planning, and backend execution preserve the same semantics.

## Test Layers

```text
Unit tests
    ↓
Model and contract tests
    ↓
Planner tests
    ↓
Plugin conformance tests
    ↓
Integration tests
    ↓
End-to-end tests
```

## Unit Tests

Unit tests cover:

- Annotation parsing
- Stable identifiers
- Port collection
- Graph construction
- Diagnostic rendering
- Registry behavior
- Profile merging
- Capability matching
- Plan serialization

Tests should avoid importing heavyweight optional backends unless they target an
integration.

## Model Definition Tests

Verify:

- Required and optional inputs
- Multiple outputs
- Parameter defaults and constraints
- Inheritance behavior
- Invalid annotations
- Forward references
- Generic source and sink types
- Step output typing

## Contract Tests

For ODCS, DTCS, and DPCS:

- Code-first generation
- Contract-first loading
- Semantic round trips
- Canonical output
- Supported-version dispatch
- Invalid document diagnostics
- Compatibility behavior

Normative fixtures should come from the corresponding standards where
available.

## Validation Tests

Test each validation phase independently:

- Model definition
- Contract integration
- Port compatibility
- Graph topology
- Profile bindings
- Plugin capabilities
- Runtime data boundaries

Diagnostics should be asserted by code, path, and severity rather than fragile
full-message matching unless testing rendering.

## Planner Tests

Planner tests should verify:

- Deterministic plans
- Implementation selection
- Binding resolution
- Execution region formation
- Materialization boundaries
- SQL and Spark fusion safety
- Hybrid backend boundaries
- Capability failures
- Absence of secrets

Equivalent input must produce equivalent canonical plans.

## Plugin Conformance

The future portable SDK is expected to provide reusable suites:

```python
def test_plugin_conformance():
    assert_dataframe_plugin_conforms(plugin)
```

Conformance should cover:

- Protocol shape
- Capability accuracy
- Lifecycle and cleanup
- Sync and async callables
- Error normalization
- Cancellation
- Contract validation behavior
- Resource safety

See [Testing Plugins](../07_PLUGIN_SDK/TESTING_PLUGINS.md).

## Backend Integration Tests

Backend test environments should be isolated and optional:

- Pandas and Polars in-process
- SQLite or DuckDB for SQL smoke tests
- Spark local mode for PySpark
- Containerized databases where necessary
- Airflow compilation tests without requiring a scheduler for every test

Mark tests by dependency:

```text
unit
integration
sql
spark
airflow
slow
network
```

## End-to-End Tests

Each primary workflow should validate the complete path:

```text
Python model
→ contracts
→ validation
→ plan
→ backend
→ results
→ lineage and generated docs
```

Representative cases:

- CSV to CSV with Polars
- CSV to SQL
- SQL to SQL with pushdown
- Pandas pipeline
- PySpark to Delta
- Structured Streaming
- Local execution and Airflow compilation

## Golden Tests

Golden files are appropriate for:

- Generated ODCS, DTCS, and DPCS
- Canonical `PipelinePlan`
- Diagnostics
- Mermaid and Graphviz
- Compiled Airflow DAGs
- SQL output

Updates must be reviewed as semantic changes, not accepted mechanically.

## Property-Based Testing

Use property-based tests for:

- Graph construction and cycle detection
- Identifier normalization
- Profile merging
- Plan serialization round trips
- Diff and compatibility invariants
- Schema normalization and fingerprint determinism
- Contract drift versus operational drift classification
- Schema-history idempotency and concurrent baseline updates
- Drift-policy precedence and fail-closed behavior
- Field-level impact analysis with complete and incomplete lineage
- Equivalent observations across dataframe, SQL, Spark, and Arrow inspectors
- Freshness windows across timezones, grace periods, and schedule boundaries
- Missing, late, duplicate, unexpected, and partially published partitions
- Minimum-safe invalidation and repair closure
- Idempotency and retry matrices for pure, transactional, compensatable, and
  unsafe operations
- Portable write and materialization semantics across supported backends
- SQLModel-to-`Data` mapping, deterministic model generation, migration safety,
  repository transactions, tenant isolation, and API field separation
- Reconciliation snapshots, tolerances, and control totals
- Backfill range, partition, state-isolation, cancellation, and resume behavior
- Cross-backend null, precision, ordering, timezone, and invalid-data parity
- Plan and environment fingerprint stability and semantic drift classification
- Quality-trend windows, deduplicated notifications, and statistical privacy
  budgets
- Random valid transformation signatures

## Async Testing

Tests must cover:

- Sync implementations
- Async implementations
- Mixed DAG branches
- Cancellation
- Timeouts
- Cleanup after failure
- Sync hooks returning awaitables
- Async resource providers

Avoid tests that depend on timing alone. Use synchronization primitives and
controlled fakes.

## Type-Checking Tests

Maintain positive and negative typing fixtures:

```text
tests/typing/pass/
tests/typing/fail/
```

Examples should prove IDE-visible types for step outputs and catch invalid
wiring where standard Python typing permits.

## Coverage

Coverage is a signal, not the goal. Critical planner, validation, security, and
cleanup branches require direct tests even when aggregate coverage is high.

## Test Isolation

- Use explicit runtimes and registries.
- Do not depend on plugin discovery order.
- Reset environment variables.
- Use temporary directories.
- Do not share mutable dataframe artifacts across tests.
- Never use production credentials.
- Treat security tests as release gates rather than optional integration tests.

## Security Testing

The security suite should cover unsafe deserialization, parser limits, path
traversal, SSRF, planning purity, plugin allowlists, injection, secret leakage,
artifact and cache isolation, outbound destination policy, credential cleanup,
and denial-of-service budgets.

Security-sensitive parsers and resolvers should receive property-based tests
and fuzzing where practical.

## Documentation Tests

Code examples should be executable or syntax-checked. Generated examples should
be verified in CI so documentation does not drift from the public API.
