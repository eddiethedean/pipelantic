# Polars

The Polars plugin is the **reference dataframe implementation** for PipelineModel.

PipelineModel is designed to remain dataframe-agnostic, but Polars aligns
especially well with its architecture through high performance, lazy execution,
parallelism, and Apache Arrow interoperability. For new projects, Polars is the
recommended execution backend.

## Goals

The Polars plugin should:

- Execute DTCS transformation implementations using Polars.
- Preserve PipelineModel semantics.
- Serve as the reference dataframe implementation.
- Support synchronous and asynchronous execution.
- Maximize performance without changing observable behavior.

## Philosophy

Pipeline authors model pipelines using contracts—not dataframes.

```python
class NormalizeCustomers(Transformation):
    customers: Input[RawCustomer]
    result: Output[Customer]
```

Execution profiles choose Polars.

```python
@NormalizeCustomers.implementation("polars")
def normalize(customers, minimum_age):
    ...
```

The transformation contract never depends on `pl.DataFrame`.

## Why Polars?

Polars offers:

- Excellent performance
- Native multithreading
- Lazy query optimization
- Apache Arrow interoperability
- Efficient memory usage
- Modern expression API

These characteristics make it an ideal default execution backend.

## Recommended Usage

PipelineModel recommends Polars for:

- New pipelines
- Large datasets
- ETL workflows
- Analytical processing
- Batch execution
- Arrow-based ecosystems

## Execution Profile

```python
production = Profile(
    dataframe_engine="polars",
)
```

Planning selects Polars implementations for compatible transformations.

## Supported Features

The Polars plugin should support:

- Typed transformation execution
- Lazy execution where appropriate
- Contract validation
- Async integration through PipelineModel
- Structured diagnostics
- Callback integration

## Relationship to Other Plugins

Transformations may provide multiple implementations.

```python
@NormalizeCustomers.implementation("polars")
def normalize_polars(...):
    ...

@NormalizeCustomers.implementation("pandas")
def normalize_pandas(...):
    ...
```

The active execution profile determines which implementation is used.

## Interoperability

Although Polars is the recommended backend, PipelineModel does not require it.

The same pipeline should execute correctly with any conforming dataframe plugin,
provided the selected plugin satisfies the required capabilities.

## Best Practices

- Keep contracts dataframe-independent.
- Use Polars expressions instead of row-wise operations when practical.
- Preserve DTCS semantics.
- Validate outputs before publication.
- Optimize inside the plugin, not the public API.

## Anti-Patterns

Avoid:

- Using `pl.DataFrame` in pipeline interfaces.
- Encoding Polars-specific behavior into contracts.
- Changing transformation semantics for optimization.
- Assuming every deployment uses Polars.

## Key Principle

> Polars is the reference execution backend for PipelineModel. It provides a
high-performance implementation while remaining completely interchangeable with
other dataframe plugins from the perspective of pipeline authors.

## Next Step

Continue with [Local Python](LOCAL_PYTHON.md) to learn how Pipeline Plans
execute directly without an external orchestrator.
