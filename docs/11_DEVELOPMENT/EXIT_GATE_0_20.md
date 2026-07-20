# Exit gate 0.20 — Trust, Isolation, and Safe I/O

Every mandatory trust and I/O control has an implementation owner, automated
verification, a stable diagnostic or event, and documented residual risk.

| Control | Owner module | Automated verification | Diagnostic / event | Residual risk |
|---|---|---|---|---|
| Pre-import plugin authorize | `etlantic.plugin_lifecycle` | `tests/unit/test_trust_isolation_0_20.py` | `PMPLUG401`/`402`, `plugin_authorization` | Contained probes are not a full sandbox |
| Static plugin manifest | `etlantic.plugin_manifest` | same + first-party manifest files | `PMPLUG410`–`420` | Third-party plugins must ship manifests |
| Capability probe | `etlantic.capability_probe` | unit + optional runtime | `PMPLUG430`–`432`, `capability_probe` | Time/output budgets only; not OS sandbox |
| Safe filesystem I/O | `etlantic.io_policy` | safe-I/O unit tests | `PMSRC101`–`113`, `safe_io` | Kernel/FS race windows outside ETLantic |
| Artifact/cache isolation | `etlantic.plan.artifacts` | identity unit tests | `ETLanticError` on mismatch | Callers must pass tenant/env consistently |
| Outbound / SSRF policy | `etlantic.outbound` | outbound unit tests | `PMSEC050`/`051`, `outbound_*` | DNS rebinding after check requires resolver controls |
| Unsafe serialization ban | `etlantic.serialization_policy` | serialization unit tests | `PMSEC060` | Plugins must not bypass via native code |
| Versioned security events | `etlantic.runtime.events` | event schema assertions | `etlantic.security_event/1` | In-process bus only (no remote SIEM) |
| Release SBOM / attest / OIDC | `.github/workflows/release.yml` | release workflow | GitHub attestations + digests | Token publish may remain as bootstrap |

## Acceptance scenarios (ROADMAP)

1. Disallowed installed plugin rejected without importing its entry point — covered.
2. Manifest tampering / mismatch / duplicate stop plan/run with stable diagnostics — covered.
3. Traversal, symlink escape, special files, partial writes, oversized inputs, concurrent writers fail safely — covered by `SafeIoPolicy`.
4. Cross-tenant/run/env/domain artifacts cannot be selected via collision — covered by identity helpers.
5. Loopback / link-local / metadata / private / unapproved outbound rejected by default — covered.
6. Plans, reports, diagnostics, audit events contain no resolved secrets or source rows — preserved from 0.19 + event metadata policy.
