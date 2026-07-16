# Distribution

Distribution describes how Pipelantic plugins are packaged, published,
discovered, installed, and maintained across the ecosystem.

A healthy plugin ecosystem depends on stable distribution practices. Plugins
should be independently releasable while remaining compatible with the
Pipelantic Plugin SDK and supported standards.

## Goals

Plugin distribution should:

- Support independent releases.
- Encourage semantic versioning.
- Make installation simple.
- Preserve compatibility metadata.
- Enable automated discovery.
- Support community and commercial plugins.

## Philosophy

The Pipelantic core should remain small.

Functionality grows through independently distributed plugins.

```text
Pipelantic Core
        │
        ▼
 Python Package Index
        │
 ┌──────┼─────────────────────────┐
 ▼      ▼         ▼              ▼
Execution Dataframe Storage   Resource
 Plugins   Plugins  Plugins   Providers
```

## Packaging

Plugins should be distributed as standard Python packages.

Recommended naming convention:

- pipelantic-airflow
- pipelantic-polars
- pipelantic-pandas
- pipelantic-postgres
- pipelantic-s3
- pipelantic-keyring
- pipelantic-secrets-aws
- pipelantic-secrets-azure
- pipelantic-secrets-gcp
- pipelantic-secrets-vault

Third-party plugins should follow a consistent naming convention where practical.

## Installation

Typical installation:

```bash
pip install pipelantic-airflow
```

Multiple plugins may be installed simultaneously.

Profiles determine which plugins are used.

## Discovery

Installed plugins should be discoverable automatically through the Plugin SDK.

Conceptually:

```python
from pipelantic import PluginRegistry

plugins = PluginRegistry.discover()
```

Discovery should not require manual registration in normal deployments.

## Compatibility Metadata

Every plugin should publish:

- Plugin name
- Plugin version
- Supported Pipelantic version(s)
- Supported SDK version
- Supported ODCS version(s)
- Supported DTCS version(s)
- Supported DPCS version(s)
- Capability declarations

Planning uses this metadata when selecting plugins.

## Semantic Versioning

Plugins should follow Semantic Versioning.

- MAJOR — breaking SDK or behavior changes
- MINOR — backward-compatible features
- PATCH — bug fixes and non-semantic improvements

## Release Workflow

Recommended workflow:

1. Implement
2. Test
3. Run SDK conformance suite
4. Publish package
5. Publish release notes
6. Update compatibility matrix

## Dependency Management

Plugins should minimize dependencies and isolate backend-specific libraries.

Optional dependencies should be preferred where practical to avoid unnecessary
install size for users who do not need every backend.

## Security

Plugin authors should:

- Sign releases when possible.
- Keep dependencies updated.
- Avoid embedding credentials.
- Follow secure disclosure practices.
- Publish supported version ranges.
- Ensure secret-provider packages pass redaction, rotation, lease, and
  sentinel-leak conformance tests.

## Best Practices

- Keep plugins independently releasable.
- Publish clear compatibility metadata.
- Use semantic versioning.
- Ship documentation with every release.
- Maintain changelogs.

## Anti-Patterns

Avoid:

- Bundling all plugins into the core package.
- Publishing plugins without compatibility metadata.
- Introducing breaking changes in minor releases.
- Hiding runtime dependencies.
- Depending on internal Pipelantic APIs.

## Key Principle

> Pipelantic grows through a distributed ecosystem of independently versioned
> plugins. Stable packaging, discovery, and compatibility metadata allow users
> to compose the execution environment that best fits their pipelines.

## Next Step

Continue with the [Examples](../09_EXAMPLES/README.md) section to see plugins
used in complete pipelines.
