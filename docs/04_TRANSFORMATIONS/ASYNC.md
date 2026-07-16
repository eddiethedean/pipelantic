# Async

PipelineModel is asynchronous by design, but it strives to make asynchronous
execution nearly invisible to application developers.

Like FastAPI, PipelineModel allows authors to write either synchronous (`def`)
or asynchronous (`async def`) code. The framework detects the implementation
style and invokes it correctly, allowing developers to focus on business logic
instead of concurrency primitives.

## Goals

PipelineModel's async model should:

- Support both synchronous and asynchronous implementations.
- Hide event-loop management from users.
- Provide a consistent programming model.
- Enable efficient concurrent execution.
- Keep transformation contracts independent of execution strategy.

## Philosophy

Authors describe *what* a transformation does.

PipelineModel decides *how* to invoke it.

```python
@NormalizeCustomers.implementation("polars")
def normalize(customers):
    ...
```

```python
@NormalizeCustomers.implementation("remote")
async def normalize(customers):
    ...
```

Both implementations satisfy the same transformation contract.

## Internal Execution Model

Conceptually:

```text
Transformation Contract
          │
          ▼
Execution Planner
          │
          ▼
Async Invocation Layer
          │
          ├── Sync implementation
          └── Async implementation
```

The invocation layer normalizes execution so callers do not need separate APIs.

## Async Callbacks

Callbacks follow the same pattern.

```python
@on_failure
def notify(context):
    ...
```

```python
@on_failure
async def notify(context):
    ...
```

PipelineModel awaits asynchronous callbacks automatically.

## Resources

Execution plugins may expose asynchronous resources such as:

- Database connections
- Object storage clients
- HTTP clients
- Message queues

Profiles bind these resources to transformations without changing the
transformation contract.

## Concurrency

Execution plugins determine how work is parallelized.

Examples include:

- Task scheduling
- Thread pools
- Async I/O
- Distributed execution
- Vectorized dataframe operations

PipelineModel plans execution but does not dictate a concurrency strategy.

## Cancellation

Long-running executions should support cooperative cancellation where the
selected execution backend allows it.

Cancellation should propagate through typed execution contexts and callbacks.

## Error Handling

Exceptions raised by synchronous and asynchronous implementations should be
translated into the same structured PipelineModel diagnostics.

Users should not need separate error-handling paths.

## Best Practices

- Prefer `async def` for naturally asynchronous operations.
- Use `def` for CPU-bound or synchronous libraries.
- Let PipelineModel manage invocation.
- Keep contracts independent of concurrency concerns.
- Avoid manual event-loop management.

## Anti-Patterns

Avoid:

- Calling `asyncio.run()` inside implementations.
- Mixing event-loop management with business logic.
- Writing separate transformation contracts for sync and async execution.
- Exposing backend-specific concurrency primitives in public APIs.

## Key Principle

> PipelineModel treats synchronous and asynchronous implementations as
equivalent ways of satisfying the same transformation contract. Concurrency is
an execution concern, not a modeling concern.

## Next Step

Continue with [DTCS](DTCS.md) to learn how synchronous and asynchronous
implementations remain separate from portable transformation semantics.
