# API Stability and Deprecation Policy

ETLantic 0.17.0 is production/stable for documented single-tenant reference
deployments, while remaining pre-1.0. Breaking changes remain possible, but
they must not be silent.

## Stability levels

| Surface | Current promise |
|---|---|
| Documented 0.17 public imports | Supported for the 0.17.x line |
| Versioned plugin protocols | Compatible within their documented protocol version |
| Pipeline Plan schema | Governed by its schema version |
| Experimental APIs | May change in any 0.x release |
| Design proposals | No compatibility promise |
| Private underscore modules | No compatibility promise |

## Breaking-change requirements

A breaking 0.x change requires a changelog entry, migration guide, before/after
example, affected plugin/protocol analysis, and tests that make the new boundary
explicit. Persistent plans should normally be regenerated.

## Deprecation behavior

When practical, a replacement is documented and a warning is emitted for at
least one release before removal. Security fixes may shorten that window.
After 1.0, incompatible public API removal requires a major release unless a
documented security exception applies.

## Removed in 0.16 (authoring vocabulary)

| Removed | Replacement |
|---|---|
| `Source` / `Sink` | `Extract` / `Load` |
| `binding=` on extract/load constructors | `asset=` |
| `.binding` property | `.asset` |
| `Profile(bindings=...)` / mirrored public JSON `bindings` | `Profile(assets=...)` |
| `RunRequest.binding_overrides` | `asset_overrides` |

Wire names intentionally **kept**: plan/graph `binding`,
`NodeKind` `"source"`/`"sink"`, DPCS `etlantic:binding`, plugin
`*_from_binding`, and port-wiring `Step.bindings`. See
[Migration 0.15 → 0.16](MIGRATION_0_15_TO_0_16.md).
