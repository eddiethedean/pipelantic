# Logging

PipelineModel provides structured, contextual logging for validation, planning,
execution, and plugin coordination.

Logging is part of the shared execution experience, but PipelineModel is not a
log-storage platform. The core defines records, context, redaction, and
lifecycle integration. Logging and observability providers route those records
to the Python logging system, console, files, OpenTelemetry, cloud services, or
other destinations.

## Goals

PipelineModel logging should be:

- structured
- correlated by pipeline, plan, run, step, and attempt
- consistent across execution backends
- safe for secrets and sensitive data
- usable locally and in distributed orchestration
- compatible with standard Python logging
- separable from metrics, traces, lineage, and durable run results

## Logging Versus Results and Events

PipelineModel distinguishes three related concepts:

```text
Lifecycle event
    Immutable fact that something occurred.

Run result
    Normalized outcome and measurements of completed work.

Log record
    Human- and machine-readable diagnostic narrative.
```

For example:

```text
event:  step.started
log:    Starting step "normalize_customers" with implementation "polars"
result: StepRunResult(status="succeeded", duration=1.42, ...)
```

Providers may derive logs from lifecycle events, but logs must not be the only
source of execution state.

## Structured Log Record

The proposed core model is:

```python
LogRecord(
    timestamp=...,
    level="INFO",
    code="PMEXEC100",
    message='Starting step "normalize_customers"',
    pipeline_id="customer_pipeline",
    pipeline_version="2.1.0",
    plan_id="plan_01...",
    run_id="run_01...",
    step_id="normalize_customers",
    attempt=1,
    plugin="pipelinemodel-polars",
    backend="polars",
    event="step.started",
    attributes={
        "implementation": "polars",
        "input_count": 1,
    },
)
```

All correlation fields are optional at the model level because validation and
planning logs may occur before a run exists. Providers should include every
field available in the current context.

## Logging Context

Context should propagate automatically:

```text
project
  └── pipeline
        └── plan
              └── run
                    └── step
                          └── attempt
```

Plugin authors should not manually copy identifiers into each message.

Conceptually:

```python
with logger.bind(run=run_context):
    logger.info(
        "PMEXEC100",
        "Starting pipeline run",
        intent=request.intent,
    )

    with logger.bind(step=step_context):
        logger.info(
            "PMEXEC110",
            "Starting step",
            implementation=step.implementation,
        )
```

Context propagation must work across async tasks. External orchestrator plugins
must map correlation identifiers into their native task context.

## Standard Logging Phases

### Loading

- source or contract discovered
- format and version identified
- reference resolved
- configuration loaded

### Validation

- validation phase started or completed
- rule or compatibility finding
- quality-gate outcome
- invalid artifact produced

### Planning

- profile applied
- implementation selected
- capability decision
- execution region formed
- materialization inserted
- fallback selected

### Execution

- run and step lifecycle
- attempt and retry behavior
- upstream artifact resolved
- resource acquired or released
- artifact materialized
- state read or committed
- callback decision

### Compilation and submission

- backend artifact generated
- external run submitted
- remote state synchronized
- cancellation requested

## Levels

Recommended use:

| Level | Meaning |
|---|---|
| `TRACE` | Fine-grained internal decisions, disabled by default |
| `DEBUG` | Developer-facing planning and execution detail |
| `INFO` | Normal lifecycle progress |
| `WARNING` | Recoverable degradation, fallback, or policy concern |
| `ERROR` | Failed operation or rejected semantic requirement |
| `CRITICAL` | Framework or environment failure affecting safe operation |

Diagnostics retain their own severity. A diagnostic may be rendered as a log,
but diagnostic severity and log level are not interchangeable.

## Stable Codes

Important logs should carry stable codes:

```text
PMLOADxxx   Loading and identification
PMVALxxx    Validation and quality
PMPLANxxx   Planning and capability resolution
PMEXECxxx   Execution lifecycle
PMARTxxx    Artifact handling
PMSTATExxx  Incremental state and checkpoints
PMPLUGxxx   Plugin behavior
PMSECxxx    Security and redaction
```

Codes make filtering and alerting reliable even when message wording improves.

## Configuration

```toml
[logging]
level = "INFO"
format = "console"
include_context = true

[logging.redaction]
enabled = true
keys = ["password", "token", "secret", "authorization"]

[profiles.production.logging]
level = "INFO"
provider = "opentelemetry"
json = true
```

Run-scoped overrides may increase verbosity:

```bash
pipelinemodel run customer.py:CustomerPipeline --log-level DEBUG
```

Changing log verbosity must not change pipeline semantics or plan identity.

## Python Logging Integration

The default provider should integrate with `logging`:

```python
import logging

logging.getLogger("pipelinemodel").setLevel(logging.INFO)
logging.getLogger("pipelinemodel.plugin.airflow").setLevel(logging.DEBUG)
```

Recommended logger hierarchy:

```text
pipelinemodel
pipelinemodel.loading
pipelinemodel.validation
pipelinemodel.planning
pipelinemodel.execution
pipelinemodel.plugin.<plugin-name>
```

PipelineModel should not call `logging.basicConfig()` automatically in library
usage. The CLI may configure its own handlers.

## Secret and Data Safety

Logs must never contain:

- resolved secret values
- authorization headers
- connection strings containing credentials
- unredacted environment snapshots
- complete dataframe or record contents by default
- raw invalid rows by default
- serialized plans containing secret material

Redaction should inspect both keys and registered sensitive-value types.
Providers must receive already-redacted records unless explicitly operating
inside a trusted secured boundary.

Data samples require a separate, explicit debug policy:

```python
DataLoggingPolicy(
    enabled=False,
    maximum_rows=0,
    allowed_classifications=set(),
)
```

## Plugin Requirements

Plugins must:

- use the logging context supplied by PipelineModel
- preserve correlation identifiers
- avoid adding their own global handlers
- classify expected failures with stable error categories
- redact plugin configuration and backend messages
- avoid logging the same exception repeatedly at multiple layers

Plugins may attach backend metadata such as job, query, task, or cluster IDs.

## External Orchestrators

External runtimes often own their own logs. The orchestration plugin should map:

```text
PipelineModel run_id   ↔ orchestrator run identifier
PipelineModel step_id  ↔ task identifier
PipelineModel attempt  ↔ task attempt
PipelineModel trace_id ↔ native trace context
```

PipelineModel should link to native logs rather than copying an unlimited
remote log stream into the core result.

## Local Debugging

Interactive execution should make upstream-result resolution visible:

```text
DEBUG PMART110 Reusing output "normalized.result" from current run context
DEBUG PMPLAN214 Keeping edge in Polars lazy execution region
INFO  PMEXEC110 Starting step "score_customers"
```

This is especially important when a result is reused, invalidated, cached, or
materialized.

## Testing

Tests should assert structured fields rather than formatted strings:

```python
def test_step_log_contains_context(captured_logs):
    record = captured_logs.find(code="PMEXEC110")
    assert record.run_id == "run-123"
    assert record.step_id == "normalize_customers"
```

Conformance tests should verify:

- correlation propagation
- redaction
- deterministic codes
- exception normalization
- async isolation
- no secret leakage

## Key Principle

> PipelineModel defines one safe, structured logging context across every
> backend. Providers control routing and storage; logs never replace lifecycle
> events or normalized results.

## See Also

- [Execution Model](EXECUTION_MODEL.md)
- [Plugins](PLUGINS.md)
- [Diagnostics](../10_REFERENCE/DIAGNOSTICS.md)
- [Configuration](../10_REFERENCE/CONFIGURATION.md)
- [Observability Provider](../07_PLUGIN_SDK/OBSERVABILITY_PROVIDER.md)
