# 5–10 Minute Quickstart

> **Status: Available in ETLantic 0.18.0.** The path below is
> production/stable within the documented single-tenant reference deployment
> boundary. See [Capabilities](CAPABILITIES.md) for that boundary.

In one file, you will validate, plan, and run a typed pipeline using core
ETLantic and in-memory storage.

## 1. Install

ETLantic requires Python 3.11 or newer.

```bash
python -m pip install 'etlantic==0.18.0'
python -m etlantic --version
```

Repository contributors should use the separate checkout flow in
[Installation](INSTALLATION.md).

## 2. Create `pipeline.py`

Copy this complete file:

```python
from etlantic import (
    Data,
    Extract,
    Input,
    Load,
    Output,
    Pipeline,
    PipelineRuntime,
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


@NormalizeCustomers.implementation("local")
def normalize_customers(customers: list[RawCustomer]) -> list[Customer]:
    return [
        Customer(
            customer_id=customer.customer_id,
            full_name=f"{customer.first_name} {customer.last_name}",
        )
        for customer in customers
    ]


class CustomerPipeline(Pipeline):
    raw: Extract[RawCustomer] = Extract(asset="customer_source")
    normalized = NormalizeCustomers.step(customers=raw)
    curated: Load[Customer] = Load(
        input=normalized.result,
        asset="customer_sink",
    )


def main() -> None:
    validation = CustomerPipeline.validate(profile="development")
    validation.raise_for_errors()
    CustomerPipeline.plan(profile="development")

    runtime = PipelineRuntime()
    runtime.memory.seed(
        "customer_source",
        [
            RawCustomer(customer_id=1, first_name="Ada", last_name="Lovelace"),
            RawCustomer(customer_id=2, first_name="Grace", last_name="Hopper"),
        ],
    )

    report = CustomerPipeline.run(profile="development", runtime=runtime)
    print(report.status.value)
    for customer in runtime.memory.get("customer_sink"):
        print(customer.model_dump())


if __name__ == "__main__":
    main()
```

The module-level definitions let the CLI import the pipeline later. The main
guard prevents imports from seeding or running it.

## 3. Run

```bash
python pipeline.py
```

Expected output:

```text
succeeded
{'customer_id': 1, 'full_name': 'Ada Lovelace'}
{'customer_id': 2, 'full_name': 'Grace Hopper'}
```

You have now checked the graph before processing data, produced a deterministic
secret-free plan, and executed the selected local implementation.

The repository companion is `examples/quickstart.py`.

## Next

Continue with [Your First Pipeline](FIRST_PIPELINE.md) for CLI
`inspect`/`validate`/`plan`, an intentional broken-wiring diagnostic, generated
contracts, and durable-storage guidance.
