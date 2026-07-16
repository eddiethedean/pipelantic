# Dataframe Plugin

A **Dataframe Plugin** implements the PipelineModel Dataframe Plugin API for a
specific dataframe engine.

Dataframe plugins execute transformation implementations using a concrete
dataframe library while preserving the logical semantics defined by the
Pipeline Plan, DTCS, and the associated data contracts.

PipelineModel itself is dataframe-independent. Dataframe plugins provide the
physical execution layer.

## Purpose

A dataframe plugin is responsible for:

- Executing transformation implementations
- Materializing logical datasets
- Validating transformation outputs
- Converting between runtime data structures
- Advertising execution capabilities
- Optimizing execution for its backend

It is **not** responsible for:

- Pipeline planning
- Graph execution
- Scheduling
- Contract generation
- Contract loading

## Architecture

```text
Transformation
       │
       ▼
Pipeline Plan
       │
       ▼
Dataframe Plugin API
       │
 ┌─────┼─────────────┐
 ▼     ▼             ▼
Polars Pandas    Future Engines
```

The plugin executes one transformation at a time while the orchestration plugin
coordinates the overall pipeline.

## Responsibilities

Every dataframe plugin should:

- Receive typed transformation inputs
- Invoke the selected implementation
- Validate outputs against declared contracts
- Return normalized outputs
- Emit structured diagnostics

Observable transformation behavior must remain identical regardless of the
backend.

## Plugin Interface

Conceptually:

```python
class DataframePlugin:
    name: str
    version: str

    def execute(
        self,
        context,
        transformation,
        implementation,
        inputs,
        parameters,
    ):
        ...
```

The exact SDK API may evolve, but plugins should expose a consistent execution
interface.

## Input Handling

Inputs arrive as logical datasets described by data contracts.

The plugin materializes them into native runtime objects.

Examples:

- Polars DataFrame
- Pandas DataFrame
- DuckDB relation
- Spark DataFrame

The transformation implementation operates on native objects.

## Output Handling

Returned datasets must satisfy the declared output contracts.

The plugin should validate outputs before they continue through the pipeline.

Invalid outputs should produce structured diagnostics.

## Capabilities

Plugins publish capabilities such as:

- Lazy execution
- Streaming
- Parallel execution
- Window functions
- Expression support
- Async compatibility

Planning compares required capabilities against those provided by the plugin.

## Async Support

Plugins should support synchronous and asynchronous implementations.

PipelineModel normalizes invocation so plugin authors do not need separate
public APIs.

## Error Handling

Plugins should translate backend-specific exceptions into structured
PipelineModel diagnostics.

Diagnostics should preserve:

- Transformation identity
- Step identity
- Pipeline identity
- Original exception
- Backend details

## Performance

Plugins may optimize execution through:

- Lazy evaluation
- Query optimization
- Vectorized execution
- Parallelism
- Resource reuse

Optimizations must never change observable semantics.

## Best Practices

- Preserve DTCS semantics.
- Keep contracts backend-independent.
- Validate outputs.
- Advertise capabilities accurately.
- Translate backend errors into PipelineModel diagnostics.

## Anti-Patterns

Avoid:

- Exposing dataframe types in public contracts.
- Changing transformation semantics.
- Skipping output validation.
- Relying on global mutable state.
- Embedding orchestration behavior.

## Key Principle

> A dataframe plugin executes transformation implementations using a specific
> dataframe engine while preserving the portable semantics defined by
> PipelineModel contracts and Pipeline Plans.

## Next Step

Continue with [Orchestrator Plugin](ORCHESTRATOR_PLUGIN.md) to learn how
execution coordination is implemented for workflow engines such as Airflow and
Dagster.
