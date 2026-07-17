# etlantic-airflow

Airflow reference orchestrator compiler for [ETLantic](https://github.com/eddiethedean/etlantic).

```bash
pip install etlantic-airflow
# or: pip install 'etlantic[airflow]'
# To import generated DAGs into an Airflow process, install apache-airflow
# separately in the Airflow environment (not required for compile).
```

## Wiring

```python
from etlantic import Profile, plan_pipeline, compile_plan

profile = Profile(
    name="airflow-prod",
    orchestrator="airflow",
    schedule={"type": "cron", "expression": "0 2 * * *", "timezone": "UTC"},
    execution={"retries": 2, "timeout_seconds": 3600},
)
plan = plan_pipeline(MyPipeline, profile=profile)
artifact = compile_plan(plan, target="airflow", profile=profile)
artifact.write("dags/my_pipeline.py")
```

## Capabilities (0.8)

- Deterministic Airflow DAG module generation from a secret-free `PipelinePlan`
- Schedule, retry, timeout, and dependency mapping
- Retry-safety fail-closed for unsafe sinks
- Artifact-ref-only XCom payloads (no large inline data)
- Lifecycle correlation keys for normalized run reports

**Not included:** managed Airflow deployments, Dagster/Prefect compilers (future
plugins). CLI `etlantic compile … --target airflow` is available in core 0.9+.
