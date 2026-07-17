# Compatibility Matrix

This table describes the declared compatibility of ETLantic 0.10.0.

| Surface | Supported range or version |
|---|---|
| Python | 3.11, 3.12, 3.13 |
| Pydantic | `>=2.12,<3` |
| ContractModel | `>=0.1.2` |
| DTCS specification | `2.0.0` (`dtcsVersion: "2.0.0"`) |
| DTCS toolkit | `>=0.12,<1` |
| DPCS toolkit | `>=0.13,<1` |
| Pipeline plan schema | `etlantic.plan/1` |
| Dataframe protocol | `etlantic.dataframe/1` |
| SQL protocol | `etlantic.sql/1` |
| Polars plugin | `etlantic-polars==0.10.0` |
| Pandas plugin | `etlantic-pandas==0.10.0` |
| SQL plugin | `etlantic-sql==0.10.0` |
| PySpark plugin | `etlantic-pyspark==0.10.0` |
| Airflow plugin | `etlantic-airflow==0.10.0` |
| Keyring provider | `etlantic-keyring==0.10.0` |
| SQLModel bridge | `etlantic-sqlmodel==0.10.0` |
| SparkForge adapter | `etlantic-sparkforge==0.10.0` |
| Orchestration protocol | `etlantic.orchestration/1` |
| DTCS Transformation Plan protocol | Published in DTCS 2.0 / `dtcs` 0.12 as `dtcs.transform-plan/1`; ETLantic authoring not shipped |
| Portable authoring profile | Not shipped; proposed `etlantic.transform/1` |
| Portable compiler protocol | Not shipped; proposed `etlantic.transform-compiler/1` for 0.12+ |
| Package stability | Alpha |
| Plugin SDK stability | Protocol stable within 0.8; third-party SDK still evolving |

## Portable transformation profiles

DTCS publication does not mean the ETLantic facade or plugin compilers are
already implemented. Compatibility is tracked independently:

| DTCS 2.0 profile | Standard status | ETLantic 0.10 status |
|---|---|---|
| `dtcs:profile/portable-relational-kernel/1` | Published | planned for 0.11 |
| `dtcs:profile/portable-relational/1` | Published | planned across 0.11–0.13 |
| `dtcs:profile/portable-window/1` | Experimental | planned for 0.15+ |
| `dtcs:profile/portable-complex-types/1` | Experimental | planned for 0.15+ |

Plugins will claim exact profiles or individual registered capabilities only
after passing the associated conformance fixtures. Similar backend behavior is
not a compatibility claim.

## Backend dependency ranges

Package metadata is authoritative; these are the 0.10 reference ranges:

| Integration | Backend range / boundary |
|---|---|
| Polars | `polars>=1.0,<2` |
| Pandas | `pandas>=2.0,<3` |
| SQL | `sqlalchemy>=2.0,<3`; PostgreSQL reference, SQLite demos only |
| PySpark | `pyspark>=3.5,<4` |
| Airflow | Compiler emits Python DAG source; Airflow is not imported by the plugin package |
| SQLModel | `sqlmodel>=0.0.22,<1` |
| SparkForge | IR adapter only; no live SparkForge dependency in 0.10 |

The package metadata in `pyproject.toml` is authoritative for dependency
ranges. During the 0.x series, public APIs and persistent formats may change.
Breaking changes must be called out in the changelog with an upgrade path.

Portable compiler compatibility will be tracked independently across core,
Pipeline Plan schema, DTCS plan/package version, ETLantic authoring profile,
compiler protocol/package, and advertised operation/function versions.
