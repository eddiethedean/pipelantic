"""Filesystem-backed durable run report store."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from etlantic.reports.model import PipelineRunReport
from etlantic.reports.store import ReportStore


@dataclass
class FileReportStore:
    """Durable report store writing one JSON file per run_id."""

    root: Path
    _memory: ReportStore = field(default_factory=ReportStore)

    def __post_init__(self) -> None:
        self.root = Path(self.root)
        self.root.mkdir(parents=True, exist_ok=True)
        for path in sorted(self.root.glob("*.json")):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                report = PipelineRunReport.from_dict(data)
                self._memory.put(report)
            except Exception:
                continue

    def put(self, report: PipelineRunReport) -> None:
        self._memory.put(report)
        path = self.root / f"{report.run_id}.json"
        path.write_text(report.to_json(), encoding="utf-8")

    def get(self, run_id: str) -> PipelineRunReport | None:
        return self._memory.get(run_id)

    def list(
        self,
        *,
        pipeline_id: str | None = None,
        limit: int | None = None,
    ) -> list[PipelineRunReport]:
        return self._memory.list(pipeline_id=pipeline_id, limit=limit)


def compare_reports(
    left: PipelineRunReport,
    right: PipelineRunReport,
) -> dict[str, Any]:
    """Compare two normalized reports without backend-specific classes."""
    left_steps = {s.step_name: s.status.value for s in left.steps}
    right_steps = {s.step_name: s.status.value for s in right.steps}
    return {
        "left_run_id": left.run_id,
        "right_run_id": right.run_id,
        "status_equal": left.status.value == right.status.value,
        "left_status": left.status.value,
        "right_status": right.status.value,
        "step_names_equal": set(left_steps) == set(right_steps),
        "step_status_diffs": {
            name: {"left": left_steps.get(name), "right": right_steps.get(name)}
            for name in sorted(set(left_steps) | set(right_steps))
            if left_steps.get(name) != right_steps.get(name)
        },
        "plan_fingerprint_equal": left.plan_fingerprint == right.plan_fingerprint,
        "artifact_count_left": len(left.artifacts),
        "artifact_count_right": len(right.artifacts),
    }
