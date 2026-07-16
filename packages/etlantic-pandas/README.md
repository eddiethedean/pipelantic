# etlantic-pandas

Pandas compatibility dataframe plugin for [ETLantic](https://github.com/eddiethedean/etlantic).

```bash
pip install etlantic-pandas
pip install 'etlantic-pandas[arrow]'  # optional Arrow interchange
```

Eager `DataFrame` execution only. Planning fails closed when a pipeline
requires unsupported lazy or zero-copy behavior.
