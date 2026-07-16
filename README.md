# PipelineModel

Typed, contract-driven data pipeline modeling for Python.

> Define data, transformations, and pipelines with typed Python classes.
> Validate and plan them once. Execute them through interchangeable backends.

## Status

**0.1.0 — Typed Modeling Kernel**

PipelineModel currently provides the authoring model, logical graph construction,
topology and compatibility diagnostics, graph inspection, and Mermaid output.
Planning, execution plugins, and contract serialization arrive in later
milestones.

See [docs/](docs/README.md) for the full design and [Roadmap](docs/11_DEVELOPMENT/ROADMAP.md)
for sequencing.

## Install

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run pytest
uv run ruff check .
uv run ruff format .
```

`uv sync` creates `.venv`, installs the package in editable mode, and installs
the `dev` dependency group (pytest, ruff) by default.

## Quick example

```python
from contractmodel import ContractModel as DataContractModel
from pipelinemodel import Input, Output, Pipeline, Sink, Source, Transformation


class RawCustomer(DataContractModel):
    customer_id: int
    first_name: str
    last_name: str


class Customer(DataContractModel):
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

- [Getting Started](docs/01_GETTING_STARTED/README.md)
- [Core Concepts](docs/02_FOUNDATIONS/CORE_CONCEPTS.md)
- [Architecture](docs/02_FOUNDATIONS/ARCHITECTURE.md)
- [Roadmap](docs/11_DEVELOPMENT/ROADMAP.md)

## License

MIT
