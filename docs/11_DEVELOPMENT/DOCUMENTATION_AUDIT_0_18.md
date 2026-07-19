> Status: Maintained audit for ETLantic 0.18.0 documentation adoption cut.

# Critical Documentation Audit — ETLantic 0.18

This audit records the documentation condition after the 0.18 adoption
remediation. It succeeds
[DOCUMENTATION_AUDIT_0_17.md](DOCUMENTATION_AUDIT_0_17.md) as the maintained
release artifact. Reassess when release posture or public package behavior
changes.

## Executive Summary

- **Overall documentation quality: Good (after remediation; was Fair).**
- **Would I personally trust this project based on the documentation?** Yes,
  for evaluation and documented single-tenant reference deployments, after
  validating selected plugins against Capabilities and Production readiness.
- **Why?** The green path is one four-step sequence; adopter-facing 0.17 labels
  were corrected; ROADMAP_SUMMARY attributes portable graduation to 0.17 and
  Gate A interchange to 0.18; Design Studies live under “not shipped”; a Gate A
  runnable example and production profile starter exist; Compare / Engine
  selection / Cookbook pages reduce category confusion.

## Remediated in this cut

1. ROADMAP_SUMMARY factual attribution (0.17 portable vs 0.18 Gate A)
2. FAQ / Evaluator / SECURITY / PRODUCTION_READINESS / DEPLOYMENT 0.18 labels
3. CAPABILITIES “Not included” contradiction for advanced portable profiles
4. Docs home and README landing status walls collapsed; canonical green path
5. CLI validate/plan vs Python seeded-run clarification
6. Design Studies moved under Design Proposals (not shipped) in `mkdocs.yml`
7. Plugin SDK and Integrations nav overview-first; migrations archived
8. `examples/interchange_polars_pandas.py` + docs companion; CI in portable job
9. `profiles/prod.example.json` linked from Capabilities / Evaluator / Cookbook
10. Compare, Engine selection, Cookbook pages
11. Extract/Load vocabulary on Pipelines / Architecture / Glossary
12. SQL examples use public `sqlalchemy.create_engine` (not `plugin._get_engine`)
13. `scripts/test_core.sh` + CONTRIBUTING shortcut
14. Diagnostics catalog generator; API author essentials + `reliability_runtime`
15. `check_docs.py` bans adopter-facing “Status in 0.17” / ROADMAP misattribution
16. Future Plugin SDK pages carry Future design banners; CONFIGURATION rebased

## Remaining / follow-up

- Full Google-style Examples on every public symbol (partial: Pipeline /
  Transformation essentials improved)
- Exhaustive human-curated diagnostic meanings for every generated code
- Slim multi-file sample project beyond single scripts
- Interim SBOM/signing adopter guidance while Gaps remain
- Broader CI execution of `file_storage.py` / `portable_*.py` (docs now label
  CI vs local accurately)

## Adoption readiness (post-cut target)

| Category | Target |
|---|---|
| Clarity | 8 |
| Completeness | 8 |
| Discoverability | 7 |
| Learnability | 8 |
| API documentation | 7 |
| Examples | 8 |
| Contributor experience | 8 |
| Professionalism | 8 |
