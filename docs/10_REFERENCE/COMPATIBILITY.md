# Compatibility Matrix

This table describes the declared compatibility of ETLantic 0.7.0.

| Surface | Supported range or version |
|---|---|
| Python | 3.11, 3.12, 3.13 |
| Pydantic | `>=2.12,<3` |
| ContractModel | `>=0.1.2` |
| DTCS toolkit | `>=0.11,<1` |
| DPCS toolkit | `>=0.13,<1` |
| Pipeline plan schema | `etlantic.plan/1` |
| Dataframe protocol | `etlantic.dataframe/1` |
| SQL protocol | `etlantic.sql/1` |
| Polars plugin | `etlantic-polars==0.7.0` |
| Pandas plugin | `etlantic-pandas==0.7.0` |
| SQL plugin | `etlantic-sql==0.7.0` |
| PySpark plugin | `etlantic-pyspark==0.7.0` |
| Package stability | Alpha |
| Plugin SDK stability | Protocol stable within 0.6; third-party SDK still evolving |

The package metadata in `pyproject.toml` is authoritative for dependency
ranges. During the 0.x series, public APIs and persistent formats may change.
Breaking changes must be called out in the changelog with an upgrade path.
