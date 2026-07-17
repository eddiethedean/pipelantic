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
        ROOT / "src/etlantic/_version.py", r'__version__ = "([^"]+)"'
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
        "Pandas, Polars, SQL, Spark, and Airflow plugins are not published as part of\nETLantic 0.4",
        "Future plugins may add Pandas, Polars",
        "Pandas and Polars pipelines | Future plugin design",
        "Pandas, Polars, SQL, Spark, and Airflow plugins | Not yet available",
        "SQL, Spark, and Airflow plugins | Not yet available",
        "SQL compilation or execution | Future design (0.6)",
        "SQL, Spark, and Airflow compilation are not shipped",
        "These examples use only APIs and dependencies shipped in ETLantic 0.4",
        "These examples use only APIs and dependencies shipped in ETLantic 0.5",
        "These examples use only APIs and dependencies shipped in ETLantic 0.6",
        "Available in ETLantic 0.4.0",
        "not a ETLantic 0.4 API guide",
        "not a ETLantic 0.5 API guide",
        "not a ETLantic 0.6 API guide",
        "not a ETLantic 0.7 API guide",
        "Dataframe, SQL, Spark, and external orchestration chapters remain accepted",
        "Spark and Airflow plugins are not part of 0.6",
        "Spark / Airflow | No",
        "PySpark and streaming | Future plugin design",
        "Still accepted design until later milestones:** Spark",
        "Spark and Airflow remain design material",
        "Later milestones add Spark",
        "plan.to_mermaid()",
        "lightweight production workloads",
        "uv run pyright",
        "Commands are provisional until the implementation toolchain is committed",
        "Airflow or other orchestrator compilation | Future design (0.8)",
        "External orchestrator compilation is not included in 0.7",
        "Full CLI `compile` / generate tooling | Continues in 0.9",
        "Graphviz and generated HTML pipeline documentation | Future design",
        "Public third-party Plugin SDK polish | Continues in 0.9",
    ]
    if "| Capability | 0.4 |" in (ROOT / "README.md").read_text(encoding="utf-8"):
        raise SystemExit("README.md capability table still labels the release as 0.4")
    if "| Capability | 0.5 |" in (ROOT / "README.md").read_text(encoding="utf-8"):
        raise SystemExit("README.md capability table still labels the release as 0.5")
    if "| Capability | 0.6 |" in (ROOT / "README.md").read_text(encoding="utf-8"):
        raise SystemExit("README.md capability table still labels the release as 0.6")
    if "| Capability | 0.7 |" in (ROOT / "README.md").read_text(encoding="utf-8"):
        raise SystemExit("README.md capability table still labels the release as 0.7")
    if "| Capability | 0.8 |" in (ROOT / "README.md").read_text(encoding="utf-8"):
        raise SystemExit("README.md capability table still labels the release as 0.8")

    scrub_paths = [
        ROOT / "README.md",
        ROOT / "examples/README.md",
        ROOT / "docs/README.md",
        ROOT / "docs/01_GETTING_STARTED/INSTALLATION.md",
        ROOT / "docs/01_GETTING_STARTED/FAQ.md",
        ROOT / "docs/01_GETTING_STARTED/README.md",
        ROOT / "docs/01_GETTING_STARTED/QUICKSTART.md",
        ROOT / "docs/01_GETTING_STARTED/FIRST_PIPELINE.md",
        ROOT / "docs/01_GETTING_STARTED/CAPABILITIES.md",
        ROOT / "docs/02_FOUNDATIONS/DOCUMENTATION_STATUS.md",
        ROOT / "docs/06_EXECUTION/LOCAL_PYTHON.md",
        ROOT / "docs/06_EXECUTION/SECRETS_MANAGEMENT.md",
        ROOT / "docs/08_VISUALIZATION/MERMAID.md",
        ROOT / "docs/09_EXAMPLES/README.md",
        ROOT / "docs/10_REFERENCE/API_REFERENCE.md",
        ROOT / "docs/10_REFERENCE/CLI.md",
        ROOT / "docs/10_REFERENCE/COMPATIBILITY.md",
        ROOT / "docs/11_DEVELOPMENT/CONTRIBUTING.md",
        ROOT / "docs/theme/javascripts/status-banner.js",
    ]
    for path in scrub_paths:
        text = path.read_text(encoding="utf-8")
        for phrase in banned_phrases:
            if phrase in text:
                raise SystemExit(
                    f"{path} still contains banned stale phrase: {phrase!r}"
                )

    # Design example pages must carry a future-design / design-study admonition
    for path in (ROOT / "docs/09_EXAMPLES").glob("*.md"):
        if path.name == "README.md":
            continue
        text = path.read_text(encoding="utf-8")
        if "!!! warning" not in text:
            raise SystemExit(f"{path} missing design/future admonition")
        if (
            "Future design—not a ETLantic 0.9 API guide" not in text
            and "Design study—" not in text
            and "Experimental design study—" not in text
        ):
            raise SystemExit(f"{path} missing Future design / design-study admonition")

    banner_js = (ROOT / "docs/theme/javascripts/status-banner.js").read_text(
        encoding="utf-8"
    )
    if "Future design—not a ETLantic 0.9 API guide" not in banner_js:
        raise SystemExit("status-banner.js missing 0.9 future-design banner text")
    if "Experimental in ETLantic 0.7" not in banner_js:
        raise SystemExit("status-banner.js missing experimental streaming banner text")
    if "/08_VISUALIZATION/GRAPHVIZ/" not in banner_js:
        raise SystemExit(
            "status-banner.js must exclude GRAPHVIZ from future viz banner"
        )
    if "/08_VISUALIZATION/HTML/" not in banner_js:
        raise SystemExit("status-banner.js must exclude HTML from future viz banner")
    if "/08_VISUALIZATION/LINEAGE/" not in banner_js:
        raise SystemExit("status-banner.js must exclude LINEAGE from future viz banner")

    start = banner_js.find("futureExecutionPages = [")
    end = banner_js.find("];", start)
    if start < 0 or end < 0:
        raise SystemExit("status-banner.js missing futureExecutionPages array")
    future_block = banner_js[start:end]
    for shipped in (
        "SQL",
        "SQL_EXECUTION",
        "SQL_PUSHDOWN",
        "POLARS",
        "PANDAS",
        "DATAFRAME_PLUGINS",
        "PYSPARK",
        "PYSPARK_EXECUTION",
        "SPARK_OPTIMIZATION",
        "STRUCTURED_STREAMING",
        "ORCHESTRATION_PLUGINS",
        "AIRFLOW",
        "COMPILATION",
    ):
        # Exact token match: "SQL" must not match SQL_EXECUTION incorrectly —
        # check quoted entries.
        if f'"{shipped}"' in future_block:
            raise SystemExit(
                f"status-banner.js still lists shipped page {shipped!r} as future"
            )

    # Shipped plugin-protocol pages must be excluded from the future Plugin SDK banner
    for shipped_sdk in (
        "DATAFRAME_PLUGIN",
        "SQL_PLUGIN",
        "SQL_DIALECT",
        "PYSPARK_PLUGIN",
        "SPARK_PROVIDER",
        "ORCHESTRATOR_PLUGIN",
    ):
        if f"/07_PLUGIN_SDK/{shipped_sdk}/" not in banner_js:
            raise SystemExit(
                f"status-banner.js must exclude {shipped_sdk} from future Plugin SDK banner"
            )

    secrets = (ROOT / "docs/06_EXECUTION/SECRETS_MANAGEMENT.md").read_text(
        encoding="utf-8"
    )
    if "Available in 0.5" not in secrets and "shipped" not in secrets.lower():
        raise SystemExit("SECRETS_MANAGEMENT.md missing shipped-in-0.5 banner")
    if 'provider = "aws-secrets-manager"' in secrets:
        raise SystemExit(
            "SECRETS_MANAGEMENT.md still shows aws-secrets-manager as current config"
        )

    # Plugin package versions must match core.
    for plugin_pyproject in (
        ROOT / "packages/etlantic-polars/pyproject.toml",
        ROOT / "packages/etlantic-pandas/pyproject.toml",
        ROOT / "packages/etlantic-sql/pyproject.toml",
        ROOT / "packages/etlantic-pyspark/pyproject.toml",
        ROOT / "packages/etlantic-airflow/pyproject.toml",
        ROOT / "packages/etlantic-keyring/pyproject.toml",
        ROOT / "packages/etlantic-sqlmodel/pyproject.toml",
    ):
        plugin_version = version_from(plugin_pyproject, r'(?m)^version = "([^"]+)"')
        if plugin_version != package_version:
            raise SystemExit(
                f"{plugin_pyproject} version {plugin_version} != core {package_version}"
            )

    print(f"Documentation consistency checks passed for {package_version}.")


if __name__ == "__main__":
    main()
