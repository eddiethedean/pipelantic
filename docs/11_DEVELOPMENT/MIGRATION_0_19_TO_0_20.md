# Migration 0.19 → 0.20

ETLantic 0.20 adds pre-import plugin trust, unified safe I/O, artifact
isolation, outbound network policy, serialization bans, and release SBOM /
attestation support.

## 1. Bump packages

```bash
pip install 'etlantic==0.20.0'
# matching extras / plugins
pip install 'etlantic-polars==0.20.0' 'etlantic-pandas==0.20.0'
```

Plugin packages require `etlantic>=0.20.0,<0.21`.

## 2. Production plugin manifests

First-party plugins ship `etlantic-plugin-manifest.json`. Production
`security_mode="production"` requires a readable static manifest before
entry-point import. Third-party plugins must ship the same schema
(`etlantic.plugin_manifest/1`) or discovery fails closed.

## 3. Allowlists still required in production

```python
Profile(
    name="production",
    security_mode="production",
    plugin_allowlist={
        "etlantic-polars": "==0.20.0",
        "etlantic-sql": "==0.20.0",
    },
)
```

Allowlist evaluation now happens **before** `ep.load()`.

## 4. Outbound destinations

If transformations emit webhooks, declare allowlisted hosts:

```python
Profile(
    name="production",
    security_mode="production",
    plugin_allowlist={"local": None},
    outbound={
        "allowed_schemes": ["https"],
        "allowed_hosts": ["hooks.example.com"],
        "allow_redirects": False,
        "max_response_bytes": 1_048_576,
    },
)
```

Loopback, link-local, private, and metadata-service targets are denied by
default.

## 5. Regenerate plans

Artifact and cache identity strings gained isolation dimensions. Stored 0.19
plans remain loadable but should be regenerated so new identity keys and trust
records are recorded.

## 6. Safe I/O roots

Report and schema-history file stores now write through `SafeIoPolicy`. Ensure
store roots are intentional directories (not world-writable shared paths) and
avoid symlink farms that escape the root.

## Residual risk

- Process isolation for capability probes is containment, not a complete
  sandbox for untrusted Python (explicit product non-goal).
- OIDC trusted publishing is preferred; long-lived PyPI tokens may remain as
  bootstrap fallback until every distribution is configured for Trusted
  Publishing.
