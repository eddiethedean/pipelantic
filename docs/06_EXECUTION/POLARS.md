# Polars Plugin

**Status: shipped in 0.5.0** as the reference dataframe backend
(`etlantic-polars`).

The portable transformation compiler described below ships in 0.12 for the
**kernel** claim set.

## Install

```bash
pip install etlantic-polars
pip install 'etlantic-polars[arrow]'  # optional
```

## Behavior

- Eager `DataFrame` execution is the baseline
- `LazyFrame` values are preserved across adjacent Polars steps
- Collection happens only at plan-declared boundaries (sink publication,
  cross-engine conversion, explicit collection points)
- Contract ↔ Polars dtype mapping with structured diagnostics for unsupported
  types
- Sync and async implementation callables are supported
- Portable kernel IR compiles via `etlantic.transform_compilers` without a
  native `@implementation("polars")` callable

## Portable compiler (shipped 0.12)

The Polars compiler is the first executable lowering for
`dtcs.transform-plan/2` (v1 readable). In **0.12** it claims **only**
`dtcs:profile/portable-relational-kernel/1` (plan-v2 `/2` metadata
compatibility without extra relational ops). Join, union, group, aggregate,
sort, distinct, and limit **execution** claims land in **0.13**. It:

- lowers portable kernel columns to native `pl.Expr` values
- lowers kernel relational nodes to `DataFrame` and `LazyFrame` operations
- preserves `LazyFrame` across compatible portable steps
- rejects unsupported (non-kernel) semantics during planning
- retains logical expression and output mappings
- collects only at plan-declared boundaries

It must not fall back to Python row functions or collect data to emulate an
unsupported operation. Richer authored profiles still need a native
`@implementation("polars")` (or a later compiler claim) until 0.13–0.15.

## Example

See `examples/dataframe_parity.py` in the repository:

```bash
uv run --group dataframes python examples/dataframe_parity.py polars
```
