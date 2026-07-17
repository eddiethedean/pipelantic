# Installation

ETLantic 0.10.0 provides the typed modeling kernel, contract interoperability
(ODCS/DTCS/DPCS), multi-phase validation, profiles, deterministic planning,
a local runtime that executes plans with Python callables, in-memory
artifacts, and stdlib JSON/CSV bindings, plus optional Polars, Pandas, SQL,
PySpark, and Airflow plugins. Structured Streaming APIs are experimental.

## Requirements

- Python 3.11 or newer
- ContractModel as a companion package (installed automatically with ETLantic)

[uv](https://docs.astral.sh/uv/) is recommended for contributors and lockfile
workflows. Adopters can install with plain `pip`.

## User Installation

```bash
python3.11 -m pip install --upgrade pip
python3.11 -m pip install etlantic
```

Or with uv:

```bash
uv add etlantic
```

Verify the installed version matches these docs (0.10.0 or newer):

```bash
python -c "import etlantic; print(etlantic.__version__)"
```

### Optional engine plugins

Core never installs Polars, Pandas, database drivers, or PySpark. Add engines
explicitly:

```bash
pip install etlantic-polars    # Polars reference plugin
pip install etlantic-pandas    # Pandas compatibility plugin
pip install etlantic-sql       # PostgreSQL SQL reference plugin
pip install etlantic-pyspark   # PySpark reference plugin + local provider
pip install etlantic-airflow   # Airflow DAG compiler
pip install etlantic-keyring   # OS keyring secret provider
pip install etlantic-sqlmodel  # SQLModel bridge helpers
pip install etlantic-sparkforge  # SparkForge → ETLantic IR adapter
# or extras:
pip install 'etlantic[polars]'
pip install 'etlantic[pandas]'
pip install 'etlantic[dataframes]'
pip install 'etlantic[sql]'
pip install 'etlantic[pyspark]'
pip install 'etlantic[airflow]'
pip install 'etlantic[keyring]'
pip install 'etlantic[sqlmodel]'
pip install 'etlantic[sparkforge]'
```

For SQL, set a connection URL (PostgreSQL is the reference; SQLite is demo-only):

```bash
export ETLANTIC_SQL_URL=postgresql+psycopg://user:pass@localhost:5432/etlantic
# or for a local demo:
export ETLANTIC_SQL_URL=sqlite+pysqlite:///:memory:
```

Select SQL with `Profile(sql_engine="sql")`. The SQL reference plugin does not
implement `MERGE` (`sql_merge=False`).

Select Spark with `Profile(spark_engine="pyspark")` and
`@Transformation.implementation("pyspark")`. See
[Migration 0.6 → 0.7](../11_DEVELOPMENT/MIGRATION_0_6_TO_0_7.md).

Airflow compilation is available via `etlantic-airflow` (`compile_plan` /
`etlantic compile … --target airflow`). Dagster and Prefect remain future
plugins.

## Upgrade

```bash
python -m pip install --upgrade etlantic
# or
uv lock --upgrade-package etlantic
```

Review the
[changelog](https://github.com/eddiethedean/etlantic/blob/main/CHANGELOG.md)
and [Migration 0.6 → 0.7](../11_DEVELOPMENT/MIGRATION_0_6_TO_0_7.md) before
upgrading between 0.x releases because breaking changes remain possible.

## Development Setup

Contributors need [uv](https://docs.astral.sh/uv/):

```bash
git clone https://github.com/eddiethedean/etlantic.git
cd etlantic
uv sync
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

`uv sync` installs runtime dependencies, the editable package, and the `dev`
group (pytest, ruff, mkdocs). The lockfile `uv.lock` pins exact versions.

### Common commands

| Command | Purpose |
|---|---|
| `uv sync` | Create/update `.venv` from `uv.lock` |
| `uv sync --group dataframes` | Also install Polars and Pandas plugins |
| `uv sync --group pyspark` | Also install the PySpark plugin + sparkless (JVM-free tests) |
| `uv sync --group airflow` | Also install the Airflow orchestrator plugin |
| `uv sync --group sql` | Also install the SQL plugin |
| `uv lock` | Refresh the lockfile after dependency changes |
| `uv run pytest` | Run tests |
| `uv run pytest tests/spark` | Run Spark suite (uses sparkless by default) |
| `uv run pytest tests/airflow` | Run Airflow compile suite |
| `uv run ruff check .` | Lint |
| `uv run ruff format .` | Format |
| `uv run python scripts/check_docs.py` | Docs consistency gate |
| `NO_MKDOCS_2_WARNING=1 uv run mkdocs build --strict` | Build the documentation site |

## Repository Layout

```text
pyproject.toml
uv.lock
.python-version
src/etlantic/
packages/etlantic-polars/
packages/etlantic-pandas/
packages/etlantic-sql/
packages/etlantic-pyspark/
packages/etlantic-airflow/
tests/
examples/
docs/
```

## Installation Problems

See [Troubleshooting](TROUBLESHOOTING.md) for Python-version errors, version
mismatches with the docs, missing plugins, stale virtual environments, and
unsupported backend examples.

## Dependency Philosophy

ETLantic keeps the core install small. Dataframe engines, SQL drivers,
orchestrators, and storage clients belong in optional plugins—not the base
package.

See [Dependency Strategy](../11_DEVELOPMENT/DEPENDENCY_STRATEGY.md) for the
full dependency policy.

## Next Step

Continue with [Capabilities](CAPABILITIES.md), then
[Quickstart](QUICKSTART.md).
