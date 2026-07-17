# Documentation Contributions

Documentation is part of the public API.

## Required Page Status

Every page describing product behavior must be one of:

- **Available in 0.10** (or the first shipped milestone when still current)
- **Experimental**
- **Partially available**
- **Future design**
- **Normative specification**
- **Internal project plan**

Future design must not be described as a complete or runnable current example.

## Local Checks

```bash
uv run pytest -q
uv run python scripts/check_docs.py
uv run python scripts/check_runnable_docs.py
NO_MKDOCS_2_WARNING=1 uv run mkdocs build --strict
```

Set `NO_MKDOCS_2_WARNING=1` to suppress Material for MkDocs' advisory about
unreleased MkDocs 2.0 (unrelated to this project's content).

The example test imports and runs `examples/quickstart.py`. Documentation CI
also checks release-version consistency and rejects future-backend claims in
the runnable examples index.

Pages labeled **Status: Available** and presented as runnable must identify a
companion source file in `examples/`. Register the page/source pair in
`scripts/check_runnable_docs.py`; the docs gate verifies that the file exists
and compiles. Core examples execute in CI. Optional-backend companions execute
in their dependency-group jobs.

## Writing Rules

- Lead with the user outcome.
- State prerequisites and expected output.
- Use only shipped APIs in beginner documentation.
- Put proposed APIs in the Future Design section.
- Link to the compatibility matrix rather than duplicating dependency ranges.
- Update the changelog, status page, and navigation when release boundaries
  change.
