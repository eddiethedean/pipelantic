# What's New in 0.19

> **Status: Available in ETLantic 0.19.0.** Contract and configuration freeze.

ETLantic 0.19.0 freezes the logical model and plan boundary into a precise,
versioned contract before further stable surface area.

## Contract and configuration freeze

- Deep plan immutability helpers and fingerprint verification at deserialize,
  compile, and run trust boundaries
- Explicit `Profile.security_mode` (`development` | `test` | `production`)
- Strict named profile resolution; unknown bare names fail closed unless
  `--allow-adhoc-profile` / `allow_adhoc_profile=True`
- Diagnosed legacy profile JSON `bindings` loads (`PMCFG110`)
- Plan and run-report loaders reject missing or unknown wire `schema` values
- Extension metadata namespace/budget helpers
- Public surface inventory and pre-1.0 deprecation schedule

## Experimental DataFusion (non-blocking)

Optional `etlantic-datafusion` may ship as **Experimental** Gate B. It does
not graduate as recommended in 0.19.0 and does not weaken the freeze gates.

## Upgrade

See [Migration 0.18 → 0.19](../11_DEVELOPMENT/MIGRATION_0_18_TO_0_19.md).
