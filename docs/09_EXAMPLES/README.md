# Examples

## Green path

1. [Installation](../01_GETTING_STARTED/INSTALLATION.md) — `pip install etlantic`
2. [Quickstart](../01_GETTING_STARTED/QUICKSTART.md)
3. Runnable scripts below

Pages under **Design Studies** are aspirational and may show APIs that are not
shipped.

## Runnable guides (docs)

- [File-backed pipeline](../06_EXECUTION/FILE_STORAGE_TUTORIAL.md) — JSON and CSV
- [Polars](../06_EXECUTION/POLARS_TUTORIAL.md)
- [Pandas](../06_EXECUTION/PANDAS_TUTORIAL.md)
- [SQL](../06_EXECUTION/SQL_TUTORIAL.md)
- [PySpark](../06_EXECUTION/PYSPARK_TUTORIAL.md)
- [Airflow](../06_EXECUTION/AIRFLOW_TUTORIAL.md)
- [Airflow Compile](AIRFLOW_COMPILE.md) — `examples/airflow_compile.py`
- [SparkForge Adapter](SPARKFORGE_ADAPTER.md) — `tests/sparkforge/`

## Runnable scripts (repository `examples/`)

These scripts are exercised by CI. From a checkout:

### In-memory quickstart

```bash
uv run python examples/quickstart.py
```

### JSON and CSV storage

```bash
uv run python examples/file_storage.py
```

### Dataframe parity (Polars / Pandas)

```bash
uv sync --group dataframes
uv run python examples/dataframe_parity.py polars
uv run python examples/dataframe_parity.py pandas
```

### SQL to SQL

```bash
uv sync --group sql
uv run python examples/sql_to_sql.py
uv run python examples/sql_boundary_hybrid.py
uv run python examples/sql_transactional_write.py
uv run python examples/sql_failure_recovery.py
```

Defaults to in-memory SQLite for demos; set `ETLANTIC_SQL_URL` for
PostgreSQL.

### Local PySpark

```bash
uv sync --group pyspark
uv run python examples/pyspark_local.py
```

### Airflow compile

```bash
uv sync --group airflow
uv run python examples/airflow_compile.py
```

## Design studies (aspirational)

The remaining pages in this section explore intended integrations. Each page
opens with a Future design warning. They may contain APIs, packages, or
commands that go beyond the shipped surface — prefer the runnable guides and
`examples/` for installable behavior.

| Topic | Prefer instead |
|---|---|
| CSV and JSON through built-in storage | `examples/file_storage.py` |
| Pandas and Polars pipelines | `examples/dataframe_parity.py` |
| SQL execution and pushdown | `examples/sql_*.py` |
| PySpark batch | `examples/pyspark_local.py` |
| Airflow compilation | [Airflow Compile](AIRFLOW_COMPILE.md) |
| Graphviz DOT / HTML lineage | `etlantic.viz` / `etlantic viz` |
| SparkForge migration adapter | [SparkForge Adapter](SPARKFORGE_ADAPTER.md) |
| Structured Streaming | Experimental foundation only |
| Portable PySpark-style transformations | [Portable Transformation](PORTABLE_TRANSFORMATION.md) |

Do not use a design study as an installation or API reference. The
[capabilities page](../01_GETTING_STARTED/CAPABILITIES.md) and
[API reference](../10_REFERENCE/API_REFERENCE.md) define the current boundary.
