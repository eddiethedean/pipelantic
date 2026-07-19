# Roadmap Summary

ETLantic 0.18.0 is production/stable for documented single-tenant reference
deployments. Milestones describe capability order, not release-date
commitments, and do not expand that bounded support envelope.

## Shipped: 0.15 through 0.18

ETLantic **0.15.0** closed Safe SQL Lowering and the LocalScheduler companion.

ETLantic **0.16.0** shipped Gate A (authoring vocabulary cleanup) and Gate B
(optional `etlantic-prefect` `ExecutionScheduler`).

ETLantic **0.17.0** shipped portable coverage expansion:

- Gate A — transform-compiler CLI inventory, exact capability matrix, drift
  checks, allowlist-safe discovery
- Gate B — Wave 1 on Polars + PySpark (`portable-window/1`,
  `portable-string-advanced/1`, `portable-conversion/1`,
  `portable-statistics/1`)
- Gate C — Wave 2 on Polars + PySpark (`portable-complex-types/1`,
  `portable-complex-values/1`, `portable-reshape/1`)

Pandas and SQL remain kernel + `portable-relational/1` in 0.17. See
[What's New in 0.17](../01_GETTING_STARTED/WHATS_NEW_0_17.md) and
[Migration 0.16 → 0.17](MIGRATION_0_16_TO_0_17.md).

**0.17 continuation** (not required to close 0.17):
`portable-relational-extended/1`, `portable-temporal-iana/1`,
`portable-nondeterministic/1`, `portable-window/2`.

## Shipped: 0.18 Gate A (versioned tabular interchange)

**0.18 status:** Gate A shipped in **0.18.0**. Gate B (DataFusion) is a
**non-blocking 0.19+ experiment** and does not ship as part of 0.18.0.

0.18.0 formalizes `etlantic.interchange/1` as the preferred, versioned physical
interchange at compatible cross-plugin boundaries while retaining ETLantic
contracts and plans as the semantic authority.

- **A0–A4:** engine-registry prerequisite; interchange descriptor; mechanism
  selection truth table; fidelity/evidence bounds; Polars↔Pandas conformance
- Parquet is a durable **artifact** mechanism, not in-process transport
- PySpark/SQL Arrow boundaries are explicit follow-ups after Polars↔Pandas
- **Gate B:** experimental `etlantic-datafusion` runtime + portable kernel
  compiler, graduating only with conformance and a measured advantage

PyArrow and DataFusion stay out of the core dependency set. 0.17 portable
continuation families may proceed in parallel but do not block 0.18.0. See the
[0.18 Versioned Tabular Interchange Plan](INTEROPERABILITY_FOUNDATION_PLAN.md).

## Prior: 0.14

ETLantic 0.14.0 completed the first three-engine portable relational baseline
and published the public portable conformance SDK. See
[What's New in 0.14](../01_GETTING_STARTED/WHATS_NEW_0_14.md).

## Toward 1.0

The 1.0 goal is a stable foundation with:

- stable authoring, Plugin SDK, plan, event, result, and run-report contracts;
- documented compatibility, deprecation, and schema-migration policies;
- completed security gates for plugin provenance, secret handling, artifact and
  cache isolation, network constraints, audit evidence, and bounded work;
- conformance and acceptance coverage across reference engines and
  orchestrators;
- complete executable tutorials, references, and migration guides.

> **Production use is supported only within the documented 0.18 reference
> envelope.** Multi-tenant isolation, deployment topology, compliance/SBOM/
> signing, and advanced supply-chain controls remain adopter-owned. Available
> allowlists and version pins do not make arbitrary topologies safe. See the
> [Evaluator Brief](../01_GETTING_STARTED/EVALUATOR.md).

Read the
[full roadmap](https://github.com/eddiethedean/etlantic/blob/main/ROADMAP.md)
for milestone details, acceptance scenarios, and release gates.
