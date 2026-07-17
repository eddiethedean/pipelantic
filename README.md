![ETLantic banner](https://raw.githubusercontent.com/eddiethedean/etlantic/main/docs/theme/assets/etlantic-banner.png)

# ETLantic

[![Documentation Status](https://readthedocs.org/projects/etlantic/badge/?version=latest)](https://etlantic.readthedocs.io/en/latest/?badge=latest)

Catch incompatible data-pipeline wiring before you process data.

Define datasets, transformations, and pipelines as typed Python classes.
Validate and plan them once. Run locally today; swap Polars, Pandas, or SQL
backends without rewriting the logical pipeline.

**Status:** Alpha **0.10.0** — local runtime + optional
Polars/Pandas/SQL/PySpark/Airflow plugins. Structured Streaming is
experimental.

## Install

Requires Python 3.11 or newer.

```bash
pip install etlantic
# optional engines / compilers
pip install etlantic-polars
pip install etlantic-pandas
pip install etlantic-sql
pip install etlantic-pyspark
pip install etlantic-airflow
```

Verify:

```bash
python -c "import etlantic; print(etlantic.__version__)"
```

### Development

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run pytest
uv run ruff check .
uv run ruff format .
```

`uv sync` creates `.venv`, installs the package in editable mode, and installs
the `dev` dependency group (pytest, ruff, mkdocs) by default.

## Release

Tag a version that matches `src/etlantic/_version.py`, then push the tag:

```bash
git tag v0.6.1
git push origin v0.6.1
```

GitHub Actions runs checks and publishes to PyPI using the `PYPI_API_TOKEN`
repository secret.

## Quick example

```python
from etlantic import (
    Data,
    Input,
    Output,
    Pipeline,
    PipelineRuntime,
    Sink,
    Source,
    Transformation,
)


class RawCustomer(Data):
    customer_id: int
    first_name: str
    last_name: str


class Customer(Data):
    customer_id: int
    full_name: str


class NormalizeCustomers(Transformation):
    customers: Input[RawCustomer]
    result: Output[Customer]


class CustomerPipeline(Pipeline):
    raw: Source[RawCustomer] = Source(binding="customer_source")
    normalized = NormalizeCustomers.step(customers=raw)
    curated: Sink[Customer] = Sink(
        input=normalized.result,
        binding="customer_sink",
    )


@NormalizeCustomers.implementation("local")
def normalize(customers: list[RawCustomer]) -> list[Customer]:
    return [
        Customer(
            customer_id=row.customer_id,
            full_name=f"{row.first_name} {row.last_name}",
        )
        for row in customers
    ]


CustomerPipeline.validate(profile="development").raise_for_errors()

runtime = PipelineRuntime()
runtime.memory.seed(
    "customer_source",
    [RawCustomer(customer_id=1, first_name="Ada", last_name="Lovelace")],
)
run_report = CustomerPipeline.run(profile="development", runtime=runtime)
print(runtime.memory.get("customer_sink"))
```

Run the complete tested version at
[examples/quickstart.py](examples/quickstart.py).

## Current capability boundary

| Capability | 0.10 |
|---|---|
| Typed modeling, validation, contracts, and planning | Available |
| Local Python execution and run reports | Available |
| Memory, callable, JSON, CSV, and no-write storage | Available |
| Polars and Pandas dataframe plugins | Available (`etlantic-polars` / `etlantic-pandas`) |
| SQL plugin | Available (`etlantic-sql`) |
| PySpark plugin + local provider | Available (`etlantic-pyspark`) |
| Structured Streaming | Experimental |
| Airflow orchestrator compiler | Available (`etlantic-airflow`) |
| CLI compile / generate / schema / SARIF | Available |
| Plugin allowlists / keyring / SQLModel extras | Available |
| SparkForge migration adapter | Available (`etlantic-sparkforge`) |

## Documentation

- [Documentation site](https://etlantic.readthedocs.io/)
- [Getting Started](docs/01_GETTING_STARTED/README.md)
- [Capabilities and Limitations](docs/01_GETTING_STARTED/CAPABILITIES.md)
- [Evaluator brief](docs/01_GETTING_STARTED/EVALUATOR.md)
- [Core Concepts](docs/02_FOUNDATIONS/CORE_CONCEPTS.md)
- [Architecture](docs/02_FOUNDATIONS/ARCHITECTURE.md)
- [Roadmap](docs/11_DEVELOPMENT/ROADMAP.md)

## License

MIT
