# Project Structure

A well-organized Pipelantic project separates **modeling** from
**execution**. Your Python classes define contracts and pipelines, while
runtime configuration and generated artifacts remain outside your source
code.

## Recommended Layout

``` text
customer-pipeline/
│
├── pyproject.toml
├── README.md
│
├── src/
│   └── customer_pipeline/
│       ├── __init__.py
│       │
│       ├── contracts/
│       │   ├── customers.py
│       │   ├── orders.py
│       │   └── products.py
│       │
│       ├── transformations/
│       │   ├── normalize_customers.py
│       │   ├── calculate_metrics.py
│       │   └── enrich_orders.py
│       │
│       ├── implementations/
│       │   ├── local/
│       │   ├── polars/          # optional (0.5+)
│       │   ├── pandas/          # optional (0.5+)
│       │   ├── sql/             # optional (0.6+)
│       │   # spark/             # future — do not require yet
│       │
│       ├── pipelines/
│       │   ├── customer_pipeline.py
│       │   └── analytics_pipeline.py
│       │
│       ├── profiles/
│       │   ├── local.py
│       │   ├── development.py
│       │   └── production.py
│       │
│       └── resources/
│           ├── databases.py
│           └── storage.py
│
├── contracts/
│   ├── data/
│   ├── transformations/
│   └── pipelines/
│
├── tests/
│
└── docs/
```

## Source Code

### contracts/

Contains `Data` contract models (`Data` remains as a deprecated
alias).

``` python
class Customer(Data):
    ...
```

These classes define your business data and generate ODCS contracts.

### transformations/

Contains transformation contract definitions.

``` python
class NormalizeCustomers(Transformation):
    ...
```

These classes define interfaces, not implementations.

### implementations/

Contains runtime-specific implementations.

Example:

- Local Python (`"local"`)
- Polars / Pandas (optional plugins in 0.5+)
- SQL (`"sql"` via `pipelantic-sql` and `Profile.sql_engine` in 0.6+)
- Spark / remote (future)

A single transformation contract may have multiple implementations.

### pipelines/

Contains Pipelantic pipeline definitions.

``` python
class CustomerPipeline(Pipeline):
    ...
```

These classes wire contracts and transformations together.

### profiles/

Profiles describe runtime bindings.

Examples:

-   local development
-   CI
-   production
-   cloud

The pipeline itself remains unchanged.

### resources/

Reusable runtime resources.

Examples include:

-   database connections
-   object storage
-   API clients
-   credentials
-   dependency providers

## Generated Contracts

The `contracts/` directory contains generated specifications.

``` text
contracts/
├── data/
├── transformations/
└── pipelines/
```

These artifacts should generally be committed to version control so they
can be reviewed, shared, and validated independently of Python source
code.

## Tests

Recommended layout:

``` text
tests/
├── contracts/
├── transformations/
├── pipelines/
├── implementations/
└── integration/
```

Separate contract validation from execution testing whenever possible.

## Documentation

Keep project-specific documentation in a local `docs/` directory.

Pipelantic itself has its own documentation, while each project
documents business-specific pipelines, assumptions, and operational
guidance.

## Design Principles

A Pipelantic project should follow these principles:

-   Data contracts are isolated from execution code.
-   Transformations define interfaces before implementations.
-   Execution engines remain interchangeable.
-   Pipelines model logical data flow.
-   Runtime configuration is separated into profiles.
-   Generated contracts are treated as first-class artifacts.

## Why This Structure?

This organization keeps business logic, contracts, runtime bindings, and
generated artifacts independent.

As projects grow, teams can evolve execution strategies without changing
pipeline definitions, or extend pipeline models without rewriting
existing implementations.

## Next Step

Continue with **FAQ.md** for answers to common questions about
Pipelantic's architecture and philosophy.
