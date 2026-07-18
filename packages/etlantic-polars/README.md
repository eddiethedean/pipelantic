# etlantic-polars

Polars dataframe plugin **and** Polars portable **kernel** transform compiler
for [ETLantic](https://github.com/eddiethedean/etlantic) 0.12.

```bash
pip install 'etlantic==0.12.0' 'etlantic-polars==0.12.0'
# optional Arrow interchange
pip install 'etlantic-polars[arrow]'
```

## Dataframe plugin

Supports eager `DataFrame` execution and `LazyFrame` preservation until an
explicit collection boundary declared in the `PipelinePlan`.

Entry point: `etlantic.dataframe_plugins` → `etlantic_polars:create_plugin`.

## Portable transform compiler (0.12)

Claims `dtcs:profile/portable-relational-kernel/1` and executes kernel actions
(`filter`, `project`, `with_fields`, `drop_fields`, `rename_fields`) plus the
kernel function set without a native `@implementation("polars")`.

```python
from etlantic import Profile
from etlantic_polars import create_transform_compiler

Profile(
    name="polars-portable",
    dataframe_engine="polars",
    portable_transform_policy="require",  # or prefer / native
)
compiler = create_transform_compiler()
print(compiler.info.name, sorted(compiler.info.capabilities.actions)[:3])
```

Entry point: `etlantic.transform_compilers` →
`etlantic_polars:create_transform_compiler`.

Runnable example: `examples/portable_polars_kernel.py` in the ETLantic repo.

Joins, windows, and conversion-profile functions remain unsupported until later
releases (0.13+). See the
[compiler protocol](https://etlantic.readthedocs.io/en/latest/07_PLUGIN_SDK/PORTABLE_TRANSFORM_COMPILER/)
and [compatibility matrix](https://etlantic.readthedocs.io/en/latest/10_REFERENCE/COMPATIBILITY/).
