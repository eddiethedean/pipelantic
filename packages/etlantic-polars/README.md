# etlantic-polars

Polars reference dataframe plugin for [ETLantic](https://github.com/eddiethedean/etlantic).

```bash
pip install etlantic-polars
# optional Arrow interchange
pip install 'etlantic-polars[arrow]'
```

Supports eager `DataFrame` execution and `LazyFrame` preservation until an
explicit collection boundary declared in the `PipelinePlan`.
