"""Unit tests for diagnostics and reports."""

from pipelinemodel import Diagnostic, Severity, ValidationReport
from pipelinemodel.exceptions import PipelineValidationError


def test_report_valid_when_no_errors() -> None:
    report = ValidationReport(
        diagnostics=(Diagnostic(code="X", severity=Severity.WARNING, message="warn"),)
    )
    assert report.valid
    assert len(report.warnings) == 1


def test_raise_for_errors() -> None:
    report = ValidationReport(
        diagnostics=(
            Diagnostic(code="PMPIPE210", severity=Severity.ERROR, message="bad"),
        )
    )
    assert not report.valid
    try:
        report.raise_for_errors()
    except PipelineValidationError as exc:
        assert exc.report is report
    else:
        raise AssertionError("expected PipelineValidationError")
