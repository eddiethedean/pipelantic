---
name: etlantic
description: Validate, plan, compile, and generate ETLantic pipelines safely.
---

# ETLantic skill

Use public CLI commands (`validate`, `plan`, `compile`, `generate`, `diff`,
`schema`, `plugin`) and public SDK imports (`etlantic.dataframe`, `.sql`,
`.spark`, `.orchestration`, `.secrets`, `.testing`).

Never write secret values into plans or reports. Production profiles require
`plugin_allowlist`. Schema observe/acknowledge must not store source rows.
