# Migration 0.11 → 0.12

ETLantic **0.12.0** adds portable planning policy and Polars **kernel**
portable compilation. Authoring from 0.11 (`@Transformation.portable`) is
unchanged; execution and plan evidence grow.

## Install

Pin exact versions for reproducible evaluation:

```bash
pip install 'etlantic==0.12.0' 'etlantic-polars==0.12.0'
```

Official plugins share the same published minor. Upgrade core and plugins
together.

## What changed

| Area | 0.11 | 0.12 |
|---|---|---|
| Portable authoring | Available | Unchanged |
| `Profile.portable_transform_policy` | N/A | `prefer` (default) / `require` / `native` |
| Plan implementation kind | Native callables | Also `portable_compiled` |
| Polars kernel execution without `@implementation("polars")` | No | Yes via `etlantic-polars` |
| Diagnostics | Authoring `PMXFORM*` | Plus planning `PMXFORM3xx` |

## Policy defaults

```python
from etlantic import Profile

# Default when omitted: prefer portable when a compiler covers the plan;
# otherwise fall back to a real native implementation with fallback_reason.
Profile(name="dev", dataframe_engine="polars")

# Fail closed if portable requirements are unsupported:
Profile(
    name="portable-eval",
    dataframe_engine="polars",
    portable_transform_policy="require",
)

# Ignore portable compilers; use native callables only:
Profile(
    name="native-only",
    dataframe_engine="polars",
    portable_transform_policy="native",
)
```

## Plan evidence

After planning, steps selected for portable compilation expose:

- `ImplementationDescriptor.kind == "portable_compiled"`
- `compiler_name` / `compiler_version` / `compiler_protocol`
- `ir_fingerprint` and embedded `portable_plan`
- `requirements` and `support_summary`

Inspect with `etlantic plan … --format json` or `explain_plan(plan)`.

## Allowlisting

Production profiles still require a non-empty `Profile.plugin_allowlist`.
Include both the dataframe plugin and, when using portable compilation, the
compiler package name:

```python
Profile(
    name="production",
    dataframe_engine="polars",
    portable_transform_policy="require",
    plugin_allowlist={
        "etlantic-polars": "==0.12.0",
    },
)
```

Allowlists select which discovered plugins may be used; they are **not** an
import-time sandbox. Install only trusted packages in the runtime environment.

## Failure modes

| Symptom | Cause | Action |
|---|---|---|
| `PMXFORM301` unsupported action/function/profile | Plan exceeds Polars kernel claim | Narrow the portable definition, add a native `@implementation`, or use `prefer`/`native` |
| `PMXFORM302` no transform compiler | `etlantic-polars` missing or not discoverable | Install matching plugin; verify entry point `etlantic.transform_compilers` |
| Phantom “native” for wrong engine | Fixed in 0.12.0 — upgrade | Re-plan after upgrade |

## Rollback

1. Pin `etlantic==0.11.x` and matching plugins.
2. Set `portable_transform_policy="native"` if staying on 0.12 temporarily.
3. Keep native `@implementation(...)` callables for engines you still need.

## Compatibility notes

- Output IR schemas now preserve contract field types when projecting named
  fields (fingerprint-affecting for portable plans).
- Project expression fields without aliases receive stable `_col_N` names.
- Window metadata on kernel plans fails closed (window profiles are not claimed
  in 0.12).

## See also

- [Portable Transformations](../04_TRANSFORMATIONS/PORTABLE_TRANSFORMATIONS.md)
- [Portable Transform Compiler](../07_PLUGIN_SDK/PORTABLE_TRANSFORM_COMPILER.md)
- [`examples/portable_polars_kernel.py`](https://github.com/eddiethedean/etlantic/blob/main/examples/portable_polars_kernel.py)
- [Capabilities](../01_GETTING_STARTED/CAPABILITIES.md)
