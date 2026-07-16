# Secrets Management

> **Available in 0.5:** `env` and mounted-file secret providers only.
> AWS Secrets Manager, Vault, keyring, and cloud identity providers are
> **future design**—do not configure them yet.

ETLantic treats secrets as runtime dependencies that are referenced during
configuration and resolved only inside an authorized execution boundary.

ETLantic is not a secret store. Plans stay secret-free: they may contain a
`SecretRef`, never a resolved value. Values must not appear in contracts,
`PipelinePlan`, logs, diagnostics, events, reports, caches, or tracebacks.

## Shipped in 0.5

### Secret references

```python
from etlantic import SecretRef

warehouse_password = SecretRef(
    provider="ci-secrets",
    name="WAREHOUSE_PASSWORD",
)
```

| Field | Meaning |
|---|---|
| `provider` | Logical provider name configured on the runtime |
| `name` | Provider-specific secret identifier |
| `key` | Optional field within a structured secret (when supported) |
| `version` | Optional version hint (provider-specific) |

### Environment provider

```python
from etlantic.secrets import EnvSecretProvider

provider = EnvSecretProvider(prefix="ETLANTIC_SECRET_")
# Resolves SecretRef(name="WAREHOUSE_PASSWORD") from
# ETLANTIC_SECRET_WAREHOUSE_PASSWORD
```

Use environment variables for CI and local smoke tests. Prefer a real secret
manager in production once provider plugins ship.

### Mounted-file provider

```python
from etlantic.secrets import MountedFileSecretProvider

provider = MountedFileSecretProvider(root="/var/run/secrets")
# Resolves SecretRef(name="warehouse_password") from a file under root
```

Useful for Kubernetes/container secret mounts. Paths are bounded to the
configured root (fail closed on traversal).

### SecretValue

Resolved secrets use `SecretValue`:

- `repr()` / `str()` are redacted
- normal serialization is refused
- equality and hashing do not expose the underlying value

### Resolution rules

- Planning must not resolve secrets
- Missing or unreadable secrets fail closed at runtime
- Redact exception messages before they enter reports or logs

## Future providers (not installable in 0.5)

The following belong in later Plugin SDK milestones. Configuration examples
that mention them are design sketches only:

| Target environment | Intended provider |
|---|---|
| Developer workstation | `keyring` |
| AWS | Secrets Manager (`boto3`) |
| Azure | Key Vault |
| Google Cloud | Secret Manager |
| HashiCorp Vault | `hvac` |
| 1Password | official SDK |

See the [Secret Provider SDK](../07_PLUGIN_SDK/SECRET_PROVIDER.md) (future
design) for the intended plugin shape.

## See Also

- [Security Model](../02_FOUNDATIONS/SECURITY.md)
- [Security policy](https://github.com/eddiethedean/etlantic/blob/main/SECURITY.md)
- [Local Python](LOCAL_PYTHON.md)
- [Compatibility](../10_REFERENCE/COMPATIBILITY.md)
