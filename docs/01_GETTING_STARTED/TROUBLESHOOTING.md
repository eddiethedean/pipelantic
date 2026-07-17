# Troubleshooting

## `pip install etlantic` rejects my Python version

ETLantic requires Python 3.11 or newer. Check with:

```bash
python --version
```

## Installed version is older than the docs

These docs describe ETLantic **0.10.0**. Confirm what you installed:

```bash
python -c "import etlantic; print(etlantic.__version__)"
```

If the version is older, upgrade:

```bash
python -m pip install --upgrade 'etlantic>=0.7.0'
```

If pip still resolves an older release, you may be on a mirror or pin. Check
`pip index versions etlantic` (or visit
[PyPI](https://pypi.org/project/etlantic/)) and clear conflicting constraints
in your environment.

## `pip install etlantic-polars` / `etlantic-pandas` / `etlantic-sql` / `etlantic-pyspark` fails

Those packages ship with ETLantic 0.10.0. They are separate distributions:

```bash
python -m pip install --upgrade etlantic-polars
python -m pip install --upgrade etlantic-pandas
python -m pip install --upgrade etlantic-sql
python -m pip install --upgrade etlantic-pyspark
```

If pip reports no matching distribution:

1. Confirm core is already at 0.10.0 or newer.
2. Confirm Python is 3.11+.
3. Confirm the package name uses a hyphen (`etlantic-pyspark`), not an
   underscore.

From a git checkout, install optional groups with
`uv sync --group dataframes` / `--group sql` / `--group pyspark` /
`--group airflow` / `--group sparkforge` as needed.

## A transformation has no implementation

Declaring a `Transformation` defines its contract, not its executable code.
Register a local implementation before running:

```python
@MyTransformation.implementation("local")
def run_locally(rows):
    return rows
```

## My memory source returns no records

Seed the exact binding name used by the pipeline:

```python
runtime.memory.seed("customer_source", records)
```

Read sink output using its binding:

```python
runtime.memory.get("customer_sink")
```

## Planning and execution use different profiles

Use `local` for plan-oriented examples or `development` for the built-in local
runtime examples. Do not silently switch profile names within one workflow.

## A Pandas, Polars, SQL, Spark, or Airflow example fails

Install the matching plugin (`etlantic-polars`, `etlantic-pandas`,
`etlantic-sql`, or `etlantic-pyspark`) and set the corresponding profile engine
(`dataframe_engine`, `sql_engine`, or `spark_engine`). Airflow compilation
remains design material for later milestones. Start with the runnable
examples under `examples/` (including `examples/pyspark_local.py` and
`examples/sql_to_sql.py`).

## Commands in a design page do not exist

The current CLI supports `validate`, `inspect`, `plan`, `plan explain`, `run`,
and `report show|export`. See the [CLI reference](../10_REFERENCE/CLI.md).

## A virtual environment breaks after moving the repository

Virtual-environment entry points contain absolute paths. Delete and recreate
the environment after moving or renaming a checkout:

```bash
rm -rf .venv
uv sync --locked
```

Only run the removal command from the repository root after confirming
`.venv` is the project environment.

## Where to report a problem

Include the ETLantic version, Python version, command, complete traceback or
diagnostic code, and a minimal pipeline definition in the issue report. Never
include credentials or production data.
