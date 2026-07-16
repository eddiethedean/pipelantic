# Sources

A `Source[T]` defines a typed entry point into a ETLantic pipeline.

Sources introduce data from external systems into the pipeline while declaring
the logical contract of the records they produce. Like every other modeling
primitive in ETLantic, a source describes **what** data enters the
pipeline—not **how** it is retrieved.

Execution plugins perform the actual reads.

## Purpose

A source answers one question:

> Where does pipeline data begin?

By declaring a source with a data contract, ETLantic can:

- Validate incoming data
- Build the pipeline graph
- Generate DPCS artifacts
- Produce lineage
- Generate documentation
- Plan execution

## Basic Example

```python
from etlantic import Source

customers = Source[RawCustomer](
    binding="customers_csv",
)
```

The source declares that it produces `RawCustomer` records.

## Relationship to Data Contracts

Every source is typed with a `Data`.

```python
customers: Source[Customer]
```

The contract defines the logical records.

Execution plugins determine whether those records originate from:

- CSV files
- Parquet
- SQL queries
- Object storage
- REST APIs
- Kafka
- Message queues
- Streaming systems
- Other external systems

## Bindings

Sources identify *what* to read through a binding.

```python
customers = Source[Customer](
    binding="warehouse.customers",
)
```

Bindings are intentionally execution-neutral.

A profile or plugin resolves the binding into runtime-specific details.

## Validation

Source validation is typically the first runtime validation boundary.

ETLantic may validate:

- Contract compatibility
- Required fields
- Nullability
- Types
- Constraints
- Source metadata

Plugins may perform native validation or delegate to ContractModel.

## Planning

During planning, ETLantic resolves:

- Source bindings
- Execution plugin
- Validation policy
- Runtime resources
- Authentication requirements

Planning should detect missing or incompatible bindings before execution.

## Execution Independence

The same source definition should work across multiple runtimes.

```python
customers = Source[Customer](
    binding="customers",
)
```

Different execution profiles may map that binding to:

- Local files
- Cloud storage
- SQL databases
- Data lake tables
- Streaming topics

The pipeline definition remains unchanged.

## Relationship to DPCS

Every source becomes part of the generated DPCS pipeline contract.

The generated artifact records:

- Source identity
- Data contract
- Binding
- Metadata
- Relationships

## Lineage

Sources form the roots of the pipeline lineage graph.

ETLantic can automatically derive:

- Origin datasets
- Downstream dependencies
- Impact analysis
- Documentation

## Best Practices

- Type every source with a published data contract.
- Use stable binding names.
- Keep bindings execution-neutral.
- Validate source data before downstream processing.
- Let execution profiles resolve runtime details.

## Anti-Patterns

Avoid:

- Embedding SQL, filesystem paths, or cloud SDK objects directly in source contracts.
- Returning dataframe types instead of logical contracts.
- Duplicating schema information already defined by `Data`.
- Coupling sources to a specific execution engine.

## Key Principle

> A `Source[T]` defines the logical origin of data. Execution plugins decide how
> that data is located, read, and materialized.

## Next Step

Continue with **SINKS.md** to learn how typed sinks publish validated data at
the end of a pipeline.
