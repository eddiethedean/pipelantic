# Run Reports

Every ETLantic run returns a structured `PipelineRunReport`.

The report is the canonical, backend-independent summary of what was planned,
executed, produced, validated, retried, skipped, and failed. It preserves the
useful reporting experience from SparkForge while removing medallion-specific
fields and storage-engine assumptions.

## Basic Usage

```python
report = CustomerPipeline.run(profile="production")

print(report.status)
print(report.duration)
print(report.summary)

for step in report.steps:
    print(step.step_id, step.status, step.duration)
```

Async execution returns the same model:

```python
report = await CustomerPipeline.arun(profile="production")
```

## Report Versus Result

ETLantic uses one public run object:

```text
PipelineRunReport
├── normalized execution result
├── step and artifact results
├── validation and state results
├── diagnostics
├── plan summary
└── rendering helpers
```

Internal plugins may produce narrower result objects, but the public run API
normalizes them into `PipelineRunReport`.

The report is data, not console output. Text, JSON, HTML, and other formats are
renderings of the same model.

## Proposed Model

```python
@dataclass(frozen=True)
class PipelineRunReport:
    pipeline_id: str
    pipeline_version: str | None
    plan_id: str
    run_id: str
    intent: RunIntent
    profile: str
    status: RunStatus

    started_at: datetime
    ended_at: datetime | None
    duration: timedelta | None

    summary: RunSummary
    steps: tuple[StepRunReport, ...]
    artifacts: tuple[ArtifactResult, ...]
    validations: tuple[ValidationResult, ...]
    state_transitions: tuple[StateTransitionResult, ...]
    diagnostics: tuple[RunDiagnostic, ...]
    recommendations: tuple[RunRecommendation, ...]
    backend_runs: tuple[BackendRunReference, ...]
```

The exact field names remain proposed until implementation, but these semantic
sections are required.

## Run Summary

`RunSummary` provides the fast SparkForge-style overview:

```python
RunSummary(
    total_steps=8,
    succeeded_steps=7,
    failed_steps=0,
    skipped_steps=1,
    cancelled_steps=0,
    retry_attempts=1,
    records_read=150_000,
    records_produced=149_850,
    records_written=149_850,
    valid_records=149_850,
    invalid_records=150,
    validation_pass_rate=0.999,
    artifacts_produced=10,
    materializations=3,
    state_commits=1,
)
```

Counts may be unavailable or expensive for some backends. Unknown values must
remain `None`; ETLantic must not report zero when the backend did not
measure them.

## Step Reports

Each logical step receives its own report even when several steps are fused
into one SQL statement or Spark execution region.

```python
StepRunReport(
    step_id="normalize_customers",
    transformation_id="normalize_customers",
    status="succeeded",
    attempt_count=1,
    started_at=...,
    ended_at=...,
    duration=...,
    implementation="polars",
    plugin="etlantic-polars",
    physical_unit_id="polars-region-2",
    inputs=(...),
    outputs=(...),
    validations=(...),
    diagnostics=(),
)
```

Step reports should include:

- logical and physical identities
- status and timing
- attempt and retry history
- selected implementation and plugin
- resolved upstream result references
- input and output artifact summaries
- record counts when measured
- validation outcomes
- callback actions
- materialization and cache decisions
- backend metadata and links
- errors and diagnostics

## Previous-Step Results

Reports make direct result reuse visible:

```python
ArtifactTransferReport(
    producer="normalize_customers.result",
    consumer="score_customers.customers",
    strategy="native_lazy_reference",
    materialized=False,
    reused=True,
)
```

This lets users distinguish:

- direct in-memory or lazy reuse
- SQL relation or CTE reuse
- Spark logical-plan reuse
- cache hits
- checkpoint reuse
- durable artifact transfer
- rereads from external source bindings

## Validation Results

Quality reporting includes:

```python
ValidationResult(
    boundary="normalize_customers.result",
    contract_id="customer",
    policy="production",
    evaluated_records=10_000,
    valid_records=9_970,
    invalid_records=30,
    pass_rate=0.997,
    threshold=0.995,
    passed=True,
    valid_artifact=...,
    invalid_artifact=...,
    findings=(...),
)
```

The report must not embed rejected records by default. It references the
invalid artifact when policy permits one to be produced.

## Run Intents and State

Incremental and backfill runs should report:

- requested run intent
- effective strategy
- state read
- cursor or watermark range
- overlap or replay window
- state commit outcome
- whether state advancement was withheld

```python
StateTransitionResult(
    strategy="watermark",
    before="2026-07-15T00:00:00Z",
    candidate="2026-07-16T00:00:00Z",
    committed="2026-07-16T00:00:00Z",
    status="committed",
)
```

Sensitive state values may be redacted or summarized.

## Diagnostics and Recommendations

The report includes stable diagnostics:

```text
PMEXEC301: Step retry succeeded on attempt 2.
PMART214: Result was materialized because it crosses an Airflow task boundary.
PMVAL402: 30 invalid records were routed to quarantine.
```

Recommendations are advisory and separately typed:

```python
RunRecommendation(
    code="PMPERF101",
    message="Output is reused by four consumers; consider persistence.",
    step_id="normalize_customers",
)
```

Recommendations never change execution automatically.

## Backend References

Reports should link to external execution systems when available:

```python
BackendRunReference(
    backend="airflow",
    run_id="scheduled__2026-07-16T...",
    url="https://airflow.example/dags/customer/grid?...",
)
```

Similar references may point to:

- Spark applications
- Databricks jobs
- SQL query history
- cloud logs
- traces
- lineage systems

## Rendering

The report supports deterministic renderers:

```python
report.to_dict()
report.to_json()
report.to_text()
report.to_html()
```

CLI examples:

```bash
etlantic run customer.py:CustomerPipeline
etlantic run customer.py:CustomerPipeline --output json
etlantic report show RUN_ID
etlantic report export RUN_ID --format html
```

HTML reports may add diagrams and styling, but they consume the same canonical
report model.

## Durable Run History

An observability provider may persist reports or reconstruct them from
lifecycle events.

The core should support:

```python
runtime.reports.get(run_id)
runtime.reports.list(pipeline_id="customer_pipeline")
```

Durable history enables:

- execution trends
- quality trends
- performance regression detection
- anomaly detection
- audit evidence
- comparison between profiles and backends

Persistence is provider-owned. `PipelineRunReport` remains provider-neutral.

## Partial and External Runs

Reports must represent incomplete knowledge:

- submitted but still running
- cancelled
- timed out
- abandoned after losing backend contact
- partially successful
- external backend reports unavailable

A report may be updated through immutable snapshots:

```python
snapshot = handle.report()
final_report = await handle.wait()
```

The final state must not be inferred solely from missing errors.

## Security

Reports must exclude:

- secret values
- credential-bearing connection strings
- raw environment snapshots
- raw invalid records
- unbounded backend logs

Plan configuration and backend metadata must be redacted before inclusion.

## Compatibility

The serialized report schema should be versioned independently:

```python
report.schema_version
```

Additive fields may be introduced compatibly. Removing fields or changing their
meaning requires a major report-schema version.

## Relationship to SparkForge

ETLantic preserves SparkForge's useful reporting concepts:

- run ID and mode
- timestamps and duration
- total, successful, failed, and skipped steps
- step-level timing and status
- rows processed and written
- validation rates
- write and table metadata
- warnings and recommendations
- durable execution history

It generalizes them by:

- removing bronze, silver, and gold report sections
- supporting named outputs and direct step-result references
- separating logical steps from fused physical units
- allowing unknown metrics
- including artifacts, state transitions, retries, and backend links
- remaining consistent across SQL, PySpark, Polars, Pandas, and orchestrators

## Key Principle

> Every run returns one structured, backend-independent report. Renderers,
> observability providers, and external runtimes enrich that report without
> changing its portable meaning.

## See Also

- [Execution Model](EXECUTION_MODEL.md)
- [Logging](LOGGING.md)
- [Lifecycle Extensions](LIFECYCLE_EXTENSIONS.md)
- [HTML Reports](../08_VISUALIZATION/HTML.md)
- [Diagnostics](../10_REFERENCE/DIAGNOSTICS.md)
