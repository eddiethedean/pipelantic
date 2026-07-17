# Governance

ETLantic currently uses a maintainer-led governance model.

## Decision authority

Maintainers accept changes based on user value, correctness, compatibility,
security, architectural ownership, and maintenance cost. The repository's
public code, tests, accepted ADRs, and published standards are authoritative;
roadmap dates and design studies are not commitments.

## Change classes

| Change | Required evidence |
|---|---|
| Documentation correction | Source or executable behavior |
| Compatible implementation | Tests and affected docs |
| Public API addition | Two concrete consumers or one end-to-end workflow |
| Plugin protocol change | Compatibility analysis and conformance tests |
| Persistent format/contract change | Versioning and migration path |
| Difficult-to-reverse architecture | ADR and maintainer approval |

## Conflicts of authority

- ODCS, DTCS, and DPCS specifications own contract meaning.
- ETLantic owns logical modeling, validation, and planning behavior.
- Plugins own backend realization.
- Code and tests supersede stale narrative documentation for a shipped release.

Maintainers should document rejected alternatives when a decision materially
constrains third-party plugins or persistent artifacts.
