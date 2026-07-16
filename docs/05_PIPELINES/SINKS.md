# Sinks

A `Sink[T]` defines a typed exit point from a PipelineModel pipeline.

Sinks publish validated data to external systems. Like `Source[T]`, a sink
declares **what** data crosses the pipeline boundary while execution plugins
determine **how** that data is written.

## Purpose

A sink answers one question:

> Where does the pipeline publish its results?

Because every sink is typed, PipelineModel can validate publication boundaries,
generate DPCS artifacts, derive lineage, and plan execution without depending
on a specific storage technology.

## Basic Example

```python
from pipelinemodel import Sink

warehouse = Sink[Customer](
    input=normalized.result,
    binding="warehouse.customers",
)
```

The sink declares that it publishes `Customer` records.

## Relationship to Data Contracts

Every sink references a published `DataContractModel`.

```python
warehouse: Sink[Customer]
```

The contract defines the logical records being published.

Execution plugins decide whether those records are written to:

- SQL databases
- Data warehouses
- Object storage
- Parquet files
- CSV files
- REST APIs
- Message queues
- Streaming systems
- Other destinations

## Bindings

Bindings identify the logical destination.

```python
Sink[Customer](
    input=normalized.result,
    binding="curated.customers",
)
```

Bindings remain execution-neutral and are resolved by the active execution
profile or plugin.

## Validation

Sink inputs are the final validation boundary.

PipelineModel may validate:

- Contract compatibility
- Required fields
- Nullability
- Constraints
- Version compatibility
- Publication policy

The recommended default is full validation before data leaves the pipeline.

## Planning

During planning PipelineModel resolves:

- Destination binding
- Execution plugin
- Validation policy
- Runtime resources
- Authentication
- Write strategy

Missing or incompatible destinations should be reported before execution.

## Relationship to DPCS

Each sink becomes part of the generated DPCS pipeline contract, including:

- Sink identity
- Input binding
- Data contract
- Destination binding
- Metadata

## Lineage

Sinks form the terminal nodes of the lineage graph.

PipelineModel can automatically derive:

- Published datasets
- Upstream dependencies
- Impact analysis
- Documentation

## Best Practices

- Publish typed data contracts.
- Validate before writing.
- Use stable logical bindings.
- Keep sink definitions execution-neutral.
- Let plugins manage write semantics.

## Anti-Patterns

Avoid:

- Embedding SQL statements or SDK clients in sink declarations.
- Publishing dataframe types instead of logical contracts.
- Skipping validation at publication boundaries.
- Coupling sinks to a single execution engine.

## Key Principle

> A `Sink[T]` defines the logical destination of data. Execution plugins decide
> how that data is written and committed.

## Next Step

Continue with [Subpipelines](SUBPIPELINES.md) to learn how complete pipeline
graphs can be composed from reusable pipeline definitions.
