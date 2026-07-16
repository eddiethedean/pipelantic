# Dataframe Plugins

Dataframe plugins implement the physical execution of transformations using a
specific dataframe library while preserving the logical semantics defined by
DTCS and the Pipeline Plan.

PipelineModel does **not** depend on a dataframe library. Instead, dataframe
plugins translate portable transformation contracts into efficient operations
for a chosen backend.

## Goals

Dataframe plugins should:

- Preserve transformation semantics.
- Remain interchangeable.
- Hide backend-specific APIs from pipeline authors.
- Support synchronous and asynchronous execution.
- Expose capabilities for planning.

## Philosophy

Transformations define **what** happens.

Dataframe plugins define **how** it happens.

```text
Transformation (DTCS)
          │
          ▼
   Pipeline Plan
          │
          ▼
 Dataframe Plugin
          │
   ┌──────┼──────┐
   ▼      ▼      ▼
 Polars Pandas DuckDB
```

## Why Plugins?

Keeping dataframe engines outside the core provides:

- Backend independence
- Easier optimization
- Cleaner public APIs
- Multiple execution strategies
- Future extensibility

## Supported Backends

PipelineModel is designed to support plugins for:

- Polars (recommended default)
- Pandas
- DuckDB
- Spark
- Future dataframe libraries

The available plugins determine which implementations can be selected during
planning.

## Transformation Implementations

A transformation may expose multiple implementations.

```python
@NormalizeCustomers.implementation("polars")
def normalize(...):
    ...

@NormalizeCustomers.implementation("pandas")
def normalize(...):
    ...
```

The active dataframe plugin determines which implementation executes.

## Capabilities

Each dataframe plugin should publish capabilities such as:

- Lazy execution
- Streaming support
- Parallel execution
- Join strategies
- Window functions
- Expression engine
- Async compatibility

Planning compares required capabilities against those supplied by the plugin.

## Polars

Polars is the recommended backend because it offers:

- Excellent performance
- Native parallelism
- Lazy execution
- Strong Arrow interoperability
- Modern expression API

It aligns well with PipelineModel's asynchronous, execution-agnostic design.

## Pandas

Pandas remains a supported plugin for compatibility with the broader Python
ecosystem.

It is valuable for existing projects and third-party libraries, even though
some execution profiles may prefer Polars for performance and scalability.

## Execution Independence

Transformation contracts never reference dataframe types directly.

Avoid:

```python
customers: Input["pl.DataFrame"]
```

Prefer:

```python
customers: Input[Customer]
```

The dataframe plugin determines the runtime representation.

## Plugin Lifecycle

Typical lifecycle:

```text
Discover
    │
    ▼
Register
    │
    ▼
Capability Evaluation
    │
    ▼
Implementation Selection
    │
    ▼
Execution
```

## Best Practices

- Keep contracts dataframe-independent.
- Implement native optimizations inside plugins.
- Preserve observable semantics.
- Declare capabilities explicitly.
- Validate outputs before publishing.

## Anti-Patterns

Avoid:

- Embedding dataframe APIs in public contracts.
- Requiring a single dataframe engine.
- Changing transformation semantics for performance.
- Exposing backend-specific objects outside plugin boundaries.

## Key Principle

> Dataframe plugins optimize execution, not behavior. A pipeline should produce
the same logical results regardless of the selected dataframe backend.

## Next Step

Continue with [Orchestration Plugins](ORCHESTRATION_PLUGINS.md) to learn how
Pipeline Plans are bound to workflow orchestration platforms.
