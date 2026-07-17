# Evaluator Brief

A one-page answer for enterprise evaluators and technical decision-makers.

## What ETLantic is

A typed, contract-driven **modeling** layer for data pipelines in Python. You
define datasets, transformations, and pipelines once; ETLantic validates and
plans them; plugins execute.

It is **not** a dataframe engine, distributed scheduler, warehouse, or secret
manager.

## What is ready in alpha 0.9.0

| Area | Ready? |
|---|---|
| Typed authoring (`Data`, `Transformation`, `Pipeline`) | Yes |
| Validation and secret-free `PipelinePlan` | Yes |
| ODCS / DTCS / DPCS interchange | Yes |
| Local in-process runtime + run reports | Yes |
| Memory / callable / JSON / CSV / no-write storage | Yes |
| Env + mounted-file secrets | Yes |
| Polars / Pandas plugins | Yes (separate packages) |
| SQL plugin (`etlantic-sql`) | Yes (PostgreSQL reference) |
| PySpark plugin (`etlantic-pyspark`) | Yes (local provider; batch production path) |
| Structured Streaming | Experimental |
| Airflow / orchestrator compilation | Yes (`etlantic-airflow`) |
| Multi-tenant durable orchestration | No |
| Formal SLA / support response times | No |

## Security posture

- Plans never contain resolved secrets
- SQL plugins use structured compilation with identifier/parameter safety;
  untrusted raw SQL is out of scope
- Spark session credentials resolve at acquire time and never embed in plans
- Threat model documents many controls as **Gap** (plugin allowlists, DoS
  budgets, stronger isolation)—read
  [Security](../02_FOUNDATIONS/SECURITY.md) and the repository
  [security policy](https://github.com/eddiethedean/etlantic/blob/main/SECURITY.md)
- Report vulnerabilities privately; alpha has best-effort fixes only

## What not to bet on yet

- Copying long Airflow “design study” tutorials into production
- Treating Structured Streaming APIs as stable (they are experimental in 0.7)
- AWS Secrets Manager / Vault / keyring configuration from older docs
- Process-local reports as an audit system of record
- Stable 1.0 compatibility guarantees

## Recommended evaluation path

1. [Capabilities](CAPABILITIES.md)
2. [Quickstart](QUICKSTART.md) or `examples/quickstart.py`
3. Optional: `examples/dataframe_parity.py` with Polars or Pandas
4. Optional: `examples/sql_to_sql.py` (and other `examples/sql_*.py`) with
   `etlantic-sql`
5. Optional: `examples/pyspark_local.py` with `etlantic-pyspark`
6. [Migration 0.6 → 0.7](../11_DEVELOPMENT/MIGRATION_0_6_TO_0_7.md) if upgrading
7. [Roadmap](../11_DEVELOPMENT/ROADMAP.md) for sequencing

## Support channel

GitHub issues for bugs and questions. Include ETLantic version, Python
version, and a minimal reproduction. Never include credentials or production
data.
