# Prefect Feasibility Spike (0.15)

Status: notes only — **not** a release dependency  
Package target: optional `etlantic-prefect` in **0.16** (Gate B)

## Goal

Prove that a Prefect adapter can consume a resolved `PipelinePlan` through the
same [`ExecutionScheduler`](../../src/etlantic/runtime/scheduler.py) boundary as
`LocalScheduler`, without re-planning or becoming a core dependency.

## Findings (spike)

1. **Boundary:** `LocalScheduler.analyze` / `execute` is sufficient as the
   direct-execution contract. Prefect should implement the same protocol in
   0.16 rather than inventing a second discovery system.
2. **Units:** 0.15 still schedules logical graph nodes via the runtime host.
   `plan.physical_units` remain advisory until fusion-driven unit scheduling
   lands (post-0.16). The 0.16 MVP maps **one Prefect task per selected
   logical node** with the same dependency closure as `LocalScheduler`.
3. **Ownership:** Prefect must not own validation, materialization,
   retry-safety, redaction, or `PipelineRunReport` construction.
4. **Default path:** Prefect remains absent from core imports and from the
   default `development` / `test` profiles.
5. **Not a compiler:** Prefect is an `ExecutionScheduler`, not an
   `OrchestratorPlugin` / `compile_plan` target like Airflow.

## Non-goals for the spike

- Publishing `etlantic-prefect`
- Changing production profile defaults
- Replacing `etlantic-airflow`

## Follow-ups for 0.16 (Gate B MVP)

- Wire `Profile(orchestrator="prefect")` + plugin allowlisting into the run
  path (stop hard-coding only `LocalScheduler`)
- Publish `packages/etlantic-prefect` implementing `ExecutionScheduler` /
  `etlantic.scheduler/1`
- Map one Prefect task per selected logical node (same closure as local)
- Correlate ETLantic run/node ids with Prefect flow/task-run ids
- Minimal shared public conformance fixtures with `LocalScheduler`
- Local direct invocation only; no Cloud/server required for the basic path

## Deferred past 0.16

- Fusion-driven `physical_units` as the Prefect (or local) execution grain
- Prefect deployment/serve and durable scheduling
- Full scheduler conformance corpus from the scheduler plan

Vocabulary cleanup (`Source` / `Sink` / `binding=` removal) is a **sibling**
0.16 Gate A and does not depend on this package. See
[ROADMAP §0.16](https://github.com/eddiethedean/etlantic/blob/main/ROADMAP.md#016--authoring-vocabulary-cleanup-and-optional-prefect-scheduler).
