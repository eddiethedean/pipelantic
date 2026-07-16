# Local Python

The Local Python execution plugin allows PipelineModel to execute validated
**Pipeline Plans** directly within a Python process.

Local execution is the reference execution environment for PipelineModel. It is
ideal for development, testing, experimentation, CI, and lightweight
production workloads.

Unlike orchestration platforms, Local Python requires no external scheduler or
workflow engine. It executes the same Pipeline Plan while preserving identical
pipeline semantics.

## Goals

The Local Python plugin should:

- Execute Pipeline Plans without external infrastructure.
- Preserve DPCS semantics.
- Support synchronous and asynchronous implementations.
- Provide deterministic execution.
- Serve as the reference execution backend.
- Enable rapid local development.

## Philosophy

Local execution should never bypass the PipelineModel lifecycle.

```text
Pipeline
    │
    ▼
Validation
    │
    ▼
Planning
    │
    ▼
Pipeline Plan
    │
    ▼
Local Python Plugin
    │
    ▼
Python Runtime
```

The only difference between local execution and orchestration is the execution
plugin.

## Why Local Execution?

Local execution is useful for:

- Unit testing
- Integration testing
- Interactive development
- Jupyter notebooks
- Command-line tools
- CI pipelines
- Small production deployments

Developers can validate pipeline behavior before deploying to larger execution
platforms.

## Execution Model

The Local Python plugin executes steps according to the dependency graph.

Execution preserves:

- Step ordering
- Parallel opportunities
- Failure semantics
- Retry policies
- Callback behavior
- Resource lifecycles

The implementation should never change observable pipeline behavior.

## Sync and Async

The Local Python plugin supports both:

```python
def normalize(...):
    ...
```

and

```python
async def normalize(...):
    ...
```

PipelineModel automatically invokes the correct implementation style.

Developers should not manage event loops directly.

## Concurrency

Where possible, the plugin may execute independent branches concurrently.

Concurrency should always respect:

- Dependency ordering
- Resource constraints
- Failure semantics
- Callback ordering

Optimization must never alter pipeline meaning.

## Resources

The Local Python plugin coordinates:

- Resource plugins
- Storage plugins
- Dataframe plugins
- Callback execution

It acquires resources during execution and releases them when no longer needed.

## Diagnostics

The plugin should emit structured execution events including:

- Pipeline started
- Step started
- Step completed
- Step failed
- Retry
- Pipeline completed

Events should reference stable pipeline and step identities.

## Relationship to Other Plugins

Local execution is one orchestration backend among many.

The same Pipeline Plan may also execute using:

- Airflow
- Dagster
- Prefect
- Future orchestration plugins

Observable pipeline semantics should remain identical.

## Best Practices

- Use Local Python during development.
- Validate before execution.
- Test pipelines locally before deployment.
- Keep execution profiles environment-specific.
- Preserve deterministic behavior.

## Anti-Patterns

Avoid:

- Executing Python pipeline definitions directly.
- Skipping validation or planning.
- Embedding local-only behavior into pipeline contracts.
- Treating Local Python as a separate execution model.

## Key Principle

> Local Python is the reference execution backend for PipelineModel. It executes
validated Pipeline Plans directly within Python while preserving the same
portable semantics expected from every orchestration plugin.

## Next Step

Continue with [Compilation](COMPILATION.md) to compare direct local execution
with generation of backend-specific artifacts.
