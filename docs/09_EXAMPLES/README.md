# Examples

The repository's current runnable examples live in the top-level `examples/`
directory.

## Runnable in 0.5

### In-memory quickstart

```bash
python examples/quickstart.py
```

This example covers typed contracts, a local Python implementation, validation,
planning, execution, a run report, and output inspection. It is executed by
the test suite.

The Getting Started [Quickstart](../01_GETTING_STARTED/QUICKSTART.md) contains
the same workflow as a copy-pasteable single-file tutorial.

### Dataframe parity (Polars / Pandas)

```bash
# requires pipelantic-polars / pipelantic-pandas
python examples/dataframe_parity.py polars
python examples/dataframe_parity.py pandas
```

## Future design examples

The remaining pages in this section explore intended integrations and advanced
workflows. They are retained as design material and may contain APIs, packages,
or commands that do not exist yet.

| Topic | 0.5 status |
|---|---|
| CSV and JSON through built-in storage | Core capability; use the storage guide |
| Pandas and Polars pipelines | Available via `pipelantic-pandas` / `pipelantic-polars` |
| SQL execution and pushdown | Future plugin design |
| PySpark and streaming | Future plugin design |
| Airflow compilation | Future plugin design |
| Generated Graphviz/HTML documentation | Future design |

Do not use a future design page as an installation or API reference. The
[capabilities page](../01_GETTING_STARTED/CAPABILITIES.md) and
[API reference](../10_REFERENCE/API_REFERENCE.md) define the current boundary.
