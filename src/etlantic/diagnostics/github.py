"""GitHub Actions annotation renderer for diagnostics."""

from __future__ import annotations

from collections.abc import Iterable

from etlantic.diagnostics import Diagnostic, Severity


def diagnostics_to_github_annotations(
    diagnostics: Iterable[Diagnostic],
) -> list[str]:
    """Return GitHub workflow command lines for annotations."""
    lines: list[str] = []
    for diagnostic in diagnostics:
        level = {
            Severity.ERROR: "error",
            Severity.WARNING: "warning",
            Severity.INFO: "notice",
            Severity.HINT: "notice",
        }.get(diagnostic.severity, "notice")
        path = "/".join(str(p) for p in diagnostic.path if p) or "pipeline"
        # ::error file=...,title=CODE::message
        lines.append(
            f"::{level} file={path},title={diagnostic.code}::{diagnostic.message}"
        )
    return lines
