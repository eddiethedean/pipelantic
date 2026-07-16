# Getting Started

Welcome to PipelineModel!

> **Project status:** PipelineModel is currently design-first and
> pre-implementation. The examples in this section define the intended
> developer experience. See
> [Documentation Status](../02_FOUNDATIONS/DOCUMENTATION_STATUS.md).

This section is designed to get you productive as quickly as possible.
Rather than starting with implementation details, you'll learn the core
ideas that make PipelineModel different from traditional ETL frameworks.

## What You'll Learn

By the end of this guide you will be able to:

-   Install PipelineModel
-   Define typed data contracts
-   Define typed transformations
-   Wire transformations into pipelines
-   Validate your pipeline before execution
-   Generate portable contract specifications
-   Execute the pipeline using the runtime of your choice

## Prerequisites

You should be comfortable with:

-   Python 3.11+
-   Basic type annotations
-   Pydantic models
-   ETL concepts

No prior experience with orchestration frameworks is required.

## Documentation Roadmap

Read the Getting Started section in this order:

1. [Installation](INSTALLATION.md)
2. [Quickstart](QUICKSTART.md)
3. [Your First Pipeline](FIRST_PIPELINE.md)
4. [Project Structure](PROJECT_STRUCTURE.md)
5. [FAQ](FAQ.md)

## The PipelineModel Mental Model

PipelineModel separates **modeling** from **execution**.

You describe *what* the pipeline is:

-   Data Contracts
-   Transformation Contracts
-   Pipeline Contracts

PipelineModel validates and plans the pipeline.

Execution is then delegated to the libraries and orchestrators you
choose.

``` text
Python Classes
      │
      ▼
ODCS + DTCS + DPCS
      │
      ▼
Pipeline Validation
      │
      ▼
Execution Planning
      │
      ▼
Execution Plugins
(Pandas, Polars, Airflow, ...)
```

## A Preview

``` python
from contractmodel import DataContractModel
from pipelinemodel import Pipeline, Transformation, Input, Output

class Customer(DataContractModel):
    id: int
    name: str

class NormalizeCustomers(Transformation):
    customers: Input[Customer]
    result: Output[Customer]

class CustomerPipeline(Pipeline):
    ...
```

This should feel familiar if you've used FastAPI: Python type
annotations are the source of truth.

## Philosophy

PipelineModel is built around a few core ideas:

-   Types describe interfaces.
-   Contracts are generated from code.
-   Pipelines model intent, not execution.
-   Validation happens before execution.
-   Execution engines are replaceable.

## Next Step

Continue with [Installation](INSTALLATION.md) to review the intended package
layout and development installation workflow.
