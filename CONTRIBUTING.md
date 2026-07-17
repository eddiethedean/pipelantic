# Contributing

Thank you for your interest in ETLantic.

Full contributor guidance lives in the documentation:

**[docs/11_DEVELOPMENT/CONTRIBUTING.md](docs/11_DEVELOPMENT/CONTRIBUTING.md)**

Quick start:

```bash
git clone https://github.com/eddiethedean/etlantic.git
cd etlantic
uv sync
uv run pytest
uv run ruff check .
uv run python scripts/check_docs.py
```

Please report security issues privately per [SECURITY.md](SECURITY.md).
Do not open public issues that include credentials or production data.

Participation is governed by the
[Code of Conduct](docs/11_DEVELOPMENT/CODE_OF_CONDUCT.md), and project decisions
follow the [Governance guide](docs/11_DEVELOPMENT/GOVERNANCE.md).
