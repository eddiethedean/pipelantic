"""Report model regression tests."""

from __future__ import annotations

from datetime import UTC, datetime

from etlantic.reports.model import PipelineRunReport, RunSummary
from etlantic.runtime.request import RunIntent
from etlantic.runtime.state import RunStatus


def test_report_includes_lineage_in_json() -> None:
    report = PipelineRunReport(
        pipeline_id="p",
        plan_id="plan",
        run_id="run",
        intent=RunIntent.STANDARD,
        profile="development",
        status=RunStatus.SUCCEEDED,
        started_at=datetime.now(UTC),
        summary=RunSummary(total_steps=1, succeeded=1),
        lineage=({"from": "a.result", "to": "b.rows"},),
    )
    data = report.to_dict()
    assert data["lineage"] == [{"from": "a.result", "to": "b.rows"}]
    assert "lineage" in report.to_json()


def test_report_from_dict_round_trip() -> None:
    from datetime import timedelta

    from etlantic.reports.model import (
        RunDiagnostic,
        SchemaObservationResult,
        StepRunReport,
    )
    from etlantic.runtime.state import StepStatus

    started = datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC)
    ended = datetime(2026, 1, 2, 3, 4, 8, tzinfo=UTC)
    report = PipelineRunReport(
        pipeline_id="p",
        plan_id="plan",
        run_id="run",
        intent=RunIntent.STANDARD,
        profile="development",
        status=RunStatus.SUCCEEDED,
        started_at=started,
        ended_at=ended,
        duration=timedelta(seconds=3),
        summary=RunSummary(total_steps=1, succeeded=1),
        steps=(
            StepRunReport(
                step_id="s1",
                step_name="step",
                status=StepStatus.SUCCEEDED,
                attempts=1,
                started_at=started,
                ended_at=ended,
                duration_seconds=3.0,
            ),
        ),
        diagnostics=(
            RunDiagnostic(code="PMEXEC301", severity="warning", message="soft"),
        ),
        schema_observations=(
            SchemaObservationResult(
                subject_id="raw", layer="current", fingerprint="abc"
            ),
        ),
        lineage=({"from": "a.result", "to": "b.rows"},),
        plan_fingerprint="fp",
    )
    restored = PipelineRunReport.from_dict(report.to_dict())
    assert restored.lineage == report.lineage
    assert restored.diagnostics[0].code == "PMEXEC301"
    assert restored.schema_observations[0].fingerprint == "abc"
    assert restored.steps[0].duration_seconds == 3.0
    assert restored.duration_seconds == 3.0
    assert restored.plan_fingerprint == "fp"
