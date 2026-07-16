# Installation

PipelineModel 0.1 provides the typed modeling kernel. Planning, execution
plugins, and contract serialization arrive in later milestones.

## Requirements

- Python 3.11 or newer
- [uv](https://docs.astral.sh/uv/) for project and dependency management
- ContractModel as a companion package (installed automatically)

## Development Setup

```bash
git clone https://github.com/eddiethedean/pipelinemodel.git
cd pipelinemodel
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
src/pipelinemodel/
tests/
docs/
```

## Verification

```bash
uv run python -c "import pipelinemodel; print(pipelinemodel.__version__)"
```

## User Installation (future)

Once published to PyPI:

```bash
pip install pipelinemodel
# or
uv add pipelinemodel
```

Backend plugins will remain independently installable and must not be required
by the core package.

## Dependency Philosophy

PipelineModel keeps the core install small. Dataframe engines, orchestrators,
and storage clients belong in optional plugins—not the base package.

See [Dependency Strategy](../11_DEVELOPMENT/DEPENDENCY_STRATEGY.md) for the
full dependency policy.

## Next Step

Continue with [Quickstart](QUICKSTART.md) or [First Pipeline](FIRST_PIPELINE.md).
