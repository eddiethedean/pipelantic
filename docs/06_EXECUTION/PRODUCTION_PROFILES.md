# Production Profiles

ETLantic 0.17.0 treats production configuration as an explicit trust boundary.
The built-in `production` profile is a template, not a deployable setup.

## Built-in production fails closed

`production_profile()` supplies strict validation and the `production`
security domain, but its `plugin_allowlist` and `assets` are empty. Validation
therefore emits `PMPLUG401` until the allowlist is non-empty. Real pipelines
also need their logical extract and load assets resolved.

This command is expected to fail for a pipeline that needs production
configuration:

```bash
etlantic validate package.pipeline:CustomerPipeline --profile production
```

## Write an explicit profile

Keep resolved secret values out of profile files. Use `SecretRef` when a
profile needs a secret reference.

```python
from etlantic import Profile, write_profile

profile = Profile(
    name="customer-production",
    dataframe_engine="polars",
    security_domain="production",
    validation_policy="strict",
    plugin_allowlist={
        "etlantic-polars": "==0.17.0",
    },
    assets={
        "customer_source": "json",
        "customer_sink": "json",
    },
    portable_transform_policy="require",
    concurrency=4,
    timeout_seconds=300,
    retry_max_attempts=3,
)

write_profile(profile, "profiles/customer-production.json")
```

Allowlist keys may match the discovered plugin key or its advertised name.
Use exact versions for a controlled pilot. An allowlist permits code to be
discovered; it does not install the package or resolve missing bindings.

## Use the JSON profile from the CLI

```bash
etlantic validate package.pipeline:CustomerPipeline \
  --profile profiles/customer-production.json --format sarif

etlantic plan package.pipeline:CustomerPipeline \
  --profile profiles/customer-production.json --format json
```

`--profile` resolves an existing `.json` path through `load_profile`. The
profile path is explicit; ETLantic does not search for a project configuration
file or read `ETLANTIC_PROFILE`.

## Use a scoped planning context in Python

`PlanningContext` owns the profile and planning registries. It does not acquire
live resources or resolve secrets.

```python
import json

from etlantic import PlanningContext, load_profile
from package.pipeline import CustomerPipeline

profile = load_profile("profiles/customer-production.json")
context = PlanningContext.create(profile=profile)

validation = CustomerPipeline.validate(context=context)
if not validation.valid:
    raise RuntimeError(validation.to_text())

plan = CustomerPipeline.plan(context=context)
print(json.dumps(plan.to_dict(), indent=2))
```

When a deployment needs custom `BindingDescriptor` entries, register them on
`context.registry` before validation and planning, as shown in the
[File Storage Tutorial](FILE_STORAGE_TUTORIAL.md). Reuse the same context for
validation, planning, and execution so those scoped registrations remain
consistent.

See [Configuration in 0.17.0](../10_REFERENCE/CONFIGURATION_TODAY.md),
[CI Integration](CI_INTEGRATION.md), and
[Security](../02_FOUNDATIONS/SECURITY.md).
