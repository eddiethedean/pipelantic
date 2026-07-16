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
