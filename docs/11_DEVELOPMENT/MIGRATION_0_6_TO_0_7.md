# Migration: 0.6 → 0.7

ETLantic 0.7 adds distributed Spark execution. Core remains Spark-free.

## Install

```bash
pip install 'etlantic>=0.7'
pip install etlantic-pyspark          # optional
# or: pip install 'etlantic[pyspark]'
```

## Profile

```python
from etlantic import Profile

Profile(
    name="spark-local",
    spark_engine="pyspark",
    spark_udf_policy="warn",       # allow | warn | native_required | deny
    spark_streaming=False,         # experimental when True
    required_spark_capabilities=("spark_delta",),  # optional fail-closed
)
```

`spark_engine` takes precedence over `sql_engine` and `dataframe_engine` when set.

## Implementations

```python
@NormalizeCustomers.implementation("pyspark")
def normalize(customers):
    ...
```

## Streaming

Structured Streaming APIs are **experimental** in 0.7
(`etlantic.STREAMING_STABILITY == "experimental"`). Batch-only
transformations are rejected from streaming regions (`PMSPARK320`).

## Breaking / compatibility

- Plugin packages bump to `0.7.0` and require `etlantic>=0.7.0,<0.8`.
- Planner metadata includes `spark_protocol` / `spark_fusion`.
- No change to portable `Data` / `Transformation` / `Pipeline` authoring.
