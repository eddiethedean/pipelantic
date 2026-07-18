# Contributing

Thank you for your interest in ETLantic.

Full contributor guidance lives in the documentation:

**[docs/11_DEVELOPMENT/CONTRIBUTING.md](docs/11_DEVELOPMENT/CONTRIBUTING.md)**

## Quick start

```bash
git clone https://github.com/eddiethedean/etlantic.git
cd etlantic
uv sync
```

## CI-equivalent local checks

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest -q -m "not sparkforge"
uv run python scripts/check_docs.py
uv run python scripts/check_agent_guidance.py
uv run python scripts/check_release.py
uv run python examples/quickstart.py
uv run python scripts/build_docs.py
uv run pytest -q tests/sparkforge -m sparkforge
```

Fork the repository, branch from `main`, and open a pull request against
`main`. Please report security issues privately per [SECURITY.md](SECURITY.md).
Do not open public issues that include credentials or production data.

Participation is governed by the
[Code of Conduct](docs/11_DEVELOPMENT/CODE_OF_CONDUCT.md), and project decisions
follow the [Governance guide](docs/11_DEVELOPMENT/GOVERNANCE.md). Maintainers
are listed in [MAINTAINERS.md](MAINTAINERS.md).
