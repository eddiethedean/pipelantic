# Migration 0.18 → 0.19

**Status:** required for production profiles, persisted plans/reports, and
named profile resolution.

## Install

```bash
pip install -U 'etlantic==0.19.0'
# match official plugins to the same minor
pip install -U 'etlantic-polars==0.19.0'  # etc.
```

Official plugins require `etlantic>=0.19.0,<0.20`.

## Profile security_mode

Production fail-closed trust and schema-drift BLOCK now use
`Profile.security_mode == "production"` only. Profile **names** and
`security_domain` are labels.

```python
from etlantic import Profile

prod = Profile(
    name="prod-east",
    security_mode="production",
    plugin_allowlist={"local": None, "etlantic-polars": "==0.19.0"},
)
```

Built-in templates set the mode correctly (`production_profile()`,
`development_profile()`, `test_profile()`). Profile JSON missing
`security_mode` is inferred once for migration; write `security_mode`
explicitly going forward.

## Strict profile names

Unknown bare profile names fail closed:

```bash
etlantic validate pipeline.py:P --profile typo   # error PMCFG100
etlantic validate pipeline.py:P --profile typo --allow-adhoc-profile
```

SDK: `resolve_profile("typo", allow_adhoc_profile=True)`.

## Legacy bindings JSON

Loading profile JSON that only has `bindings` emits `PMCFG110` and still
loads. Prefer `assets`. Fail closed with
`Profile.from_dict(data, accept_legacy_bindings=False)`.

## Plan / report schema

`PipelinePlan` and `PipelineRunReport` JSON must include
`schema: "etlantic.plan/1"` or `schema: "etlantic.run_report/1"`. Missing or
unknown values raise. Fingerprints are verified on deserialize (default) and
again before compile/run.

## Checklist

- [ ] Upgrade core and official plugins to `0.19.0`
- [ ] Set `security_mode` on production Profile JSON
- [ ] Replace ad hoc profile names or pass `--allow-adhoc-profile`
- [ ] Migrate profile JSON `bindings` → `assets`
- [ ] Regenerate persisted plans if nested metadata warnings appear
- [ ] Re-run validate/plan in CI with SARIF
