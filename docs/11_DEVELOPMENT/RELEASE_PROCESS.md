# Release Process

ETLantic releases must coordinate the core package, Plugin SDK, generated
artifacts, compatibility policy, and documentation.

## Versioning

ETLantic follows Semantic Versioning after 1.0:

- Patch: compatible fixes and documentation
- Minor: backward-compatible capabilities
- Major: incompatible public API or persistent-format changes

During 0.x, breaking changes remain possible but must be documented.

## Release Scope

A release may affect:

- Authoring API
- Plugin SDK
- `PipelinePlan` schema
- Configuration
- CLI
- Supported ODCS, DTCS, and DPCS versions
- Built-in or separately released plugins

These version surfaces should not be conflated.

## Pre-Release Checklist

1. Confirm milestone scope.
2. Resolve release-blocking issues.
3. Review public API changes.
4. Review ADRs and deprecations.
5. Run all tests and plugin conformance suites.
6. Build documentation.
7. Verify generated examples.
8. Run security and dependency checks.
9. Verify the release gate in the
   [Security Model](../02_FOUNDATIONS/SECURITY.md).
10. Run performance regression checks.
11. Prepare release notes and migration guidance.

## Compatibility Matrix

Release notes should state:

| Surface | Supported versions |
|---|---|
| Python | Project-defined range |
| ContractModel | Compatible range |
| ODCS | Supported specification versions |
| DTCS | Supported specification versions |
| DPCS | Supported specification versions |
| Plugin SDK | API version |
| PipelinePlan | Schema version |

## Release Candidate

Major and high-risk minor releases should publish a release candidate:

```text
1.0.0rc1
```

Validate installation, end-to-end examples, external plugin compatibility, and
migration documentation before final release.

## Build

The release pipeline should:

1. Build source and wheel artifacts.
2. Inspect package metadata.
3. Install from built artifacts in clean environments.
4. Run smoke tests.
5. Verify type information is included.
6. Verify optional dependencies remain optional.

## Publish

Recommended order:

1. Publish to TestPyPI.
2. Install and smoke-test from TestPyPI.
3. Create the signed release tag.
4. Publish to PyPI.
5. Create the GitHub release.
6. Publish versioned documentation.
7. Announce plugin compatibility updates.

## Plugin Releases

Plugins should be independently versioned. A core release must not require every
plugin to release simultaneously unless the SDK compatibility range changes.

Official plugin releases should declare:

- Supported ETLantic versions
- Plugin SDK version
- Backend versions
- Capability changes
- Migration requirements

## Deprecations

After 1.0:

- Emit a documented warning.
- Provide a replacement.
- Include migration guidance.
- Retain deprecated behavior for at least one documented release window.
- Remove only in a major release unless security requires faster action.

## Plan and Configuration Migrations

Persistent `PipelinePlan` or configuration changes require:

- A schema/version change
- A migration tool or clear regeneration path
- Compatibility tests
- Release-note examples

Generated plans should normally be regenerated rather than hand-edited.

## Hotfixes

Security and critical correctness fixes may use an accelerated process, but
must still include focused tests, release notes, and artifact verification.

## Post-Release

After publishing:

- Verify package installation.
- Verify documentation links.
- Monitor issue reports.
- Update the development version.
- Open follow-up issues for deferred work.
- Record lessons from release incidents.
