# Installation

Pipelantic 0.5.0 provides the typed modeling kernel, contract interoperability
(ODCS/DTCS/DPCS), multi-phase validation, profiles, deterministic planning,
a local runtime that executes plans with Python callables, in-memory
artifacts, and stdlib JSON/CSV bindings, plus optional Polars and Pandas
dataframe plugins. SQL/Spark/orchestration plugins arrive in later milestones.

## Requirements

- Python 3.11 or newer
- [uv](https://docs.astral.sh/uv/) for project and dependency management
- ContractModel as a companion package (installed automatically)

## Development Setup

```bash
git clone https://github.com/eddiethedean/pipelantic.git
cd pipelantic
uv sync
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

`uv sync` installs runtime dependencies, the editable package, and the `dev`
group (pytest, ruff). The lockfile `uv.lock` pins exact versions.

### Common commands

| Command | Purpose |
|---|---|
| `uv sync` | Create/update `.venv` from `uv.lock` |
| `uv lock` | Refresh the lockfile after dependency changes |
| `uv run pytest` | Run tests |
| `uv run ruff check .` | Lint |
| `uv run ruff check --fix .` | Lint and apply safe fixes |
| `uv run ruff format .` | Format |

## Repository Layout

```text
pyproject.toml
uv.lock
.python-version
src/pipelantic/
tests/
docs/
```

## Verification

```bash
uv run python -c "import pipelantic; print(pipelantic.__version__)"
uv run pipelantic --help
```

## User Installation

```bash
pip install pipelantic
# or
uv add pipelantic
```

Backend plugins remain independently installable and are not required by the
core package.

```bash
pip install pipelantic-polars    # Polars reference plugin
pip install pipelantic-pandas    # Pandas compatibility plugin
# or extras:
pip install 'pipelantic[polars]'
pip install 'pipelantic[pandas]'
pip install 'pipelantic[dataframes]'
```

SQL, Spark, and Airflow plugins are not part of 0.5. Do not install
undocumented extras expecting those backends.

## Upgrade

```bash
python -m pip install --upgrade pipelantic
# or
uv lock --upgrade-package pipelantic
```

Review the
[changelog](https://github.com/eddiethedean/pipelantic/blob/main/CHANGELOG.md)
before upgrading between 0.x releases because breaking changes remain
possible.

## Installation Problems

See [Troubleshooting](TROUBLESHOOTING.md) for Python-version errors, stale
virtual environments, missing implementations, and unsupported backend
examples.

## Dependency Philosophy

Pipelantic keeps the core install small. Dataframe engines, orchestrators,
and storage clients belong in optional plugins—not the base package.

See [Dependency Strategy](../11_DEVELOPMENT/DEPENDENCY_STRATEGY.md) for the
full dependency policy.

## Next Step

Continue with [Quickstart](QUICKSTART.md) or [First Pipeline](FIRST_PIPELINE.md).
