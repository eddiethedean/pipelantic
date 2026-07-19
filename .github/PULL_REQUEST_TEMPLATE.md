## Summary

<!-- What problem does this solve? -->

## Type of change

- [ ] Bug fix
- [ ] Feature
- [ ] Documentation
- [ ] Tests / CI
- [ ] Breaking public API (call out migration)

## Checklist

- [ ] Tests cover the change (or explain why not)
- [ ] Docs / changelog updated when user-visible
- [ ] No secrets or production data in the PR
- [ ] Compatibility impact considered (plans, plugins, contracts)
- [ ] Local checks: `uv run ruff check . && uv run ruff format --check . && uv run pytest -q -m "not sparkforge and not polars and not pandas and not sql and not spark and not real_pyspark and not airflow and not prefect and not keyring and not sqlmodel" && uv run python scripts/check_docs.py`

## Test plan

<!-- Commands you ran and expected results -->
