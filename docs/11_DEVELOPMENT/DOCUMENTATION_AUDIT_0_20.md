> Status: Maintained audit for ETLantic 0.20.0 documentation adoption cut.

# Critical Documentation Audit — ETLantic 0.20

This audit records the documentation condition after the 0.20 adoption
remediation. It succeeds
[DOCUMENTATION_AUDIT_0_18.md](DOCUMENTATION_AUDIT_0_18.md) as the maintained
release artifact. Reassess when release posture or public package behavior
changes.

## Executive Summary

- **Overall documentation quality: Good.**
- **Would I personally trust this project based on the documentation?** Yes,
  for evaluation and documented single-tenant reference deployments, after
  reading Capabilities, Evaluator, and Production readiness.
- **Why?** The green path remains strong; 0.20 upgrade hub, status vocabulary,
  and profile-default callouts were refreshed; Gate A ship version is
  canonicalized at 0.18.0; design proposals were demoted under Project.

## Remediated in 0.20 pass

1. `UPGRADE.md` — 0.19→0.20 migration row, decision tree, 0.20 config cheat sheet
2. Status vocabulary — **Available in 0.20** / **0.20 reference envelope** on adopter pages
3. Stale `0.19.0` pin examples fixed in Installation and First Pipeline
4. README aligned with CI-tested `examples/quickstart.py`; CLI `pipeline.py` step added
5. COMPARE vs Capabilities SBOM/attestation language reconciled
6. Gate A ship version canonicalized (0.18.0, current in 0.20)
7. CLI profile default callout (`local` vs tutorial `development`)
8. Contributor install — uv canonical; removed broken pip `.[dev]` path
9. `check_docs.py` — stale milestone phrase bans and adopter-page assertions
10. PyPI core classifier — **Beta** (matches qualified stability claims)
11. Nav — duplicate What's New 0.20 removed from Learn; changelog rendered on site
12. Design Proposals demoted from top-level nav to Project section
13. Docs home validation block simplified (less jargon before quickstart)

## Remaining debt (not blocking 0.20 docs gate)

- Versioned docs site per release (Read the Docs `/0.20/` snapshot)
- User-facing performance summary (maintainer page linked from Execution tutorials)
- Profile primer page (`local` vs `development` vs production JSON)
- Architecture “0.20 delta” section distilled from Security + migration guides
- Search indexing still includes design studies (nav demoted only)

## Release documentation gate checklist

Before tagging a minor/patch docs cut:

- [ ] Grep adopter pages for stale pins (`0.19.0` as current example)
- [ ] Confirm `UPGRADE.md` links the latest from→to migration guide
- [ ] Run `uv run python scripts/check_docs.py`
- [ ] Run `uv run python scripts/build_docs.py`
- [ ] Confirm green path: Install → Quickstart → First Pipeline → Engine selection
- [ ] Confirm README quickstart matches `examples/quickstart.py`
- [ ] Update this audit or append a dated addendum for the release
