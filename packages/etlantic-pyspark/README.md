# etlantic-pyspark

PySpark reference execution plugin for [ETLantic](https://github.com/eddiethedean/etlantic).

```bash
pip install etlantic-pyspark
# or: pip install 'etlantic[pyspark]'
# optional Delta Lake support:
pip install 'etlantic-pyspark[delta]'
```

## Wiring

```python
from etlantic import Profile

Profile(name="spark-local", spark_engine="pyspark")
```

Register `@Transformation.implementation("pyspark")` handlers that take
Spark DataFrames (or lists of contract models) and return Spark DataFrames.

## Capabilities (0.7)

- Lazy Spark region fusion with preserved logical identities
- Local Spark provider (`local[*]`) — secrets resolved only at session acquire
- Native-expression preference with UDF policy diagnostics
- Contract ↔ Spark schema mapping (lossy/unknown never guessed)
- Valid/invalid row separation
- Delta-compatible write intents (append/overwrite/merge) when Delta is enabled
- Structured Streaming foundation (**experimental**)

**Not included:** managed cloud providers (Databricks/EMR/Connect), Airflow
compilation (0.8), SparkForge migration (0.10).
