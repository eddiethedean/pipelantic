# DTCS

## Overview

PipelineModel adopts the **Data Transformation Contract Standard (DTCS)** as the
canonical portable representation of transformation contracts.

DTCS defines **what a transformation means**. PipelineModel provides the
Python-first authoring experience and generates DTCS artifacts from typed
transformation classes.

The DTCS specification is the normative definition of transformation semantics.
This document explains how PipelineModel integrates with that specification.

---

## Why PipelineModel Uses DTCS

Transformation logic should be portable.

Developers should define a transformation once and reuse it across different
execution engines without changing its logical interface.

DTCS provides a vendor-neutral representation of:

- inputs
- outputs
- parameters
- metadata
- transformation identity
- compatibility information

PipelineModel treats DTCS as the portable artifact for transformation
definitions.

---

## Architectural Relationship

```text
Python Transformation
        │
        ▼
Transformation
        │
        ▼
PipelineModel
        │
        ▼
DTCS Artifact
        │
        ▼
Execution Planning
```

PipelineModel owns the Python API.

DTCS owns the portable transformation representation.

---

## Code-First Workflow

Developers author transformations in Python.

```python
class NormalizeCustomers(Transformation):
    customers: Input[RawCustomer]
    minimum_age: Parameter[int] = 18
    result: Output[Customer]
```

PipelineModel generates the corresponding DTCS artifact.

In a code-first project, the Python class remains the authoring source of
truth.

---

## Contract-First Workflow

PipelineModel may load existing DTCS artifacts and reconstruct transformation
definitions through its public loading APIs.

Whether authored in Python or imported from DTCS, transformations participate
in planning and validation the same way.

---

## Generated DTCS Artifacts

A transformation may generate:

```text
contracts/
└── transformations/
    └── normalize-customers.dtcs.yaml
```

Generated artifacts should be deterministic so they can be reviewed in version
control and reproduced in CI.

---

## Validation

PipelineModel validates transformation contracts before execution.

Examples include:

- input compatibility
- output compatibility
- parameter types
- implementation signatures
- required metadata
- DTCS version compatibility

Planning should fail before execution when required DTCS semantics cannot be
satisfied.

---

## Identity and Versioning

Every published transformation should expose a stable identity.

Typical metadata includes:

- identifier
- version
- description
- owner
- tags

Compatibility decisions should follow the DTCS specification and PipelineModel's
planning rules.

---

## Relationship to Implementations

DTCS describes the logical transformation.

Execution implementations remain separate.

```python
@NormalizeCustomers.implementation("polars")
def normalize(...):
    ...
```

```python
@NormalizeCustomers.implementation("pandas")
def normalize(...):
    ...
```

Multiple implementations may satisfy the same DTCS contract.

---

## Relationship to ODCS and DPCS

The three standards complement one another.

```text
ODCS
  Data Contracts
      │
      ▼
DTCS
  Transformation Contracts
      │
      ▼
DPCS
  Pipeline Contracts
```

PipelineModel unifies these standards through strongly typed Python models.

---

## Design Principles

PipelineModel follows these principles when integrating with DTCS:

- Python classes are the preferred authoring interface.
- DTCS is the portable artifact.
- Types define transformation interfaces.
- Implementations are interchangeable.
- Planning precedes execution.
- Generated artifacts are deterministic.

---

## Further Reading

For the normative definition of DTCS, refer to the
[DTCS 1.0 Specification](../specifications/DTCS_SPEC.md).

This document describes **how PipelineModel integrates with DTCS**, not the DTCS
specification itself.
