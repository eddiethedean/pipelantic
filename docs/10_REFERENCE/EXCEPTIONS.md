# Exceptions Reference

PipelineModel uses structured diagnostics for expected contract and pipeline
problems. Exceptions represent failures in API usage, loading, configuration,
plugins, or runtime execution.

> The hierarchy below is the proposed public exception model for 1.0.

## Base Exception

```python
class PipelineModelError(Exception):
    """Base class for public PipelineModel exceptions."""
```

Applications may catch this base class at integration boundaries, but should
usually catch a more specific exception.

## Proposed Hierarchy

```text
PipelineModelError
├── ConfigurationError
├── SourceLoadError
├── ModelDefinitionError
├── PipelineValidationError
├── PlanningError
│   ├── BindingResolutionError
│   ├── ImplementationResolutionError
│   └── CapabilityError
├── PluginError
│   ├── PluginDiscoveryError
│   ├── PluginCompatibilityError
│   └── PluginExecutionError
├── CompilationError
├── PipelineExecutionError
│   ├── NodeExecutionError
│   ├── DataValidationError
│   ├── PipelineTimeoutError
│   └── PipelineCancelledError
└── InternalPipelineModelError
```

## `ConfigurationError`

Raised when configuration cannot be loaded or contains invalid values that
prevent constructing a runtime.

## `SourceLoadError`

Raised for unreadable Python modules, contract documents, or required local
resources.

Syntax and contract-shape problems should normally be represented as
diagnostics attached to a load result.

## `ModelDefinitionError`

Raised when a class definition violates invariants that cannot be represented
as a usable model, such as an invalid annotation wrapper or conflicting port
declaration.

## `PipelineValidationError`

Raised by convenience methods such as `raise_for_errors()` when a validation
report contains errors.

```python
try:
    CustomerPipeline.validate().raise_for_errors()
except PipelineValidationError as exc:
    for diagnostic in exc.report.diagnostics:
        print(diagnostic.code, diagnostic.message)
```

## `PlanningError`

Raised when a valid logical pipeline cannot be resolved for a selected profile.
The exception should carry a planning report.

Common causes include missing bindings, unavailable implementations, and
unsupported backend capabilities.

## `PluginError`

Represents plugin discovery, loading, compatibility, or protocol failures.
User-code failures executed through a plugin should generally be wrapped in
`NodeExecutionError`, with the plugin named in the execution context.

## `CompilationError`

Raised when a resolved `PipelinePlan` cannot be compiled for a target backend.
The error should identify the unsupported plan element and target.

## `PipelineExecutionError`

Base class for terminal failures while executing or submitting a plan.

It should include:

- Pipeline and run identity
- Failed node, when applicable
- Attempt number
- Selected implementation and plugin
- Structured diagnostics
- Original exception through exception chaining

## `DataValidationError`

Represents invalid runtime data when the configured policy requires failure.
Partial rejection or quarantine may instead produce a successful node result
with rejected-record metadata.

## Cancellation and Timeouts

Cancellation and timeout are distinct states:

```python
except PipelineTimeoutError:
    ...
except PipelineCancelledError:
    ...
```

Plugins should preserve these states instead of converting them into a generic
failure.

## Internal Errors

`InternalPipelineModelError` indicates a broken framework invariant. It should
include a diagnostic code and enough context for a bug report, while redacting
secrets.

## Exception Chaining

PipelineModel should retain the original cause:

```python
raise NodeExecutionError(context=ctx) from original_exception
```

This preserves useful tracebacks without exposing backend exceptions as the
stable public API.

## Sync and Async Behavior

Sync and async entry points should raise equivalent public exceptions:

```python
CustomerPipeline.run()
await CustomerPipeline.arun()
```

Calling `run()` from an active asynchronous context should raise a clear usage
error directing the user to `await arun()`.

## What Not to Catch

Do not broadly catch `BaseException`. Cancellation, keyboard interruption, and
system-exiting exceptions require careful propagation and cleanup.

## See Also

- [Diagnostics](DIAGNOSTICS.md)
- [Callbacks](../04_TRANSFORMATIONS/CALLBACKS.md)
- [Error Handling](../04_TRANSFORMATIONS/ERROR_HANDLING.md)

