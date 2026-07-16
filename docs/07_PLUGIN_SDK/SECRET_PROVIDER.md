# Secret Provider

A Secret Provider resolves logical `SecretRef` objects into short-lived,
redacted values for authorized runtime consumers.

Secret Providers are a specialized Plugin SDK category. They are separated from
general Resource Providers because retrieval has stricter rules for planning,
serialization, caching, auditing, and failure handling.

## Responsibilities

A provider:

- declares supported reference forms and version semantics;
- authenticates using environment-appropriate identity;
- retrieves a secret only during execution;
- returns a protected `SecretValue`;
- applies bounded cache and lease policy;
- emits value-free audit events;
- closes clients and revokes temporary credentials where supported;
- translates vendor failures into stable ETLantic diagnostics.

A provider does not add values to plans, expose SDK clients to transformations,
log request or response bodies, silently search other providers, or define
pipeline semantics.

## Proposed Protocol

```python
from collections.abc import AsyncIterator
from typing import Protocol


class SecretProvider(Protocol):
    descriptor: SecretProviderDescriptor

    async def resolve(
        self,
        reference: SecretRef,
        context: SecretResolutionContext,
    ) -> SecretValue:
        ...

    async def lifespan(
        self,
        context: ProviderContext,
    ) -> AsyncIterator[None]:
        ...
```

The final API may represent lifespan with an asynchronous context manager.
Synchronous vendor SDKs should be bridged behind the provider.

## Capabilities

```python
SecretProviderCapabilities(
    versions=True,
    aliases=True,
    binary_values=True,
    structured_values=True,
    dynamic_credentials=False,
    leases=False,
    renewal=False,
    revocation=False,
    in_memory_cache=True,
    async_native=True,
)
```

Planning may validate capability compatibility but must not call `resolve`.

## Reference Parsing

ETLantic provides a canonical, provider-neutral `SecretRef`. Provider-specific
URI syntaxes may be accepted by adapters:

```text
secret://production-secrets/analytics/warehouse#password
```

Parsing must not mistake a credential-bearing URL for a safe reference.
Adapters normalize identifiers without performing network access.

## Resolution Context

The context supplies pipeline/run/step/attempt identities, requested scope and
purpose, cancellation and timeout policy, tenant and security-domain identity,
an audit-event emitter, and approved network policy. It does not expose
unrelated resources or secrets.

## Secret Values

`SecretValue` redacts display, rejects ordinary serialization, requires an
explicit reveal operation, preserves sensitivity when selecting a structured
field, and keeps safe metadata separate from secret material.

Python cannot reliably guarantee memory zeroization. Provider authors should
minimize lifetime and copies rather than claim stronger protection.

## Caching and Leases

Cache and lease behavior must be declared in configuration and observable in
safe metadata. Dynamic-credential providers should expose lease identity,
expiry, renewable status, renewal, and revocation.

Cleanup runs after success, failure, and cancellation. Failed renewal must not
leave a run using credentials beyond their known validity.

## Provider Packages

| Distribution concept | Primary dependencies |
|---|---|
| `etlantic-keyring` | `keyring` |
| `etlantic-secrets-aws` | `boto3`, optional `aws-secretsmanager-caching` |
| `etlantic-secrets-azure` | `azure-keyvault-secrets`, `azure-identity` |
| `etlantic-secrets-gcp` | `google-cloud-secret-manager` |
| `etlantic-secrets-vault` | `hvac` |
| `etlantic-secrets-1password` | `onepassword-sdk` |

The core may ship simple environment and mounted-file providers if they remain
explicitly selected and use only the standard library.

## Conformance Requirements

A conforming provider passes:

- protocol and capability tests;
- no-resolution-during-planning tests;
- redaction and serialization tests;
- timeout and cancellation tests;
- cache isolation and invalidation tests;
- version and rotation tests;
- cleanup, renewal, and revocation tests where applicable;
- error normalization and sentinel leak tests.

## Security Requirements

- Use least-privileged workload identity.
- Verify TLS and provider endpoints.
- Do not accept endpoints from untrusted pipeline documents.
- Disable ambient cross-provider fallback.
- Bound retries and do not retry permission denials blindly.
- Keep vendor debug logging disabled unless explicitly reviewed.
- Treat secret names and metadata as potentially sensitive.
- Never place secret material in telemetry attributes or metric labels.

## Key Principle

> Plans carry secret references. Secret Providers resolve them at the last
> authorized moment. Only the resource that needs the value receives it.

## Next Step

Continue with [Resource Provider](RESOURCE_PROVIDER.md) to see how resolved
secrets are consumed while constructing managed runtime dependencies.
