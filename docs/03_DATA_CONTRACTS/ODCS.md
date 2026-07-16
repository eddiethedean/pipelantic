# ODCS Integration

## Overview

PipelineModel adopts the **Open Data Contract Standard (ODCS)** as its canonical portable representation for data contracts.

PipelineModel does **not** redefine the ODCS specification.

Instead, it provides a Python-first authoring experience built on **ContractModel**, which generates and consumes ODCS documents.

The authoritative ODCS specification is maintained by the Open Data Contract Standard project.

---

## Why PipelineModel Uses ODCS

Data contracts should be portable.

A pipeline should not depend on a single programming language or execution engine to describe its datasets.

ODCS provides a common, implementation-independent representation that can be:

- version controlled
- reviewed
- exchanged between organizations
- consumed by governance tools
- referenced by pipelines

PipelineModel therefore treats ODCS as the canonical artifact for published data contracts.

---

## Architectural Relationship

PipelineModel intentionally separates responsibilities.

```text
Python Authoring
        │
        ▼
DataContractModel
        │
        ▼
ContractModel
        │
        ▼
ODCS Document
        │
        ▼
PipelineModel
```

Each layer has a different purpose.

| Component | Responsibility |
|-----------|----------------|
| Pydantic | Python data modeling |
| ContractModel | Operationalizes data contracts |
| ODCS | Portable contract representation |
| PipelineModel | Uses contracts to model pipelines |

---

## Code-First Workflow

PipelineModel recommends a code-first workflow.

```python
from contractmodel import DataContractModel

class Customer(DataContractModel):
    customer_id: int
    email: str
```

ContractModel generates the ODCS document.

```python
Customer.write_odcs(
    "contracts/data/customer.odcs.yaml",
)
```

In a code-first project, the Python class remains the authoring source of
truth.

---

## Contract-First Workflow

Existing ODCS contracts may also be loaded.

```python
Customer = DataContractModel.from_odcs(
    "contracts/data/customer.odcs.yaml",
)
```

The resulting class behaves like any authored `DataContractModel` and can be referenced throughout PipelineModel.

---

## Hybrid Workflow

Many organizations already maintain published ODCS contracts.

PipelineModel supports combining both approaches.

```text
Existing ODCS
        │
        ▼
ContractModel
        │
        ▼
PipelineModel

Python Authored Models
        │
        ▼
ContractModel
        │
        ▼
ODCS
```

Both become equivalent pipeline types.

---

## Referencing ODCS from Pipelines

PipelineModel never references YAML directly.

Instead, transformations and pipelines reference Python contract classes.

```python
class NormalizeCustomers(Transformation):
    customers: Input[RawCustomer]
    result: Output[Customer]
```

Those classes carry the metadata needed to identify the corresponding ODCS artifacts.

---

## Contract Generation

PipelineModel can discover every referenced contract.

```python
CustomerPipeline.write_contracts(
    "contracts/",
)
```

Example output:

```text
contracts/
├── data/
│   ├── raw-customer.odcs.yaml
│   └── customer.odcs.yaml
├── transformations/
│   └── normalize-customers.dtcs.yaml
└── pipelines/
    └── customer-pipeline.dpcs.yaml
```

Generated ODCS documents should be deterministic so they can be reviewed in version control.

---

## Contract Identity

PipelineModel relies on ContractModel to expose stable contract identity.

Conceptually, every contract provides:

- identifier
- version
- specification version
- metadata
- schema
- compatibility information

PipelineModel uses this information for validation, documentation, lineage, and bundle generation.

---

## Validation

PipelineModel coordinates validation.

ContractModel validates data against ODCS-backed contracts.

Execution plugins may optimize validation using native capabilities such as:

- Polars expressions
- Pandas vectorized operations
- SQL constraints
- Arrow schemas

When native validation is unavailable, plugins may fall back to ContractModel validation.

---

## Supported ODCS Features

PipelineModel intends to support every feature that can be represented faithfully through ContractModel.

Examples include:

- schema definitions
- field metadata
- required fields
- nullability
- descriptions
- ownership metadata
- version information
- compatibility metadata

Support ultimately depends on ContractModel's public API.

---

## Extensions

ODCS may evolve over time.

PipelineModel should preserve unknown or extension metadata whenever practical rather than discarding it.

This allows organizations to use organization-specific ODCS extensions without breaking PipelineModel.

---

## Version Compatibility

PipelineModel should clearly document:

- supported ODCS versions
- deprecated versions
- compatibility guarantees
- migration guidance

Compatibility decisions belong to ContractModel's ODCS implementation.

PipelineModel consumes those decisions.

---

## Design Principles

PipelineModel follows these principles when integrating with ODCS:

- Python classes are the preferred authoring experience.
- ODCS is the preferred portable artifact.
- ContractModel owns ODCS semantics.
- PipelineModel never duplicates the ODCS specification.
- PipelineModel references contract classes rather than YAML.
- Generated artifacts should be deterministic.
- Unknown ODCS extensions should be preserved whenever practical.

---

## Relationship to DTCS and DPCS

ODCS describes **data**.

DTCS describes **transformations**.

DPCS describes **pipelines**.

Together they provide a portable description of an entire ETL system.

```text
ODCS
    ↓
DTCS
    ↓
DPCS
```

PipelineModel unifies all three through typed Python models.

---

## Further Reading

For the normative definition of ODCS, refer to the official Open Data Contract Standard specification maintained by the upstream project.

This document describes **how PipelineModel integrates with ODCS**, not the ODCS specification itself.
