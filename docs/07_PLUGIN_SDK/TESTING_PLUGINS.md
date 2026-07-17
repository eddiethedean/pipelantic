# Testing Plugins

> **Status: Available in ETLantic 0.9+** via `etlantic.testing`.

Testing helpers provide conformance suites so third-party plugins can prove
they implement the public protocols correctly.

## Shipped suites

| Suite | Module | Use for |
|---|---|---|
| Dataframe conformance | `etlantic.testing.run_conformance_suite` | Polars/Pandas-style plugins |
| SQL conformance | `etlantic.testing.run_sql_conformance_suite` | `SqlPlugin` |
| Orchestrator conformance | `etlantic.testing.run_orchestrator_conformance_suite` | `OrchestratorPlugin` |
| Secret conformance | `etlantic.testing.run_secret_conformance_suite` | `SecretProvider` |
| Write-semantics parity | `etlantic.testing.run_write_semantics_parity_suite` | Cross-engine write modes |

Example:

```python
from etlantic.testing import run_conformance_suite

run_conformance_suite(my_plugin, engine="my-engine", sample_rows=rows)
```

```python
from etlantic.testing import run_sql_conformance_suite

run_sql_conformance_suite(my_sql_plugin)
```

## Philosophy

Every plugin should be tested against the same expectations:

```text
Plugin
   │
   ▼
SDK Conformance Suite
   │
   ├── Discovery / registration
   ├── Capability advertisement
   ├── Semantic behavior
   └── Failure / diagnostic shape
```

A plugin that passes the matching suite should behave predictably with
ETLantic planning and runtime.

## Future design

Portable transform compiler conformance
(`etlantic.testing.portable_transform_conformance`) is planned with the 0.11+
portable kernel. Do not require it for 0.10 plugins.

## Next Step

See [Dataframe Plugin](DATAFRAME_PLUGIN.md), [SQL Plugin](SQL_PLUGIN.md),
[Orchestrator Plugin](ORCHESTRATOR_PLUGIN.md), and
[Secret Provider](SECRET_PROVIDER.md) for protocol details.
