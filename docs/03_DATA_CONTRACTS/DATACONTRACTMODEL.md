# DataContractModel

`DataContractModel` is the typed foundation of PipelineModel's data layer.

It is provided by ContractModel and extends Pydantic's modeling experience so a single Python class can serve as:

- a validated Python data model
- a data contract definition
- an ODCS-compatible schema source
- a typed pipeline interface
- a source for generated documentation and contract artifacts

PipelineModel consumes `DataContractModel` classes directly. It does not redefine them.

## Basic Definition

```python
from contractmodel import DataContractModel


class Customer(DataContractModel):
    customer_id: int
    first_name: str
    last_name: str
    email: str | None = None
```

This class can validate ordinary Python data:

```python
customer = Customer(
    customer_id=42,
    first_name="Ada",
    last_name="Lovelace",
)
```

It can also be referenced by PipelineModel:

```python
from pipelinemodel import Input, Output, Transformation


class NormalizeCustomers(Transformation):
    customers: Input[Customer]
    result: Output[Customer]
```

The same class participates in runtime validation, contract generation, and pipeline type checking.

## Why PipelineModel Uses ContractModel

PipelineModel should not implement a second data-modeling system.

ContractModel already owns the concerns specific to data contracts:

- Pydantic model behavior
- field validation
- schema constraints
- ODCS metadata
- contract generation
- contract loading
- runtime data validation
- compatibility analysis
- data-contract-specific diagnostics

PipelineModel uses these capabilities to understand what data may enter or leave a pipeline node.

The architectural boundary is:

```text
ContractModel
    Defines and operationalizes data contracts

PipelineModel
    Connects data contracts through typed transformations and pipelines
```

## Pydantic Compatibility

A `DataContractModel` should preserve the normal Pydantic developer experience.

Users should be able to use:

- standard Python type annotations
- `Annotated`
- `Field`
- aliases
- defaults
- optional fields
- nested models
- enums
- validators
- model configuration
- serialization
- JSON Schema generation

Example:

```python
from typing import Annotated

from pydantic import Field

from contractmodel import DataContractModel


class Customer(DataContractModel):
    customer_id: Annotated[
        int,
        Field(
            gt=0,
            description="Stable customer identifier",
        ),
    ]

    email: Annotated[
        str,
        Field(
            description="Primary customer email address",
        ),
    ]

    age: Annotated[
        int | None,
        Field(
            ge=0,
            le=130,
        ),
    ] = None
```

PipelineModel should reuse this metadata rather than requiring equivalent declarations elsewhere.

## Contract Metadata

Data contracts require metadata beyond individual fields.

ContractModel should provide a class-level configuration surface for values such as:

- contract name
- contract version
- description
- owner
- domain
- status
- tags
- logical type
- ODCS specification version

A possible authoring style is:

```python
from contractmodel import ContractConfig, DataContractModel


class Customer(DataContractModel):
    customer_id: int
    email: str

    contract_config = ContractConfig(
        name="customer",
        version="1.0.0",
        description="Canonical customer record.",
        owner="customer-data-team",
        tags={"customer", "curated"},
    )
```

The final ContractModel API may use a different configuration name or structure. PipelineModel should consume the public ContractModel metadata API rather than depending on private implementation details.

## Inheritance

Data-contract inheritance may be useful for sharing common fields:

```python
from datetime import datetime


class AuditedRecord(DataContractModel):
    created_at: datetime
    updated_at: datetime


class Customer(AuditedRecord):
    customer_id: int
    email: str
```

Inheritance should remain ordinary Pydantic inheritance.

However, contract identity and version metadata must be explicit for each concrete published contract. PipelineModel should not guess whether a subclass represents a new contract, a new contract version, or an internal reusable model.

## Nested Models

Nested Pydantic models should be supported when ContractModel can map them reliably into ODCS.

```python
class Address(DataContractModel):
    street: str
    city: str
    postal_code: str


class Customer(DataContractModel):
    customer_id: int
    address: Address
```

PipelineModel should treat `Customer` as the pipeline-level data contract. Nested contract behavior remains a ContractModel concern.

## Collections

Standard collection annotations may describe repeated values:

```python
class Order(DataContractModel):
    order_id: int
    item_ids: list[int]
    labels: set[str] = set()
```

These field-level collections are different from transformation cardinality.

For example:

```python
class CombineCustomers(Transformation):
    customers: Input[list[Customer]]
    result: Output[Customer]
```

Here, `list[Customer]` describes multiple pipeline inputs or partitions rather than a field inside one customer record.

## Optional Fields

Use ordinary Python typing:

```python
class Customer(DataContractModel):
    customer_id: int
    email: str | None = None
```

PipelineModel should rely on ContractModel and Pydantic to determine whether a field is required, nullable, or has a default.

It should not reinterpret Pydantic's field semantics.

## Strict Types and Constraints

Projects may choose strict validation:

```python
from typing import Annotated

from pydantic import Field


class Customer(DataContractModel):
    customer_id: Annotated[
        int,
        Field(strict=True, gt=0),
    ]
```

This metadata should flow into:

- runtime validation
- ODCS generation
- documentation
- compatibility analysis
- engine-specific validation plugins where supported

Execution plugins may not support every Pydantic constraint natively. They must report unsupported capabilities rather than silently ignoring declared requirements.

## Aliases

Aliases may map external field names to Python-friendly identifiers:

```python
class Customer(DataContractModel):
    customer_id: int = Field(alias="customerId")
```

ContractModel must define which name is canonical in:

- Python validation
- ODCS
- serialized records
- database mappings
- generated documentation

PipelineModel should consume that decision consistently.

## Custom Validators

Custom Pydantic validators remain available:

```python
from pydantic import field_validator


class Customer(DataContractModel):
    customer_id: int
    email: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()
```

Not every custom Python validator can be represented portably in ODCS or pushed down into an external execution engine.

ContractModel should distinguish between:

- portable contract constraints
- Python-only validation behavior
- engine-supported pushdown constraints

PipelineModel should surface that distinction during planning when it affects execution.

## Data Contract Identity

Every published data contract should have a stable identity.

At minimum, PipelineModel needs access to:

- contract identifier
- contract version
- ODCS specification version
- Python model type
- generated artifact location, when available

Stable identity allows PipelineModel to:

- detect duplicate contracts
- validate pipeline connections
- generate references
- compare versions
- produce deterministic contract bundles
- build lineage and documentation

## Data Contracts as Pipeline Types

A `DataContractModel` class is used as a logical dataset type.

```python
class ValidateCustomers(Transformation):
    customers: Input[RawCustomer]
    valid: Output[ValidCustomer]
    rejected: Output[RejectedCustomer]
```

PipelineModel compares the declared output contract of one node with the declared input contract of the next.

This comparison should be semantic, not merely based on Python class identity.

Possible relationships include:

- exact contract match
- compatible contract version
- explicitly allowed subtype
- compatible projected schema
- incompatible contract

The detailed compatibility rules remain owned by ContractModel and ODCS integration.

## Sources

Sources declare the contract of data entering the pipeline:

```python
from pipelinemodel import Source


raw_customers: Source[RawCustomer] = Source(
    binding="raw_customer_csv",
)
```

The source's execution plugin is responsible for reading data.

PipelineModel and ContractModel are responsible for validating the resulting data against `RawCustomer`.

## Sinks

Sinks declare the contract of data being published:

```python
from pipelinemodel import Sink


curated_customers: Sink[Customer] = Sink(
    input=normalized.result,
    binding="customer_warehouse",
)
```

Before a sink writes data, PipelineModel may invoke ContractModel validation according to the active profile and validation policy.

## Runtime Validation

PipelineModel coordinates validation at data boundaries:

```text
Source read
    ↓
Validate against source contract
    ↓
Transformation input
    ↓
Transformation output
    ↓
Validate against output contract
    ↓
Sink write
```

ContractModel performs the contract-specific validation.

The execution plugin may provide optimized validation for its native representation.

Examples include:

- Pydantic record validation
- Pandas dataframe validation
- Polars expression validation
- SQL constraint validation
- Arrow schema validation

## Validation Policies

Validation policy should be configurable by pipeline profile.

Example conceptual configuration:

```python
local = ExecutionProfile(
    validate_source_outputs=True,
    validate_transform_inputs=True,
    validate_transform_outputs=True,
    validate_sink_inputs=True,
)
```

A production profile may choose optimized or sampled validation where supported.

Changing the policy must not change the meaning of the underlying data contract.

## Invalid Data Handling

When data violates a contract, PipelineModel should create a typed invalid-data event.

A callback may then choose a declarative action:

```python
from pipelinemodel import (
    InvalidDataAction,
    InvalidDataContext,
    on_invalid_data,
)


@on_invalid_data
def quarantine_customer_rows(
    context: InvalidDataContext[Customer],
) -> InvalidDataAction:
    return InvalidDataAction.quarantine(
        destination="invalid-customers",
        continue_with_valid=True,
    )
```

PipelineModel coordinates the decision.

Execution and storage plugins carry out the actual filtering, quarantine, or write behavior.

## ODCS Generation

ContractModel-compatible classes should generate deterministic ODCS documents:

```python
Customer.write_odcs(
    "contracts/data/customer.odcs.yaml",
)
```

A pipeline may generate all referenced contracts at once:

```python
CustomerPipeline.write_contracts("contracts/")
```

PipelineModel should delegate ODCS generation to ContractModel rather than maintaining an independent generator.

## Loading Existing Contracts

Existing ODCS contracts may be loaded into ContractModel-compatible Python representations:

```python
Customer = DataContractModel.from_odcs(
    "contracts/data/customer.odcs.yaml",
)
```

The resulting type should be usable anywhere an authored `DataContractModel` class is accepted.

The loading API should preserve:

- contract identity
- field metadata
- constraints
- documentation
- source references
- unsupported or extension metadata where possible

## Generated Versus Authored Models

PipelineModel should not care whether a contract class was:

- authored directly in Python
- generated from ODCS
- imported from another package
- produced dynamically during tooling

All valid `DataContractModel` classes should expose the same public contract metadata interface.

## Versioning

Contract versions belong to the data contract, not to the pipeline node.

A pipeline may bind to:

- one exact version
- a compatible version range
- a named contract resolved by a registry
- a local Python class

ContractModel should determine whether two versions are compatible.

PipelineModel should use that result when validating graph connections.

## Contract Discovery

PipelineModel should be able to discover every data contract referenced by:

- sources
- transformation inputs
- transformation outputs
- sinks
- subpipelines

This enables automatic bundle generation:

```text
Pipeline class
    ↓
Discover referenced DataContractModel classes
    ↓
Deduplicate by contract identity
    ↓
Generate ODCS artifacts
    ↓
Reference them from DTCS and DPCS
```

## Public Boundary Requirements

For PipelineModel integration, ContractModel should expose stable public operations conceptually equivalent to:

```python
get_contract_identity(Customer)
get_contract_metadata(Customer)
validate_data(Customer, value)
generate_odcs(Customer)
load_odcs(path)
compare_contracts(previous, current)
```

The exact names belong to ContractModel's API design.

PipelineModel should never depend on private attributes, Pydantic internals, or undocumented ODCS conversion behavior.

## Recommended Practices

- Use one concrete `DataContractModel` per published logical dataset.
- Give every published contract a stable identifier and explicit version.
- Prefer `Annotated` and `Field` for constraints and documentation.
- Keep portable constraints separate from Python-only validation logic.
- Reuse data contract classes directly in transformation annotations.
- Commit generated ODCS artifacts when contracts are part of governance or review workflows.
- Validate outputs before publishing them through sinks.
- Let ContractModel own compatibility decisions.

## Anti-Patterns

Avoid defining the same schema separately in:

- a Pydantic model
- a transformation declaration
- a pipeline node
- an ODCS YAML file
- a dataframe plugin

The `DataContractModel` should be the Python source of truth, with ODCS serving as the portable representation.

Avoid coupling data contracts to a particular execution engine:

```python
## Avoid Making Polars or Pandas Part of the Logical Data Contract
class CustomerPolarsFrame(...):
    ...
```

The logical contract describes the records. Plugins decide how those records are represented during execution.

## Key Principle

> A `DataContractModel` describes what valid data means. PipelineModel uses that type to connect the pipeline. Execution plugins decide how the data is physically represented and processed.

## Next Step

Continue with **PYDANTIC_INTEGRATION.md** for a detailed explanation of how PipelineModel and ContractModel use Pydantic types, constraints, metadata, validation, and generated schemas.
