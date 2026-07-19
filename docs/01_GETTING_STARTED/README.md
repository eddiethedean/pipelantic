# Getting Started

Welcome to ETLantic!

ETLantic catches incompatible data-pipeline wiring **before** you process
data. Define typed datasets, transformations, and pipelines in Python;
validate and plan them once; run locally or through optional engine plugins.

> **Project status:** ETLantic **0.18.0** is production/stable within the
> documented single-tenant reference deployment boundary. Experimental
> features and broader deployment models remain outside that claim. See
> [Capabilities](CAPABILITIES.md) for the shipped boundary and
> [Evaluator brief](EVALUATOR.md) for decision-makers. How to read status labels:
> [Documentation Status](../02_FOUNDATIONS/DOCUMENTATION_STATUS.md).

## Five-minute path

1. [Installation](INSTALLATION.md) — `pip install etlantic==0.18.0`
2. [Quickstart](QUICKSTART.md) — copy, run, see Ada Lovelace
3. [First Pipeline](FIRST_PIPELINE.md) — CLI `inspect` / `validate` / `plan`
4. [Capabilities](CAPABILITIES.md) — then [Evaluator](EVALUATOR.md) or an engine tutorial

!!! note "CLI validate/plan vs Python run"
    Use the CLI for `inspect`, `validate`, and `plan`. In-memory quickstarts
    must seed data in Python (`PipelineRuntime.memory.seed`) before
    `Pipeline.run`—a fresh `etlantic run` process has an empty memory store.
    Use CLI `run` when assets are bound to durable storage (JSON/CSV/SQL).

## What You'll Learn

- Install ETLantic from PyPI
- Define typed data contracts and transformations
- Wire a pipeline and validate it before execution
- Run locally with in-memory storage
- Use the CLI for `validate` / `plan` (and `run` when assets are durable)
- Tell shipped APIs from future design

## Prerequisites

- Python 3.11+
- Basic type annotations
- Familiarity with ETL concepts helps; orchestration experience is optional

## Documentation Roadmap

1. [Installation](INSTALLATION.md)
2. [Quickstart](QUICKSTART.md)
3. [Your First Pipeline](FIRST_PIPELINE.md)
4. [Capabilities and Limitations](CAPABILITIES.md)
5. Choose an engine: [Engine selection](ENGINE_SELECTION.md), then
   [Polars](../06_EXECUTION/POLARS_TUTORIAL.md),
   [Pandas](../06_EXECUTION/PANDAS_TUTORIAL.md),
   [SQL](../06_EXECUTION/SQL_TUTORIAL.md), or
   [PySpark](../06_EXECUTION/PYSPARK_TUTORIAL.md)
6. [Evaluator Brief](EVALUATOR.md)
7. [Compare](COMPARE.md) / [FAQ](FAQ.md) / [Troubleshooting](TROUBLESHOOTING.md)
8. [Project Structure](PROJECT_STRUCTURE.md) (after a second pipeline)
9. [Cookbook](COOKBOOK.md) for common recipes

## The ETLantic Mental Model

``` text
Typed Python classes
      │
      ▼
Validation (catch bad wiring)
      │
      ▼
PipelinePlan (secret-free, deterministic)
      │
      ▼
Run locally  |  Compile (Airflow)  |  Generate contracts
```

ETLantic 0.18.0 can execute registered Python implementations with its local
runtime and optional Polars/Pandas/SQL/PySpark plugins, compile plans to
Airflow DAGs via `etlantic-airflow`, execute plans through the Prefect local
MVP, and compile supported portable transformation families without native
engine implementations.

## Next Step

Continue with [Installation](INSTALLATION.md), then
[Quickstart](QUICKSTART.md).
