# Callbacks

Callbacks allow applications to respond to important events in a pipeline's lifecycle
without embedding operational logic inside transformation implementations.

ETLantic coordinates callback invocation. Execution plugins perform the
underlying work.

Callbacks are one of several lifecycle extension mechanisms. They are distinct
from runtime lifespan, execution middleware, and resource injection. See
[Lifecycle Extension Mechanisms](../06_EXECUTION/LIFECYCLE_EXTENSIONS.md).

## Goals

Callbacks should:

- Separate business logic from operational behavior.
- Support synchronous and asynchronous functions.
- Be strongly typed.
- Be execution-engine independent.
- Produce predictable, inspectable behavior.

## Callback Types

Typical callback categories include:

- Invalid input data
- Invalid output data
- Transformation failure
- Retry decisions
- Transformation completion
- Pipeline completion
- Pipeline failure

## Invalid Data

```python
from etlantic import (
    InvalidDataAction,
    InvalidDataContext,
    on_invalid_data,
)

@on_invalid_data
def quarantine(context: InvalidDataContext[Customer]) -> InvalidDataAction:
    return InvalidDataAction.quarantine(
        destination="invalid-customers",
        continue_with_valid=True,
    )
```

ETLantic interprets the returned action while the execution plugin performs
the quarantine or filtering.

## Failure Callbacks

```python
from etlantic import FailureContext, on_failure

@on_failure
def notify(context: FailureContext):
    ...
```

Failure callbacks may:

- Log diagnostics
- Send notifications
- Trigger incident workflows
- Decide retry behavior

## Completion Callbacks

```python
from etlantic import CompletionContext, on_complete

@on_complete
async def publish_metrics(context: CompletionContext):
    ...
```

Completion hooks are useful for metrics, auditing, and downstream automation.

## Sync and Async

Callbacks may use either style.

```python
@on_failure
def handler(context):
    ...
```

```python
@on_failure
async def handler(context):
    ...
```

ETLantic normalizes invocation internally.

## Typed Context Objects

Callbacks receive strongly typed context objects rather than unstructured
dictionaries.

Typical context information includes:

- Pipeline identifier
- Transformation identifier
- Contract identity
- Execution profile
- Run identifier
- Diagnostics
- Exception information (when applicable)

## Callback Actions

Some callbacks return an action object.

Conceptually:

```python
return InvalidDataAction.fail()
return FailureAction.retry()
return InvalidDataAction.quarantine(...)
return InvalidDataAction.continue_with_valid()
```

The action remains declarative. Plugins execute the requested behavior.

## Ordering

When multiple callbacks are registered, ETLantic should execute them in a
deterministic order documented by the framework.

Callbacks associated with a wrapped operation run inside run or step middleware
unless the callback explicitly represents final provider shutdown. Yield-based
resource cleanup occurs after the callback has finished using the injected
resource.

## Callbacks Versus Middleware

Use middleware when behavior must surround every matching invocation:

- timing
- tracing
- structured logging
- context propagation

Use callbacks when behavior responds to a specific outcome:

- validation failed
- step completed
- retry exhausted
- pipeline completed

Callbacks should not implement a general `call_next` wrapper.

## Outbound Events

A callback may return an `Emit` action targeting a typed outbound event:

```python
@CustomerPipeline.on_complete
def publish_completion(context):
    return Emit(
        CustomerPipeline.pipeline_completed,
        PipelineCompleted(
            pipeline_id=context.pipeline_id,
            run_id=context.run_id,
        ),
    )
```

The outbound event declares what may be sent. A notification provider handles
HTTP, Kafka, queue, or other delivery mechanics.

## Best Practices

- Keep callbacks focused on operational concerns.
- Use typed context objects.
- Avoid modifying pipeline topology from callbacks.
- Prefer declarative action objects over side effects.
- Keep callbacks idempotent where practical.

## Anti-Patterns

Avoid:

- Embedding business transformations inside callbacks.
- Depending on runtime-specific objects.
- Mutating contracts.
- Swallowing failures silently.
- Using callbacks as unbounded middleware.
- Sending undocumented transport-specific payloads directly from portable
  pipeline definitions.

## Key Principle

> Callbacks describe **how the framework should respond** to lifecycle events.
> They do not change the logical transformation contract.

## Next Step

Continue with [Error Handling](ERROR_HANDLING.md) to learn how callback actions,
runtime failures, and validation failures interact.
