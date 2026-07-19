# Performance Guidance

ETLantic 0.17 makes no capacity, throughput, or latency claims beyond the
documented smoke baselines. Those results prove that a small reference harness
completed in one recorded environment; they are not production sizing data.

See [Performance Baselines](PERFORMANCE_RESULTS.md) for the current evidence,
environment details, and reporting requirements.

## Run the local harness

The repository includes a dataframe correctness and timing harness:

```bash
uv sync --group dataframes
uv run python benchmarks/dataframe_scale.py polars
uv run python benchmarks/dataframe_scale.py pandas
```

Record the commit, Python and dependency versions, hardware, operating system,
dataset shape, warm-ups, samples, median, p95, and raw results. Do not compare
results from unlike environments as if they were controlled benchmarks.

## Measure your workload

Benchmark representative graphs, data shapes, I/O, concurrency, and failure
paths on the engines and infrastructure you will deploy. ETLantic plans are
data-only coordination artifacts: plan construction is free of backend
execution, but not literally zero-cost. Planning does not read source rows or
execute transformations. Execution cost belongs primarily to the selected
dataframe, SQL, Spark, storage, and orchestration backends.

Separate validation and planning overhead from backend execution and I/O when
reporting results. See [Benchmark Design](BENCHMARKS.md) for methodology.
