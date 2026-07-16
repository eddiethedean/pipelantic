# Command-Line Interface

The PipelineModel command-line interface exposes validation, planning,
generation, visualization, compilation, and delegated execution for local
development and automation.

> The commands in this chapter describe the proposed PipelineModel 1.0 CLI.
> Names and options may change before the public API is stabilized.

## Command

```bash
pipelinemodel [GLOBAL_OPTIONS] COMMAND [ARGS]
```

The CLI must use the same public APIs as Python applications. It must not
implement a second planner, validator, or contract generator.

## Global Options

```text
--project PATH        Project root or configuration file
--profile NAME        Execution profile
--format FORMAT       human, json, or sarif output
--color / --no-color  Control ANSI color
--verbose             Include additional operational detail
--quiet               Suppress non-error output
--version             Display the installed version
--help                Display help
```

Command-line options override environment variables, which override project
configuration.

## Core Commands

### `init`

Create a new PipelineModel project.

```bash
pipelinemodel init customer_pipeline
```

The generated project should contain a minimal typed pipeline, tests, profiles,
and contract output directories.

### `inspect`

Inspect a pipeline without executing it.

```bash
pipelinemodel inspect src/customer_pipeline.py:CustomerPipeline
```

Inspection may report:

- Pipeline identity and version
- Sources, steps, sinks, and subpipelines
- Referenced ODCS, DTCS, and DPCS contracts
- Registered transformation implementations
- Unresolved bindings
- Available profiles

### `validate`

Validate contracts, transformation interfaces, graph wiring, and selected
profile bindings.

```bash
pipelinemodel validate src/customer_pipeline.py:CustomerPipeline
pipelinemodel validate contracts/customer.dpcs.yaml
pipelinemodel validate . --profile production
```

Validation does not execute user transformation code.

### `plan`

Resolve a pipeline and profile into a deterministic `PipelinePlan`.

```bash
pipelinemodel plan src/customer_pipeline.py:CustomerPipeline \
  --profile production \
  --output build/customer-plan.json
```

Planning resolves:

- Plugin and implementation selection
- Source and sink bindings
- Resources
- Execution regions
- Capability requirements
- Materialization boundaries

### `run`

Delegate a validated plan to the selected orchestration backend.

```bash
pipelinemodel run src/customer_pipeline.py:CustomerPipeline --profile local
```

`run` is primarily intended for local or directly managed backends. An
externally managed orchestrator may instead return a submission identifier or
require compilation.

### `compile`

Compile a plan into a backend artifact.

```bash
pipelinemodel compile src/customer_pipeline.py:CustomerPipeline \
  --profile production \
  --target airflow \
  --output build/dags/customer_pipeline.py
```

Possible targets include Airflow DAGs, deployment bundles, SQL scripts, Spark
job definitions, and plugin-defined artifacts.

### `generate`

Generate portable artifacts from typed Python models.

```bash
pipelinemodel generate contracts src/customer_pipeline.py:CustomerPipeline \
  --output contracts/
```

Subcommands may include:

```text
generate contracts
generate docs
generate mermaid
generate graphviz
generate html
```

Generated contracts must remain separated by standard:

```text
contracts/
├── data/             # ODCS
├── transformations/  # DTCS
└── pipelines/        # DPCS
```

### `graph`

Render a logical pipeline or resolved plan.

```bash
pipelinemodel graph src/customer_pipeline.py:CustomerPipeline \
  --format mermaid \
  --output build/customer-pipeline.mmd
```

The logical graph should remain distinguishable from a backend execution graph.

### `plugins`

Inspect installed plugins and capabilities.

```bash
pipelinemodel plugins list
pipelinemodel plugins show polars
pipelinemodel plugins check --profile production
```

### `config`

Inspect effective configuration and its provenance.

```bash
pipelinemodel config show --profile production
pipelinemodel config validate
```

Sensitive values must be redacted.

## Pipeline References

Python pipelines use an importable reference:

```text
package.module:PipelineClass
```

File references may also be supported:

```text
src/pipelines/customer.py:CustomerPipeline
```

Contract-first pipelines use a DPCS path:

```text
contracts/pipelines/customer.dpcs.yaml
```

## Output Formats

Human output is the default. Machine-readable modes are intended for CI and
editor integrations.

```bash
pipelinemodel validate . --format json
pipelinemodel validate . --format sarif
```

## Exit Codes

| Code | Meaning |
|---:|---|
| 0 | Command completed successfully |
| 1 | Validation, planning, or compatibility errors |
| 2 | Invalid command usage or configuration |
| 3 | Source, import, or I/O failure |
| 4 | Plugin or backend failure |
| 130 | Interrupted by the user |

## CI Example

```bash
pipelinemodel validate . --profile production --format sarif
pipelinemodel generate contracts . --check
pipelinemodel plan . --profile production --check
```

`--check` should compare generated output without modifying files.

## Safety

Commands that only inspect, validate, plan, or generate must not execute
transformation implementations. Commands that may cause external effects must
say so clearly and support a dry-run mode where meaningful.

## See Also

- [Configuration](CONFIGURATION.md)
- [Diagnostics](DIAGNOSTICS.md)
- [Environment Variables](ENVIRONMENT_VARIABLES.md)
- [Execution Model](../06_EXECUTION/EXECUTION_MODEL.md)

