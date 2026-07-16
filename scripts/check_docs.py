"""Small dependency-free documentation consistency checks."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).parents[1]


def version_from(path: Path, pattern: str) -> str:
    match = re.search(pattern, path.read_text(encoding="utf-8"))
    if match is None:
        raise SystemExit(f"Could not find version in {path}")
    return match.group(1)


def main() -> None:
    package_version = version_from(
        ROOT / "src/pipelantic/_version.py", r'__version__ = "([^"]+)"'
    )
    project_version = version_from(ROOT / "pyproject.toml", r'(?m)^version = "([^"]+)"')
    if package_version != project_version:
        raise SystemExit(
            f"Version mismatch: package={package_version}, project={project_version}"
        )

    current_markers = [
        ROOT / "README.md",
        ROOT / "docs/README.md",
        ROOT / "docs/01_GETTING_STARTED/CAPABILITIES.md",
        ROOT / "SECURITY.md",
    ]
    for path in current_markers:
        text = path.read_text(encoding="utf-8")
        if package_version not in text:
            raise SystemExit(
                f"{path} does not mention current version {package_version}"
            )

    examples_index = (ROOT / "docs/09_EXAMPLES/README.md").read_text(encoding="utf-8")
    if "complete working examples" in examples_index.lower():
        raise SystemExit("Examples index still claims all design examples are runnable")

    banned_phrases = [
        "does not ship Pandas or Polars",
        "Pandas, Polars, SQL, Spark, and Airflow plugins are not published as part of\nPipelantic 0.4",
        "Future plugins may add Pandas, Polars",
        "Pandas and Polars pipelines | Future plugin design",
    ]
    scrub_paths = [
        ROOT / "docs/README.md",
        ROOT / "docs/01_GETTING_STARTED/INSTALLATION.md",
        ROOT / "docs/01_GETTING_STARTED/FAQ.md",
        ROOT / "docs/01_GETTING_STARTED/README.md",
        ROOT / "docs/09_EXAMPLES/README.md",
        ROOT / "docs/10_REFERENCE/COMPATIBILITY.md",
    ]
    for path in scrub_paths:
        text = path.read_text(encoding="utf-8")
        for phrase in banned_phrases:
            if phrase in text:
                raise SystemExit(
                    f"{path} still contains banned stale phrase: {phrase!r}"
                )

    print(f"Documentation consistency checks passed for {package_version}.")


if __name__ == "__main__":
    main()
