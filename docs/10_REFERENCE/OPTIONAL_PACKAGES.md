# Optional Packages

> **Status: Available in ETLantic 0.16.0.** Core `etlantic` does not install
> engines. Install only the plugins you need, pinned to the same minor line.

## Install pins

Prefer exact pins for a controlled pilot:

```bash
pip install 'etlantic==0.16.0'
pip install 'etlantic-polars==0.16.0'
pip install 'etlantic-pandas==0.16.0'
pip install 'etlantic-sql==0.16.0'
pip install 'etlantic-pyspark==0.16.0'
pip install 'etlantic-airflow==0.16.0'
pip install 'etlantic-prefect==0.16.0'
pip install 'etlantic-keyring==0.16.0'
pip install 'etlantic-sqlmodel==0.16.0'
pip install 'etlantic-sparkforge==0.16.0'
```

Official plugin packages declare `etlantic>=0.16.0,<0.17` so they stay on the
0.16 line. Cross-minor mixing is unsupported unless a future release documents
compatibility tests.

## Package surfaces

| Package | Public entry | Role |
|---|---|---|
| `etlantic-polars` | `etlantic_polars` | Polars dataframe engine + portable compiler |
| `etlantic-pandas` | `etlantic_pandas` | Pandas dataframe engine + eager portable compiler |
| `etlantic-sql` | `etlantic_sql` | Native SQL (PostgreSQL) engine |
| `etlantic-pyspark` | `etlantic_pyspark` | PySpark engine + portable compiler |
| `etlantic-airflow` | `etlantic_airflow` | Airflow DAG compiler (`etlantic compile --target airflow`) |
| `etlantic-prefect` | `etlantic_prefect` | Prefect direct-execution scheduler (`Profile(orchestrator="prefect")`) |
| `etlantic-keyring` | `etlantic_keyring` | OS keyring secret provider |
| `etlantic-sqlmodel` | `etlantic_sqlmodel` | SQLModel ↔ contract bridge |
| `etlantic-sparkforge` | `etlantic_sparkforge` | SparkForge adapter (medallion stays here, not in core) |

MkDocs API generation scans core `src/` only. For optional-package constructors,
registration, and failure modes, use the package READMEs under
[`packages/`](https://github.com/eddiethedean/etlantic/tree/main/packages)
and the engine tutorials.

## Related

- [Compatibility](COMPATIBILITY.md)
- [Portable compiler matrix](PORTABLE_COMPILER_MATRIX.md)
- [Capabilities](../01_GETTING_STARTED/CAPABILITIES.md)
- [Third-party compiler tutorial](../07_PLUGIN_SDK/THIRD_PARTY_COMPILER_TUTORIAL.md)
