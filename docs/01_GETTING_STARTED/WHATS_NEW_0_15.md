# What's New in ETLantic 0.15

> **Status: Available in ETLantic 0.15.0.**

ETLantic 0.15 ships **Safe SQL Lowering** for the portable kernel and
`portable-relational/1` claim set, prefers the **Extract / Load / asset**
authoring vocabulary, and extracts direct execution behind a built-in
**LocalScheduler** boundary.

## Safe SQL Lowering

`etlantic-sql` now registers a portable transform compiler
(`etlantic.transform_compilers` → `sql`) that lowers
`dtcs.transform-plan/2` into typed `etlantic.sql/1` IR and executes through
the PostgreSQL reference dialect (SQLite remains a convenience path for local
conformance).

- Bound parameters and validated identifiers only — no literal interpolation
- Trusted SQL fragments are forbidden in portable definitions
- Dialect gaps fail during `analyze()` with `PMXFORM*` findings
- Public conformance:
  `run_portable_transform_conformance_suite(create_transform_compiler())`

Native `@implementation("sql")` remains supported and tested.

## Extract / Load / asset

Prefer:

```python
from etlantic import Extract, Load

raw = Extract[Customer](asset="customers")
out = Load[Customer](input=result, asset="curated")
```

`Source` / `Sink` / `binding=` emit `DeprecationWarning` and are removed in
0.16. Plan, DPCS, and plugin wire names (`binding`, `"source"` / `"sink"`
kinds, `etlantic:binding`) are unchanged for fingerprint stability.

See [Migration 0.14 → 0.15](../11_DEVELOPMENT/MIGRATION_0_14_TO_0_15.md).

## LocalScheduler

`Pipeline.run` / `arun` now enter through `LocalScheduler`, the zero-service
direct-execution default. Airflow remains an external compile target
(`etlantic.orchestration/1`). Optional Prefect packaging is planned for 0.16
Gate B as an `ExecutionScheduler` (logical-node MVP; not a DAG compiler);
vocabulary cleanup is the independent Gate A. See the
[scheduler plan](../11_DEVELOPMENT/SCHEDULER_AND_PREFECT_PLAN.md) and
[ROADMAP §0.16](https://github.com/eddiethedean/etlantic/blob/main/ROADMAP.md#016--authoring-vocabulary-cleanup-and-optional-prefect-scheduler).

## Not in 0.15

Advanced portable profile graduation (window, reshape, complex values, …)
remains **0.15 continuation** work and is not required to close this release.
