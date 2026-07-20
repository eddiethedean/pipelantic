# What's New in 0.20

> **Status: Available in ETLantic 0.20.0.** Trust, Isolation, and Safe I/O.

ETLantic 0.20.0 authorizes plugins and external effects before executable code
or mutable resources cross the analysis boundary.

## Breaking for you if…

- Production profiles discover plugins without static
  `etlantic-plugin-manifest.json` metadata → fail closed (`PMPLUG413`).
- Outbound `Emit` metadata includes `url` / `destination` / `webhook` without
  an allowlisted host in `Profile.outbound` → denied (`PMSEC050`).
- Artifact/cache identity strings now embed tenant, environment, and
  authorization segments — regenerate plans after upgrade.
- Plugin packages must pin `etlantic>=0.20.0,<0.21`.

```python
from etlantic import Profile

prod = Profile(
    name="prod-east",
    security_mode="production",
    tenant="acme",
    environment="prod",
    plugin_allowlist={"etlantic-polars": "==0.20.0"},
    outbound={
        "allowed_schemes": ["https"],
        "allowed_hosts": ["hooks.example.com"],
    },
    safe_io={"max_read_bytes": 10_485_760},
)
```

Full steps: [Migration 0.19 → 0.20](../11_DEVELOPMENT/MIGRATION_0_19_TO_0_20.md).

## Trust and plugin lifecycle

- Deterministic `discover → evaluate → authorize → load` phases
- Static `etlantic.plugin_manifest/1` inspectable without importing entry points
- Allowlist / pin / provenance / digest checks before `ep.load()`
- Optional isolated capability probe (containment, not a sandbox)
- Versioned `SecurityEvent` records for authorization decisions

## Safe I/O and isolation

- Unified `SafeIoPolicy` for contracts, profiles, reports, schema history,
  artifacts, and caches
- Approved roots, symlink rejection, special-file rejection, bounded reads,
  atomic writes, locking, integrity digests
- Artifact/cache identities include run, tenant, environment, security domain,
  authorization, compiler fingerprint, and contract version

## Outbound and serialization

- Default-deny outbound / webhook / remote-reference policy (SSRF controls)
- Unsafe serialization formats (pickle/joblib/…) prohibited at loaders

## Supply chain

- Release workflow emits artifact digests / CycloneDX SBOM when available
- GitHub build provenance attestations
- OIDC trusted publishing preferred; token publish remains residual bootstrap

## Exit-gate matrix

See [EXIT_GATE_0_20](../11_DEVELOPMENT/EXIT_GATE_0_20.md).

## Upgrade

See [Migration 0.19 → 0.20](../11_DEVELOPMENT/MIGRATION_0_19_TO_0_20.md).
