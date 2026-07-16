# Installation

PipelineModel is currently a design-first, pre-implementation project.

There is no supported PyPI release or installable package in this repository
yet. The commands below document the intended installation experience and
development toolchain; they should not be treated as currently working package
instructions.

## Intended Requirements

The current plan targets:

- Python 3.11 or newer
- `uv` for project and dependency management
- ContractModel as a companion package
- Optional backend packages installed independently

The minimum Python version may be revisited before 1.0.

## Intended User Installation

Core modeling package:

```bash
pip install pipelinemodel
```

Backend plugins should remain independently installable:

```bash
pip install pipelinemodel-polars
pip install pipelinemodel-pandas
pip install pipelinemodel-airflow
pip install pipelinemodel-pyspark
```

Exact distribution names are proposed and will be finalized with the Plugin
SDK.

Heavy dependencies such as Airflow and PySpark must not be required by the core
package.

## Intended Development Setup

Once the package scaffold exists, the expected workflow is:

```bash
git clone https://github.com/<organization>/pipelinemodel.git
cd pipelinemodel
uv sync --all-extras --dev
uv run pytest
```

The repository should eventually include:

```text
pyproject.toml
src/pipelinemodel/
tests/
docs/
examples/
```

## Intended Verification

```python
import pipelinemodel

print(pipelinemodel.__version__)
```

Plugin inspection should be available through:

```bash
pipelinemodel plugins list
```

## Dependency Philosophy

The core installation should include only what is needed for:

- Typed authoring
- Introspection
- Validation
- Planning
- Diagnostics
- Contract coordination

Users install execution, orchestration, storage, and resource integrations
separately.

## Current Next Step

Because the package is not yet implemented, continue with the
[Quickstart](QUICKSTART.md) as an accepted design example, then review the
[Roadmap](../11_DEVELOPMENT/ROADMAP.md) for implementation order.
