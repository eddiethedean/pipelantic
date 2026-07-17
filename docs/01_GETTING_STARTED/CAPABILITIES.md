# Current Capabilities and Limitations

ETLantic 0.7.0 is an alpha release. This page is the shortest answer to
"What can I use today?"

## Available in 0.7

| Capability | Status |
|---|---|
| Typed data, transformation, and pipeline models | Available |
| Structural and semantic validation | Available |
| ODCS, DTCS, and DPCS generation and loading | Available |
| Profiles and deterministic, secret-free pipeline plans | Available |
| Local synchronous and asynchronous execution | Available |
| Python transformation implementations | Available |
| Memory, callable, JSON, CSV, and no-write storage | Available |
| Run reports, structured logging, and local debugging | Available |
| Runtime secret references and env/file providers | Available |
| Dataframe execution protocol (`etlantic.dataframe/1`) | Available |
| Polars plugin (eager + lazy preservation) | Available (`etlantic-polars`) |
| Pandas plugin (eager compatibility) | Available (`etlantic-pandas`) |
| Optional Arrow interchange | Available when PyArrow is installed |
| SQL execution protocol (`etlantic.sql/1`) | Available |
| SQL plugin (PostgreSQL reference) | Available (`etlantic-sql`) |
| Spark execution protocol (`etlantic.spark/1`) | Available |
| PySpark plugin + local Spark provider | Available (`etlantic-pyspark`) |
| Lazy Spark region fusion | Available |
| Delta-compatible write intents | Available (fail-closed without Delta) |
| Structured Streaming foundation | **Experimental** |
| Mermaid diagrams (`Pipeline.to_mermaid`) | Available |

## Not included in 0.7

| Capability | Status |
|---|---|
| `MERGE` / upsert in the reference SQL plugin | Not implemented (`sql_merge=False`; fail closed) |
| Managed Spark providers (Databricks/EMR/Connect) | Future / optional adapters |
| Airflow or other orchestrator compilation | Future design (0.8) |
| Public third-party Plugin SDK polish | Continues in 0.9 |
| SparkForge migration adapter | Future design (0.10) |
| Graphviz and generated HTML pipeline documentation | Future design |
| Stable 1.0 compatibility guarantees | Not yet |

## Install matrix

```bash
pip install etlantic                 # core only — no engines
pip install etlantic-polars          # Polars reference plugin
pip install etlantic-pandas          # Pandas compatibility plugin
pip install etlantic-sql             # PostgreSQL SQL reference plugin
pip install etlantic-pyspark         # PySpark reference plugin
pip install 'etlantic[sql]'          # same as etlantic-sql via extra
pip install 'etlantic[pyspark]'      # same as etlantic-pyspark via extra
pip install 'etlantic-polars[arrow]' # optional PyArrow
```

Core never imports Polars, Pandas, PyArrow, NumPy, database drivers, or PySpark.

Select Spark with `Profile(spark_engine="pyspark")` and
`@Transformation.implementation("pyspark")`.

## Next Step

Continue with [Quickstart](QUICKSTART.md), or read the
[Evaluator brief](EVALUATOR.md) if you are assessing the project for adoption.
