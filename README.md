![Pipelantic banner](https://raw.githubusercontent.com/eddiethedean/pipelantic/main/docs/theme/assets/pipelantic-banner.png)

# Pipelantic

[![Documentation Status](https://readthedocs.org/projects/pipelantic/badge/?version=latest)](https://pipelantic.readthedocs.io/en/latest/?badge=latest)

Typed, contract-driven data pipeline modeling for Python.

> Define data, transformations, and pipelines with typed Python classes.
> Validate and plan them once. Execute them through interchangeable backends.

## Status

**0.3.0 — Validation and Pipeline Plan IR**

Pipelantic provides the typed modeling kernel, contract interoperability, and
an immutable secret-free `PipelinePlan`. Planning is pure (no secret
resolution or execution). Local runtime arrives in later milestones.

See the [hosted documentation](https://pipelantic.readthedocs.io/) for the
full design,
[CHANGELOG.md](CHANGELOG.md) for release notes, and
[Roadmap](docs/11_DEVELOPMENT/ROADMAP.md) for sequencing.

## Install

```bash
pip install pipelantic
# or
uv add pipelantic
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

Tag a version that matches `src/pipelantic/_version.py`, then push the tag:

```bash
git tag v0.3.0
git push origin v0.3.0
```

GitHub Actions runs checks and publishes to PyPI using the `PYPI_API_TOKEN`
repository secret.

## Quick example

```python
from pipelantic import Data, Input, Output, Pipeline, Sink, Source, Transformation


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


graph = CustomerPipeline.inspect()
report = CustomerPipeline.validate()
print(CustomerPipeline.to_mermaid())
```

## Documentation

- [Documentation site](https://pipelantic.readthedocs.io/)
- [Getting Started](docs/01_GETTING_STARTED/README.md)
- [Core Concepts](docs/02_FOUNDATIONS/CORE_CONCEPTS.md)
- [Architecture](docs/02_FOUNDATIONS/ARCHITECTURE.md)
- [Roadmap](docs/11_DEVELOPMENT/ROADMAP.md)

## License

MIT
