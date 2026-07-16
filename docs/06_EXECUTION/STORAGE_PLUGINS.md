# Storage Plugins

Storage plugins provide ETLantic with a portable way to read from and write
to persistent storage systems.

Rather than embedding storage-specific APIs into pipeline definitions, storage
plugins translate logical source and sink bindings into operations for concrete
storage technologies.

Pipeline authors describe **what** data should be read or written. Storage
plugins determine **how** those operations are performed.

## Goals

Storage plugins should:

- Preserve data contract semantics.
- Support multiple storage technologies.
- Hide storage-specific APIs from pipeline authors.
- Be interchangeable through execution profiles.
- Expose capabilities for planning.
- Keep storage concerns outside pipeline definitions.

## Philosophy

```text
Pipeline Plan
      │
      ▼
 Storage Plugin
      │
 ┌────┼─────────────────────────┐
 ▼    ▼            ▼            ▼
CSV  PostgreSQL   S3       Delta Lake
```

Storage is an implementation concern, not a modeling concern.

## Responsibilities

Storage plugins are responsible for:

- Reading sources
- Writing sinks
- Managing connections
- Handling authentication
- Optimizing transfers
- Reporting storage diagnostics

They are **not** responsible for:

- Pipeline planning
- Contract validation
- Transformation semantics
- Graph execution

## Supported Storage Systems

ETLantic is designed to support plugins for:

- Local files
- CSV
- Parquet
- JSON
- PostgreSQL
- MySQL
- SQLite
- DuckDB
- Snowflake
- BigQuery
- Delta Lake
- Apache Iceberg
- Amazon S3
- Azure Blob Storage
- Google Cloud Storage
- Future storage systems

## Source Integration

A source declares a logical binding.

```python
customers = Source[Customer](
    binding="customers",
)
```

The storage plugin resolves that binding into a physical location.

## Sink Integration

A sink publishes through the same abstraction.

```python
warehouse = Sink[Customer](
    input=normalized.result,
    binding="warehouse.customers",
)
```

The selected storage plugin determines how the write occurs.

## Resource Bindings

Profiles map logical bindings to runtime resources.

Development:

```text
customers -> ./data/customers.parquet
```

Production:

```text
customers -> s3://company/raw/customers/
```

The pipeline definition remains unchanged.

## Capabilities

Storage plugins should declare capabilities such as:

- Read support
- Write support
- Transactions
- Streaming
- Partitioning
- Versioning
- Compression
- Batch operations

Planning compares required capabilities against those provided by the plugin.

## Validation

Storage plugins cooperate with ContractModel and DataContractModel to ensure
published and retrieved data satisfies the declared contracts.

## Error Handling

Plugins should report structured diagnostics for:

- Missing resources
- Authentication failures
- Network failures
- Permission errors
- Serialization failures
- Write conflicts

## Best Practices

- Keep bindings logical.
- Store credentials outside contracts.
- Preserve contract semantics.
- Declare capabilities explicitly.
- Use profiles for environment-specific configuration.

## Anti-Patterns

Avoid:

- Embedding filesystem paths in pipeline models.
- Hard-coding cloud SDKs into transformations.
- Returning storage-specific objects from public APIs.
- Coupling contracts to one storage technology.

## Key Principle

> Storage plugins provide the physical persistence layer for ETLantic while
preserving the portable, storage-independent semantics defined by pipeline,
transformation, and data contracts.

## Next Step

Continue with [Resource Providers](RESOURCE_PLUGINS.md) to learn how execution
resources are acquired, managed, and shared across plugins.
