# Validation

Validation is a core part of the Pipelantic data-contract lifecycle.

Pipelantic coordinates **when** validation happens, ContractModel defines **what valid data means**, and execution plugins determine **how validation is performed efficiently** for a chosen runtime.

The architectural boundary is:

```text
Data
      │
      ▼
ContractModel
Defines contract semantics
      │
      ▼
Pipelantic
Coordinates validation boundaries
      │
      ▼
Execution Plugin
Performs engine-specific validation
```

## Goals

Data-contract validation should:

- Detect invalid data before it is published
- Catch transformation output violations early
- Preserve ContractModel semantics across execution engines
- Support both record-oriented and dataframe-oriented validation
- Produce structured diagnostics
- Allow configurable failure and quarantine behavior
- Remain independent of Pandas, Polars, SQL, or any other runtime
- Avoid silently weakening declared contract requirements

## Responsibility Boundaries

### ContractModel

ContractModel owns:

- Field and model validation
- Pydantic semantics
- Data-contract constraints
- ODCS mappings
- Contract identity
- Compatibility analysis
- Data-contract diagnostics
- Validation reports

### Pipelantic

Pipelantic owns:

- Validation timing
- Validation policy
- Validation boundary selection
- Callback dispatch
- Invalid-data actions
- Execution-plan checks
- Plugin capability checks
- Aggregating validation results across a pipeline

### Execution plugins

Execution plugins own:

- Native dataframe validation
- SQL validation pushdown
- Arrow schema checks
- Sampling or batch validation
- Materialization where required
- Rejecting or splitting invalid records
- Writing quarantined data
- Returning structured validation results

## Validation Boundaries

Pipelantic may validate data at four primary boundaries.

### 1. Source output validation

After a source reads data, the result may be validated against the source contract.

```text
External source
      │
      ▼
Read plugin
      │
      ▼
Source contract validation
```

This confirms that incoming data satisfies the declared data contract before downstream transformations receive it.

### 2. Transformation input validation

Before a transformation runs, each input may be validated against its declared `Input[T]` contract.

```python
class NormalizeCustomers(Transformation):
    customers: Input[RawCustomer]
    result: Output[Customer]
```

Pipelantic verifies that the provided input is governed by a compatible contract.

Runtime validation may also confirm that the actual data satisfies `RawCustomer`.

### 3. Transformation output validation

After a transformation completes, each output may be validated against its declared `Output[T]` contract.

```text
Transformation implementation
          │
          ▼
Output contract validation
          │
          ▼
Downstream node
```

An invalid output indicates that the implementation failed to satisfy its declared transformation interface.

The recommended default is to fail the node.

### 4. Sink input validation

Before a sink writes or publishes data, Pipelantic may validate the input against the sink contract.

This is the final publication boundary and should usually receive the strongest validation policy.

## Validation Lifecycle

A typical data path looks like this:

```text
Read
  │
  ▼
Validate source output
  │
  ▼
Validate transformation input
  │
  ▼
Execute transformation
  │
  ▼
Validate transformation output
  │
  ▼
Validate sink input
  │
  ▼
Write or publish
```

Profiles may enable or disable individual validation boundaries, but the contract semantics remain unchanged.

## Structural Validation

Structural validation checks whether data contains the expected shape.

Examples include:

- Required fields
- Allowed fields
- Nested object structure
- Collection structure
- Field names
- Field aliases
- Nullability
- Record shape

Structural validation should happen before more expensive semantic checks whenever practical.

## Type Validation

Type validation checks whether values match their declared logical types.

Examples include:

- Integer
- Decimal
- String
- Boolean
- Date
- Datetime
- UUID
- Enum
- Nested object
- List
- Mapping

ContractModel remains authoritative for type meaning.

Plugins may translate logical types into native types, but they must report unsupported mappings.

## Constraint Validation

Constraints may include:

- Minimum and maximum values
- Minimum and maximum lengths
- Regular-expression patterns
- Enumerated values
- Required uniqueness
- Allowed nullability
- Cross-field invariants
- Custom validators

Portable constraints should be enforced consistently across runtimes.

Python-only custom validators may require fallback validation through ContractModel.

## Record Validation

Record-oriented validation uses Pydantic or ContractModel directly.

```python
customer = Customer.model_validate(
    {
        "customer_id": 42,
        "email": "ada@example.com",
    }
)
```

This approach is appropriate for:

- Small datasets
- API payloads
- Individual events
- Unit tests
- Fallback validation
- Detailed error reporting

It may be too expensive for large dataframe workloads.

## Batch and Dataframe Validation

For large datasets, plugins should prefer vectorized or batch validation.

Examples:

### Polars

A Polars plugin may compile contract constraints into expressions.

### Pandas

A Pandas plugin may use vectorized masks.

### SQL

A SQL plugin may generate predicates or constraints.

### Arrow

An Arrow plugin may validate schema compatibility and nullability.

The result should still conform to the same logical contract semantics.

## Native Validation Capability

Plugins should declare which validation capabilities they support.

Conceptually:

```python
PluginValidationCapabilities(
    schema=True,
    required_fields=True,
    nullability=True,
    numeric_ranges=True,
    string_lengths=True,
    regex=True,
    enums=True,
    custom_python_validators=False,
    cross_field_rules=False,
)
```

Pipelantic uses this information during planning.

If a required constraint is unsupported, Pipelantic may:

- Fall back to ContractModel
- Materialize data
- Reject the plan
- Warn when policy permits partial validation

Silent omission is not allowed.

## Validation Modes

Pipelantic should support several validation modes.

### Full

Validate all records and all supported constraints.

```python
ValidationMode.FULL
```

### Schema only

Validate shape and logical types without row-level semantic checks.

```python
ValidationMode.SCHEMA
```

### Sampled

Validate a configured sample.

```python
ValidationMode.SAMPLED
```

### Disabled

Skip runtime data validation.

```python
ValidationMode.DISABLED
```

Disabling validation affects enforcement, not the meaning of the contract.

Profiles should make this distinction explicit.

## Validation Profiles

A profile may configure validation behavior:

```python
from pipelantic import Profile

production = Profile(
    name="production",
    # validation policy fields may evolve; keep policies declarative
)
```

The exact API may differ, but the policy should remain declarative and inspectable.

## Invalid Input Data

Invalid input data may be handled by policy.

Possible actions include:

- Fail the node
- Reject invalid records
- Drop invalid records
- Quarantine invalid records
- Continue with valid records
- Invoke callbacks
- Record diagnostics
- Emit metrics

Example:

```python
from pipelantic import (
    InvalidDataAction,
    InvalidDataContext,
    on_invalid_data,
)


@on_invalid_data(stage="input_validation")
def handle_invalid_customers(
    context: InvalidDataContext[RawCustomer],
) -> InvalidDataAction:
    return InvalidDataAction.quarantine(
        destination="invalid-customers",
        continue_with_valid=True,
    )
```

Pipelantic coordinates the action.

Plugins carry out the actual split, write, or quarantine.

## Invalid Output Data

Invalid transformation output is more serious.

It means the implementation did not fulfill the declared transformation contract.

Recommended default behavior:

```text
Invalid transformation output
        │
        ▼
Fail the node
        │
        ▼
Invoke failure and invalid-data hooks
        │
        ▼
Prevent publication
```

Profiles may override this behavior, but permissive handling should require explicit configuration.

## Validation Results

Validation should produce structured results rather than only raising exceptions.

Conceptually:

```python
report = CustomerPipeline.validate_data(
    node="normalized",
    value=result,
)

if not report.valid:
    for diagnostic in report.diagnostics:
        print(diagnostic.code, diagnostic.message)
```

A validation report should include:

- Contract identity
- Contract version
- Node identity
- Validation stage
- Validation mode
- Number of records checked
- Number of valid records
- Number of invalid records
- Diagnostics
- Unsupported constraints
- Plugin used
- Duration
- Whether fallback validation occurred

## Diagnostics

Validation diagnostics should be structured and machine-readable.

A diagnostic may include:

- Code
- Message
- Severity
- Contract path
- Data field path
- Record index or key
- Invalid value, when safe
- Constraint
- Suggested remediation
- Node identity
- Run identity

Example human-readable output:

```text
PMDATA102

Node: normalize_customers
Contract: customer@1.0.0
Field: email
Record: 42

Value does not satisfy the declared email constraint.
```

## Sensitive Data

Diagnostics must avoid exposing sensitive values.

ContractModel and Pipelantic should support:

- Redacted values
- Omitted values
- Field sensitivity metadata
- Safe logging defaults
- Configurable detail levels
- Restricted diagnostic sinks

Personally identifiable information, secrets, and regulated data should not be logged by default.

## Error Translation

Pydantic errors should be translated into Pipelantic validation diagnostics.

```text
Pydantic ValidationError
        │
        ▼
ContractModel Validation Report
        │
        ▼
Pipelantic InvalidDataContext
        │
        ▼
Callback and InvalidDataAction
```

Users should not have to parse raw Pydantic error structures.

## Sync and Async Validation

Validation callbacks may be synchronous or asynchronous.

```python
@on_invalid_data
def handle_invalid(context):
    ...
```

```python
@on_invalid_data
async def handle_invalid(context):
    ...
```

Pipelantic normalizes both through its internal async invocation layer.

Validation plugins may also expose sync or async implementations.

## Validation and Planning

Planning should verify that the chosen execution profile can satisfy validation requirements.

Example failures include:

- A plugin cannot enforce strict types
- A remote runtime cannot run Python validators
- A streaming source cannot support full materialization
- A selected profile disables required publication validation
- A sink cannot quarantine rejected records
- A plugin cannot preserve field aliases

These issues should be reported before execution begins.

## Compatibility Validation

Pipeline wiring validation is distinct from runtime data validation.

### Wiring compatibility

Checks whether one node's output contract is compatible with the next node's input contract.

### Runtime validation

Checks whether actual data satisfies the declared contract.

Both are required.

```text
Output contract compatibility
            │
            ▼
Actual output data validation
```

ContractModel owns compatibility analysis.

Pipelantic invokes it during graph validation.

## Validation Pushdown

Validation should be pushed as close to the source as practical.

Examples:

- Database predicates
- SQL constraints
- Storage schema checks
- Parquet metadata checks
- Arrow schema validation
- Native dataframe expressions

Pushdown is an optimization.

The logical contract remains the source of truth.

## Fallback Validation

When pushdown is incomplete, Pipelantic may fall back to ContractModel validation.

```text
Plugin-native checks
        │
        ▼
Unsupported constraints remain
        │
        ▼
ContractModel fallback
```

Fallback behavior should be visible in the execution plan and validation report.

## Streaming Validation

Streaming validation introduces additional concerns:

- Unbounded input
- Windowed checks
- Incremental statistics
- Late-arriving data
- Partial failures
- Checkpoint behavior

Pipelantic should treat streaming validation as a plugin capability.

A contract may remain the same while enforcement strategy differs.

## Partial Acceptance

Some data sources and transformations may allow valid records to continue while invalid records are rejected.

Conceptually:

```text
Input batch
    │
    ├── Valid records ──► Continue
    │
    └── Invalid records ──► Reject or quarantine
```

Partial acceptance must be explicit.

It should never occur silently.

## Quarantine

Quarantine is an execution behavior, not a new contract type.

A quarantine destination may be configured through:

- A node callback
- A profile
- A storage binding
- A plugin setting

The quarantined records should retain:

- Original data where permitted
- Validation diagnostics
- Contract identity
- Pipeline and node identity
- Run identity
- Timestamp
- Source metadata

## Metrics

Validation may emit metrics such as:

- Records checked
- Records accepted
- Records rejected
- Validation duration
- Constraint failures
- Fallback usage
- Quarantine volume

Metrics belong to runtime observability, not data-contract semantics.

## Testing Validation

Tests should cover:

- Valid records
- Missing required fields
- Extra fields
- Nullability
- Type coercion
- Strict types
- Aliases
- Nested models
- Custom validators
- Batch validation
- Plugin fallback
- Invalid-data callbacks
- Quarantine behavior
- Sensitive-value redaction
- Output contract violations

Each plugin should run a shared conformance suite against ContractModel semantics.

## Recommended Defaults

Suggested defaults:

| Boundary | Default |
|---|---|
| Source output | Schema validation |
| Transformation input | Compatibility plus schema validation |
| Transformation output | Full validation |
| Sink input | Full validation |
| Invalid source/input records | Fail unless policy allows partial acceptance |
| Invalid transformation output | Fail node |
| Unsupported required constraints | Fail planning |
| Sensitive invalid values | Redact |

These defaults may evolve, but safety should be preferred over permissiveness.

## Recommended Practices

- Validate transformation outputs before downstream use.
- Validate sink inputs before publication.
- Let ContractModel define contract semantics.
- Let plugins optimize enforcement.
- Require plugins to declare unsupported constraints.
- Treat fallback validation as visible plan behavior.
- Redact sensitive values in diagnostics.
- Use explicit policies for partial acceptance.
- Preserve structured validation results.
- Test every execution plugin against the same contract fixtures.

## Anti-Patterns

### Silent validation gaps

A plugin must not ignore unsupported constraints.

### Runtime-only discovery

Do not wait until a production run to discover that a plugin cannot enforce required rules.

### Treating validation as a transformation

Validation checks truth conditions. It should not silently mutate data.

### Hiding invalid output

Transformation output violations should not be downgraded casually.

### Logging entire rejected records

Diagnostics should minimize exposure of sensitive data.

### Duplicating contract rules in plugins

Plugins should compile or enforce ContractModel semantics, not invent independent rules.

## Key Principle

> ContractModel defines validity. Pipelantic decides where and when validity is checked. Execution plugins perform the check using the most appropriate runtime strategy.

## Next Step

Continue with **VERSIONING.md** to learn how data contracts evolve, how compatibility is evaluated, and how Pipelantic validates contract versions across pipeline boundaries.
