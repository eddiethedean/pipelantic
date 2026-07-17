# etlantic-sparkforge

SparkForge → ETLantic **migration adapter** (ETLantic 0.10 Migration Preview).

SparkForge remains the medallion-facing facade (bronze / silver / gold).
This package maps those conventions onto ordinary ETLantic `Source` / `Step` /
`Sink`, `Profile`, `RunSelection` / `RunIntent`, and `PipelineRunReport`
surfaces. **ETLantic core never gains medallion types.**

## Install

```bash
pip install etlantic-sparkforge
# or
pip install 'etlantic[sparkforge]'
```

Optional live SparkForge bridging is available when the SparkForge /
`pipeline_builder` package is installed in the same environment. IR fixture
tests and the core adapter do **not** require it.

## Quick start (IR → Pipeline)

```python
from etlantic_sparkforge import (
    SparkForgePipelineSpec,
    SparkForgeStepSpec,
    StepKind,
    LayerKind,
    adapt_pipeline,
    debug_request_from_sparkforge,
)

spec = SparkForgePipelineSpec(
    name="ecommerce",
    schema="demo",
    steps=(
        SparkForgeStepSpec(
            name="orders",
            kind=StepKind.BRONZE_RULES,
            layer=LayerKind.BRONZE,
            table_name="bronze_orders",
        ),
        SparkForgeStepSpec(
            name="clean_orders",
            kind=StepKind.SILVER_TRANSFORM,
            layer=LayerKind.SILVER,
            source="orders",
            table_name="silver_orders",
            write_mode="overwrite",
        ),
    ),
)
adapted = adapt_pipeline(spec)
adapted.pipeline_cls.validate(profile=adapted.profile)
request = debug_request_from_sparkforge(mode="incremental", skip_writes=True)
```

## Progressive engine deprecation path

1. **Plan-only** — generate/inspect ETLantic plans from SparkForge IR
2. **Dual reporting** — `adapt_run_result` → `PipelineRunReport`
3. **ETLantic planning** — selections/intents via `debug_request_from_sparkforge`
4. **Plugin execution** — `Profile.spark_engine="pyspark"` / SQL plugins
5. **Facade** — SparkForge keeps medallion builder; retire duplicated engines

See `docs/11_DEVELOPMENT/MIGRATION_0_9_TO_0_10.md`.

## Boundary

| Concern | Owner |
|---|---|
| bronze / silver / gold APIs | SparkForge |
| portable graph, plan, reports | ETLantic |
| mapping + parity fixtures | `etlantic-sparkforge` |
