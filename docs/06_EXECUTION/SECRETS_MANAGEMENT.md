# Secrets Management

Pipelantic treats secrets as runtime dependencies that are referenced during
configuration and resolved only inside an authorized execution boundary.

Pipelantic is not a secret store. It provides a portable reference model,
provider lifecycle, redaction rules, and policy checks while delegating storage,
authentication, rotation, and audit enforcement to external systems.

## Design Goals

Secrets management must:

- keep plaintext values out of source code and committed configuration;
- keep resolved values out of contracts, `PipelinePlan`, logs, diagnostics,
  events, reports, caches, tracebacks, and generated documentation;
- support local development and managed cloud or enterprise stores;
- use workload identity or managed identity where available;
- resolve values as late as possible and release them as early as possible;
- make provider, secret identity, version policy, and required permission
  inspectable without revealing the value;
- support rotation without rebuilding the logical pipeline.

## Secret References

Configuration stores a `SecretRef`, not a secret value:

```python
from pipelantic import SecretRef

warehouse_password = SecretRef(
    provider="production-secrets",
    name="analytics/warehouse",
    key="password",
    version="current",
)
```

Conceptually, a reference contains:

| Field | Meaning |
|---|---|
| `provider` | Logical provider configured by the selected profile |
| `name` | Provider-specific secret identifier |
| `key` | Optional field within a structured secret |
| `version` | Optional immutable version or provider alias |
| `purpose` | Optional human-readable use, safe for plans and audit events |

The serializable plan may contain this reference. It must never contain the
resolved value or a credential-bearing URI.

## Configuration

```toml
[profiles.production.secrets.production-secrets]
provider = "aws-secrets-manager"
region = "us-east-1"
cache_ttl = "5m"

[profiles.production.resources.analytics_database]
provider = "sqlalchemy"
url = "postgresql+psycopg://analytics@warehouse.internal/analytics"
password = { secret = "production-secrets:analytics/warehouse#password" }
```

Local development can select a different provider without changing the
pipeline:

```toml
[profiles.local.secrets.production-secrets]
provider = "keyring"
service = "pipelantic.customer-platform"
```

Environment variables remain a compatibility provider, not the recommended
production default:

```toml
[profiles.ci.secrets.production-secrets]
provider = "environment"
prefix = "PIPELANTIC_SECRET_"
```

## Resolution Lifecycle

```text
Configuration and PipelinePlan
            │
            │ SecretRef only
            ▼
Execution boundary starts
            │
            ▼
Secret provider authenticates
            │
            ▼
SecretValue is resolved
            │
            ▼
Resource provider consumes value
            │
            ▼
Value expires, is discarded, or is revoked
```

Planning must not authenticate to a secret manager or resolve a value.
Capability validation may verify that a provider plugin is installed and that a
reference is structurally valid. A remote existence or permission check is an
explicit runtime preflight with its own audit event.

## Sensitive Values

A resolved value should use a `SecretValue` wrapper with these properties:

- `repr()` and `str()` are always redacted;
- normal serialization is refused;
- equality and hashing do not expose the underlying value;
- explicit reveal is restricted to provider and resource-construction code;
- derived values remain sensitive by default;
- zeroization is attempted where practical but is not promised for immutable
  Python strings or third-party SDK internals.

Pydantic's `SecretStr` and `SecretBytes` are useful boundary types because they
redact display and normal serialization. They are not secret managers and do
not eliminate copies already made by Python or an SDK.

## Provider Selection

| Environment | Package or SDK | Position |
|---|---|---|
| Developer workstation | `keyring` | Preferred local provider using the operating-system credential store |
| AWS | `boto3`; optionally `aws-secretsmanager-caching` | Separate provider plugin; prefer IAM roles |
| Azure | `azure-keyvault-secrets` + `azure-identity` | Separate provider plugin; prefer managed identity |
| Google Cloud | `google-cloud-secret-manager` | Separate provider plugin; prefer workload identity |
| HashiCorp Vault | `hvac` | Separate provider plugin; support dynamic credentials and leases |
| 1Password | `onepassword-sdk` | Optional provider; asynchronous SDK and secret references fit well |
| Kubernetes or containers | Mounted secret files | Lightweight provider using bounded filesystem reads |
| CI and compatibility | Environment variables | Explicit provider with strong redaction |

`SecretStorage` is a useful Linux Secret Service implementation detail, but
Pipelantic should normally use the cross-platform `keyring` abstraction rather
than expose a Linux-only API.

## Authentication and Bootstrap

Preferred authentication order:

1. Workload, managed, pod, task, or instance identity
2. Federated short-lived identity
3. Human-authorized local credential store
4. Mounted bootstrap token with restricted permissions
5. Environment variable only when the deployment platform requires it

Do not store a cloud client secret in the same project configuration that
references the cloud vault.

## Caching

Secret caching is provider policy, not plan semantics.

Safe defaults:

- cache only in memory;
- scope caches to a runtime or run;
- use a bounded size and short TTL;
- include provider, tenant, identifier, and requested version in the cache key;
- never persist plaintext cache entries;
- invalidate on authentication failure, revocation, or explicit rotation;
- do not cache one-time credentials unless the provider defines their lease.

AWS documents that its Python caching component uses an LRU policy and refresh
interval, but also notes that the cache is not security hardened and does not
force invalidation. Pipelantic providers must expose caching as an explicit
choice rather than silently enabling it.

## Rotation and Versions

References may request a fixed immutable version, a provider alias such as
`current`, a lease-based dynamic credential, or the latest enabled version.

Run reports may record the provider, identifier, and resolved version when that
metadata is safe. They must not record the value. Long-running runtimes must
define whether rotation takes effect per runtime, run, step, or attempt.

## Auditing

Secret access emits a security event containing provider and reference
identity, pipeline/run/step/attempt identity, safe version metadata, outcome,
duration, and cache-hit status. It contains no secret value.

The provider's native audit log remains authoritative for access to the backing
store.

## Failure Behavior

Secret failures fail closed and produce structured diagnostics for unavailable
providers, authentication failures, permission denial, missing or disabled
versions, expiry, revocation, malformed values, and failed lease renewal.

Fallback between providers is allowed only when declared by the profile. A
production profile must never silently fall back from a managed store to an
environment variable or plaintext file.

## Testing

The SDK conformance suite should verify:

- no resolution during planning;
- redacted `repr`, logs, diagnostics, reports, and exceptions;
- serialization refusal for `SecretValue`;
- bounded caching, isolation, invalidation, rotation, and version selection;
- cancellation and cleanup behavior;
- absence of sentinel secret values from snapshots and golden files.

Live provider tests belong in isolated, opt-in integration suites with
dedicated least-privileged identities.

## Primary References

- [Python keyring](https://keyring.readthedocs.io/en/stable/)
- [Pydantic secret types](https://docs.pydantic.dev/latest/api/types/#pydantic.types.SecretStr)
- [AWS Secrets Manager client-side caching](https://docs.aws.amazon.com/secretsmanager/latest/userguide/retrieving-secrets_cache-python.html)
- [Azure Key Vault Secrets Python client](https://learn.microsoft.com/en-us/python/api/overview/azure/keyvault-secrets-readme)
- [Google Cloud Secret Manager Python client](https://cloud.google.com/python/docs/reference/secretmanager/latest)
- [HashiCorp-supported Vault client libraries](https://developer.hashicorp.com/vault/api-docs/libraries)
- [1Password SDKs](https://www.1password.dev/sdks/)

## See Also

- [Security Model](../02_FOUNDATIONS/SECURITY.md)
- [Configuration](../10_REFERENCE/CONFIGURATION.md)
- [Secret Provider SDK](../07_PLUGIN_SDK/SECRET_PROVIDER.md)
- [Resource Provider](../07_PLUGIN_SDK/RESOURCE_PROVIDER.md)
