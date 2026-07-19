# Roadmap Summary

ETLantic is an alpha project moving toward a stable, secure modeling and plugin
platform. Milestones describe capability order, not release-date commitments.

## 0.15 shipped

ETLantic 0.16.0 closed the Safe SQL Lowering exit gate and the LocalScheduler
companion:

- `etlantic-sql` claims kernel + `portable-relational/1` through typed
  `etlantic.sql/1` IR (PostgreSQL reference dialect; bound parameters only);
- Extract / Load / `asset=` is the preferred authoring vocabulary
  (`Source` / `Sink` / `binding=` warn; remove in 0.16);
- `Pipeline.run` / `arun` enter through built-in `LocalScheduler`;
- public portable conformance covers Polars, PySpark, Pandas, and SQL.

See [What's New in 0.15](../01_GETTING_STARTED/WHATS_NEW_0_15.md) and
[Capabilities](../01_GETTING_STARTED/CAPABILITIES.md) for the shipped boundary.

### 0.15 continuation (not required to close 0.15)

Richer portable profiles (window, string-advanced, conversion, complex
types/values, statistics, reshape, relational-extended, temporal-IANA,
nondeterministic) graduate **one family at a time** only after two independent
compilers pass shared fixtures. That work is sequenced after the SQL vertical
slice; it is not a separate 0.16 milestone.

## Prior: 0.14

ETLantic 0.14.0 completed the first three-engine portable relational baseline
(Pandas joined Polars and PySpark) and published the public portable
conformance SDK. See [What's New in 0.14](../01_GETTING_STARTED/WHATS_NEW_0_14.md).

## Next: 0.16 (shipped)

0.16.0 shipped Gate A (vocabulary cleanup) and Gate B (optional
`etlantic-prefect` `ExecutionScheduler`). See
[What's New in 0.16](../01_GETTING_STARTED/WHATS_NEW_0_16.md) and
[Migration 0.15 → 0.16](MIGRATION_0_15_TO_0_16.md).

## 0.17+ portable plugin workstream

Every applicable first-party dataframe, SQL, and Spark execution plugin will
pair its runtime integration with a portable transform compiler. Polars,
Pandas, SQL, and PySpark already provide the kernel and
`portable-relational/1` baseline; future work expands truthful per-family
coverage, cross-engine differential tests, conformance evidence, capability
matrices, and native-to-portable migration guidance.

This does not require portable compilers from orchestrators, schedulers,
secret/storage/resource/observability providers, or model bridges. Third-party
execution plugins may remain native-only when they omit portable claims and
document the limitation. See
[Building an ETLantic Plugin](../07_PLUGIN_SDK/BUILDING_A_PLUGIN.md).

## Toward 1.0

The 1.0 goal is a stable foundation with:

- stable authoring, Plugin SDK, plan, event, result, and run-report contracts;
- documented compatibility, deprecation, and schema-migration policies;
- completed security gates for plugin provenance, secret handling, artifact and
  cache isolation, network constraints, audit evidence, and bounded work;
- conformance and acceptance coverage across reference engines and
  orchestrators;
- complete executable tutorials, references, and migration guides.

> **Do not productionize ETLantic before the 1.0 security release gate
> closes.** Version 0.15.0 is alpha; available allowlists and version pins do
> not make the product production-ready. See the
> [Evaluator Brief](../01_GETTING_STARTED/EVALUATOR.md).

Read the
[full roadmap](https://github.com/eddiethedean/etlantic/blob/main/ROADMAP.md)
for milestone details, acceptance scenarios, and release gates.
