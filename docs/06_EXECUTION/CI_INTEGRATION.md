# CI Integration

> **Status: Available in ETLantic 0.10.0.**

Validate without executing transformation code and publish SARIF diagnostics:

```bash
etlantic validate package.pipeline:CustomerPipeline \
  --profile production --format sarif > etlantic.sarif
etlantic plan package.pipeline:CustomerPipeline \
  --profile production --format json > pipeline-plan.json
```

Use a production `Profile` with a non-empty `plugin_allowlist`. Treat the plan
as build metadata: it is secret-free, but may reveal pipeline structure and
resource names.

Recommended gates:

1. Pin ETLantic and official plugins to one tested release.
2. Validate every changed pipeline.
3. Generate contracts and fail on unexpected diffs.
4. Upload SARIF through the CI platform's supported integration.
5. Compile orchestrator artifacts only from a valid plan.
6. Never resolve runtime secrets during validation or planning.

See [diagnostics](../10_REFERENCE/DIAGNOSTICS.md),
[security](../02_FOUNDATIONS/SECURITY.md), and
[runtime configuration](../10_REFERENCE/RUNTIME_CONFIGURATION.md).
