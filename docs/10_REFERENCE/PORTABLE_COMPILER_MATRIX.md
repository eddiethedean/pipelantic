# Portable Compiler Matrix

This matrix records the portable transformation claims shipped in ETLantic
0.15.0. It is narrower than each backend's native capabilities.

## Compiler claims

| Package | Engine | Claimed profiles | Execution mode | Join collision policy |
|---|---|---|---|---|
| `etlantic-polars==0.16.0` | Polars | `portable-relational-kernel/1`, `portable-relational/1` | Eager and lazy | `fail` only |
| `etlantic-pyspark==0.16.0` | PySpark | `portable-relational-kernel/1`, `portable-relational/1` | Eager and lazy | `fail` only |
| `etlantic-pandas==0.16.0` | Pandas | `portable-relational-kernel/1`, `portable-relational/1` | Eager only (`lazy=False`) | `fail` only |
| `etlantic-sql==0.16.0` | SQL | `portable-relational-kernel/1`, `portable-relational/1` | Eager (relation/SQL) | `fail` only |

The full profile identifiers are
`dtcs:profile/portable-relational-kernel/1` and
`dtcs:profile/portable-relational/1`. The compilers read
`dtcs.transform-plan/2` and readable v1 plans. Candidate `/2` profile metadata
is treated as an alias of the corresponding `/1` claim; this does not add
candidate extensions.

## Claimed operations

All four compilers advertise the same 0.16.0 action surface:

| Profile group | Actions |
|---|---|
| Kernel | `filter`, `project`, `with_fields`, `drop_fields`, `rename_fields` |
| Relational | `join`, `union`, `aggregate`, `sort`, `distinct`, `deduplicate`, `limit` |

The shared scalar function claim includes lower/upper, concatenation, substring
and replacement, length and string predicates, conditional/null functions, and
common numeric functions. Relational aggregates include sum, average, min,
max, count, count-all, and count-distinct. Exact claims are available at
runtime from `compiler.info.capabilities`; use those records instead of
assuming backend-wide compatibility.

Supported join types are `inner`, `left`, `right`, `full`, `outer`, `semi`,
`anti`, and `cross`. For portable plans, `collisionPolicy` must be `fail`.
Suffixing or coalescing colliding non-key columns is outside the claim and
fails during analysis.

## Boundaries

- Pandas portable execution is eager. A plan requiring lazy execution is
  rejected.
- Polars and PySpark preserve backend-visible lazy operations where supported.
- SQL portable lowering targets typed `etlantic.sql/1` with bound parameters
  only. Trusted SQL fragments are forbidden in portable definitions. The
  PostgreSQL dialect is the reference; SQLite is a local convenience path.
- Windows, complex values/types, reshape, advanced conversion/statistics, and
  extended relational profiles are not claimed (0.15 continuation backlog).
- Unsupported actions, functions, modes, and profiles must fail closed during
  support analysis. Compilers do not silently fall back to UDFs or raw SQL.

## Verify claims

The public conformance suite selects fixtures from the advertised capability
record:

```python
from etlantic.testing import run_portable_transform_conformance_suite
from etlantic_sql import create_transform_compiler

run_portable_transform_conformance_suite(create_transform_compiler())
```

Official Polars, PySpark, Pandas, and SQL compilers run this suite in CI,
along with cross-engine differential tests. Third-party compilers must run it
for every advertised profile and operation.

See [Portable Transformation Compiler Protocol](../07_PLUGIN_SDK/PORTABLE_TRANSFORM_COMPILER.md),
[Third-Party Compiler Tutorial](../07_PLUGIN_SDK/THIRD_PARTY_COMPILER_TUTORIAL.md),
and [Compatibility](COMPATIBILITY.md).
