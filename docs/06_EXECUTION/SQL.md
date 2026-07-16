# SQL

The SQL execution backend allows PipelineModel to execute eligible
transformations directly inside a SQL database instead of materializing data
into an in-memory dataframe.

SQL execution is an optimization of the execution strategy, not a different
pipeline model. Pipelines, contracts, and transformation interfaces remain
portable regardless of whether execution occurs in SQL, Polars, Pandas, or
another backend.

## Goals

SQL execution should:

- Execute transformations close to the data.
- Minimize data movement.
- Preserve DTCS and DPCS semantics.
- Support multiple SQL dialects.
- Reuse the standard Pipeline Plan.
- Fall back to other implementations when necessary.

## Execution Lifecycle

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
Pipeline Plan (IR)
    │
    ▼
SQL Execution Plugin
    │
    ▼
SQL Compiler
    │
    ▼
Database
```

## SQL Implementations

Transformations remain implementation-independent.

```python
class BuildCustomerSummary(Transformation):
    customers: Input[Customer]
    orders: Input[Order]
    result: Output[CustomerSummary]
```

A SQL implementation may be registered:

```python
@BuildCustomerSummary.implementation("sql")
def build_customer_summary(...):
    ...
```

The planner selects this implementation only when its requirements are satisfied.

## Planner Selection

The planner should prefer SQL execution when:

- A SQL implementation exists.
- Required inputs are accessible from SQL.
- The selected database supports required features.
- Output can be written without changing semantics.
- Required plugin capabilities are available.

Otherwise another implementation (such as Polars) should be selected.

## SQL Compiler

The SQL execution plugin compiles logical operations into a dialect-specific
query.

Compilation targets may include:

- SQLite
- PostgreSQL
- DuckDB
- Snowflake
- BigQuery
- SQL Server
- Databricks SQL

The compiler preserves pipeline semantics while adapting syntax to the selected
dialect.

## Pushdown Optimization

The SQL backend may optimize execution through:

- Predicate pushdown
- Projection pruning
- Join pushdown
- Aggregation pushdown
- Window function pushdown
- Common table expressions
- INSERT ... SELECT
- CREATE TABLE AS SELECT
- MERGE or UPSERT

These optimizations must not alter observable behavior.

## Transaction Semantics

Where supported, SQL execution should perform writes transactionally.

Typical flow:

```text
Read
 │
 ▼
Transform
 │
 ▼
Validate Output
 │
 ▼
Begin Transaction
 │
 ▼
Publish
 │
 ▼
Commit
```

Failures should roll back partial writes whenever possible.

## Capability Detection

SQL plugins should advertise capabilities such as:

- Transactions
- Window functions
- MERGE
- Recursive CTEs
- Streaming
- Temporary tables
- Stored procedures

Planning validates required capabilities before execution.

## Validation

Input and output contracts remain authoritative.

Execution must validate contract requirements even when the transformation is
fully executed inside the database.

## Diagnostics

SQL execution should emit structured diagnostics including:

- Generated query identifier
- Pipeline identity
- Step identity
- Dialect
- Execution phase
- Backend exception
- Suggested remediation

## Performance

SQL execution is particularly effective for:

- SQL-to-SQL pipelines
- Large joins
- Aggregations
- Incremental warehouse loading
- ELT workflows

Avoid unnecessary movement of data into Python when equivalent SQL execution is
available.

## Best Practices

- Keep transformation contracts backend-independent.
- Register SQL implementations alongside dataframe implementations.
- Let the planner choose the implementation.
- Prefer logical SQL expressions over raw SQL strings.
- Preserve deterministic semantics.

## Anti-Patterns

Avoid:

- Embedding SQL inside pipeline definitions.
- Hard-coding database-specific syntax in contracts.
- Skipping output validation.
- Assuming every database supports every SQL feature.

## Key Principle

> SQL execution is another backend for PipelineModel. It executes the same
validated Pipeline Plan using database-native operations, allowing computation
to move to the data while preserving the portable semantics defined by ODCS,
DTCS, and DPCS.

## Next Step

Continue with **COMPILATION.md** to learn how PipelineModel compiles Pipeline
Plans into backend-specific execution artifacts, including SQL.
