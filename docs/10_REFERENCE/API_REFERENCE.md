# Python API Reference

> **Status: Available in ETLantic 0.10.0.** Signatures and docstrings below
> are generated from the package source.

## Start here by persona

| Persona | Start with | Then |
|---|---|---|
| Pipeline author | Root imports below, [CLI](CLI.md) | `etlantic.pipeline`, `etlantic.plan`, `etlantic.reports` |
| Plugin author | `etlantic.dataframe` / `.sql` / `.spark` / `.orchestration` / `.secrets` | [Testing](#testing-helpers), [Plugin SDK](../07_PLUGIN_SDK/README.md) |
| CI / ops | [CLI](CLI.md), [Runtime configuration](RUNTIME_CONFIGURATION.md) | `etlantic.plugin_trust`, SARIF validate |

The package root is the supported convenience import surface for common
authoring, planning, runtime, storage, report, secret, and interchange types:

```python
from etlantic import (
    Data,
    Input,
    Output,
    Parameter,
    Pipeline,
    PipelineRuntime,
    Sink,
    Source,
    Transformation,
)
```

`DataContractModel` is a deprecated alias for `Data`.

## Authoring

!!! note "Proposed 0.11+ portable authoring API"
    `etlantic.transform`, `@Transformation.portable`, symbolic DataFrame and
    Column objects, and `functions as F` are accepted future design and are not
    importable in ETLantic 0.10. See
    [Portable Transformations](../04_TRANSFORMATIONS/PORTABLE_TRANSFORMATIONS.md).

### Data contracts

::: etlantic.contracts
    options:
      show_root_heading: true
      members_order: source
      filters: ["!^_"]

### Transformations

::: etlantic.transformation
    options:
      show_root_heading: true
      members_order: source
      filters: ["!^_"]

### Pipelines

::: etlantic.pipeline
    options:
      show_root_heading: true
      members_order: source
      filters: ["!^_"]

### Ports and references

::: etlantic.ports
    options:
      show_root_heading: true
      members_order: source
      filters: ["!^_"]

::: etlantic.refs
    options:
      show_root_heading: true
      members_order: source
      filters: ["!^_"]

## Validation and diagnostics

::: etlantic.diagnostics
    options:
      show_root_heading: true
      members_order: source
      filters: ["!^_"]

::: etlantic.validation
    options:
      show_root_heading: true
      members_order: source
      filters: ["!^_"]

::: etlantic.policy
    options:
      show_root_heading: true
      members_order: source
      filters: ["!^_"]

## Profiles, planning, and registries

::: etlantic.profile
    options:
      show_root_heading: true
      members_order: source
      filters: ["!^_"]

::: etlantic.plan
    options:
      show_root_heading: true
      members_order: source
      filters: ["!^_"]

::: etlantic.registry
    options:
      show_root_heading: true
      members_order: source
      filters: ["!^_"]

::: etlantic.plugin_trust
    options:
      show_root_heading: true
      members_order: source
      filters: ["!^_"]

::: etlantic.model
    options:
      show_root_heading: true
      members_order: source
      filters: ["!^_"]

## Local runtime and reports

::: etlantic.runtime
    options:
      show_root_heading: true
      members_order: source
      filters: ["!^_"]

::: etlantic.lifecycle
    options:
      show_root_heading: true
      members_order: source
      filters: ["!^_"]

::: etlantic.reports
    options:
      show_root_heading: true
      members_order: source
      filters: ["!^_"]

## Storage and secrets

::: etlantic.storage
    options:
      show_root_heading: true
      members_order: source
      filters: ["!^_"]

::: etlantic.secrets
    options:
      show_root_heading: true
      members_order: source
      filters: ["!^_"]

## Contract interchange

::: etlantic.interchange
    options:
      show_root_heading: true
      members_order: source
      filters: ["!^_"]

## Dataframe protocol

::: etlantic.dataframe
    options:
      show_root_heading: true
      members_order: source
      filters: ["!^_"]

## SQL protocol

::: etlantic.sql
    options:
      show_root_heading: true
      members_order: source
      filters: ["!^_"]

## Spark protocol

::: etlantic.spark
    options:
      show_root_heading: true
      members_order: source
      filters: ["!^_"]

## Orchestration protocol

::: etlantic.orchestration
    options:
      show_root_heading: true
      members_order: source
      filters: ["!^_"]

## Visualization

::: etlantic.viz
    options:
      show_root_heading: true
      members_order: source
      filters: ["!^_"]

::: etlantic.mermaid
    options:
      show_root_heading: true
      members_order: source
      filters: ["!^_"]

## Agents, IDE, and notebooks

::: etlantic.agents
    options:
      show_root_heading: true
      members_order: source
      filters: ["!^_"]

::: etlantic.ide
    options:
      show_root_heading: true
      members_order: source
      filters: ["!^_"]

::: etlantic.notebook
    options:
      show_root_heading: true
      members_order: source
      filters: ["!^_"]

## Observability

::: etlantic.observability
    options:
      show_root_heading: true
      members_order: source
      filters: ["!^_"]

## Schema history

::: etlantic.schema_history
    options:
      show_root_heading: true
      members_order: source
      filters: ["!^_"]

## Capabilities

::: etlantic.capabilities
    options:
      show_root_heading: true
      members_order: source
      filters: ["!^_"]

## Reliability and schema drift

::: etlantic.reliability
    options:
      show_root_heading: true
      members_order: source
      filters: ["!^_"]

::: etlantic.schema_drift
    options:
      show_root_heading: true
      members_order: source
      filters: ["!^_"]

::: etlantic.schema_policy
    options:
      show_root_heading: true
      members_order: source
      filters: ["!^_"]

## Testing helpers

::: etlantic.testing
    options:
      show_root_heading: true
      members_order: source
      filters: ["!^_"]

## Exceptions

::: etlantic.exceptions
    options:
      show_root_heading: true
      members_order: source
      filters: ["!^_"]

## Stability

ETLantic is alpha. A root export is public in the current release, but 0.x
releases may change APIs. Review the changelog and
[compatibility matrix](COMPATIBILITY.md) before upgrading. Narrative CLI docs:
[CLI](CLI.md).
