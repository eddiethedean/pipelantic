"""Normalize SparkForge-shaped run results into PipelineRunReport."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from etlantic.reports.model import (
    ArtifactResult,
    PipelineRunReport,
    RunDiagnostic,
    RunSummary,
    StepRunReport,
    ValidationResult,
)
from etlantic.runtime.request import RunIntent
from etlantic.runtime.state import RunStatus, StepStatus

_SECRET_KEYS = frozenset(
    {
        "password",
        "secret",
        "token",
        "api_key",
        "apikey",
        "credential",
        "private_key",
    }
)


def _redact(value: Any) -> Any:
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, item in value.items():
            if any(s in str(key).lower() for s in _SECRET_KEYS):
                out[str(key)] = "***"
            else:
                out[str(key)] = _redact(item)
        return out
    if isinstance(value, list):
        return [_redact(v) for v in value]
    return value


def adapt_run_result(
    payload: dict[str, Any],
    *,
    pipeline_id: str | None = None,
    profile: str = "sparkforge",
) -> PipelineRunReport:
    """Convert a SparkForge-shaped result dict into PipelineRunReport.

    Never retains secret-like keys from the source payload.
    """
    safe = _redact(payload)
    status_raw = str(safe.get("status") or safe.get("pipeline_status") or "succeeded")
    try:
        status = RunStatus(status_raw.lower())
    except ValueError:
        status = (
            RunStatus.FAILED
            if status_raw.lower() in {"failed", "error", "failure"}
            else RunStatus.SUCCEEDED
        )

    steps_raw = safe.get("steps") or safe.get("step_results") or []
    steps: list[StepRunReport] = []
    for item in steps_raw:
        if not isinstance(item, dict):
            continue
        step_status_raw = str(item.get("status") or "succeeded").lower()
        try:
            step_status = StepStatus(step_status_raw)
        except ValueError:
            step_status = (
                StepStatus.FAILED if "fail" in step_status_raw else StepStatus.SUCCEEDED
            )
        name = str(item.get("name") or item.get("step_name") or "step")
        steps.append(
            StepRunReport(
                step_id=str(item.get("step_id") or name),
                step_name=name,
                status=step_status,
                attempts=int(item.get("attempts") or 1),
                error_message=item.get("error") or item.get("error_message"),
                records_in=item.get("records_in") or item.get("input_count"),
                records_out=item.get("records_out") or item.get("output_count"),
                metadata={
                    k: v
                    for k, v in item.items()
                    if k
                    not in {
                        "name",
                        "step_name",
                        "step_id",
                        "status",
                        "attempts",
                        "error",
                        "error_message",
                        "records_in",
                        "records_out",
                        "input_count",
                        "output_count",
                    }
                },
            )
        )

    validations: list[ValidationResult] = []
    for item in safe.get("validations") or safe.get("quality_results") or []:
        if not isinstance(item, dict):
            continue
        validations.append(
            ValidationResult(
                node_name=str(item.get("node_name") or item.get("step") or "unknown"),
                boundary=str(item.get("boundary") or "quality_gate"),
                status=str(item.get("status") or "passed"),
                message=item.get("message"),
                records_checked=item.get("records_checked") or item.get("total"),
                records_invalid=item.get("records_invalid") or item.get("invalid"),
            )
        )

    artifacts: list[ArtifactResult] = []
    for item in safe.get("artifacts") or safe.get("tables") or []:
        if not isinstance(item, dict):
            continue
        identity = str(
            item.get("identity") or item.get("table") or item.get("name") or ""
        )
        if not identity:
            continue
        artifacts.append(
            ArtifactResult(
                identity=identity,
                logical_output=str(item.get("logical_output") or identity),
                strategy=str(item.get("strategy") or "external"),
                status=str(item.get("status") or "available"),
                record_count=item.get("record_count") or item.get("count"),
            )
        )

    diagnostics: list[RunDiagnostic] = []
    for item in safe.get("diagnostics") or safe.get("errors") or []:
        if isinstance(item, str):
            diagnostics.append(
                RunDiagnostic(code="PMSF500", severity="error", message=item)
            )
        elif isinstance(item, dict):
            diagnostics.append(
                RunDiagnostic(
                    code=str(item.get("code") or "PMSF500"),
                    severity=str(item.get("severity") or "error"),
                    message=str(item.get("message") or item),
                )
            )

    succeeded = sum(1 for s in steps if s.status is StepStatus.SUCCEEDED)
    failed = sum(1 for s in steps if s.status is StepStatus.FAILED)
    summary = RunSummary(
        total_steps=len(steps),
        succeeded=succeeded,
        failed=failed,
        records_in=safe.get("records_in"),
        records_out=safe.get("records_out"),
    )

    started = safe.get("started_at")
    if isinstance(started, str):
        started_at = datetime.fromisoformat(started.replace("Z", "+00:00"))
    else:
        started_at = datetime.now(UTC)

    intent_raw = str(safe.get("intent") or safe.get("mode") or "standard").lower()
    try:
        from etlantic_sparkforge.runtime_map import intent_from_sparkforge

        intent = intent_from_sparkforge(intent_raw)
    except ValueError:
        intent = RunIntent.STANDARD

    return PipelineRunReport(
        pipeline_id=str(
            pipeline_id
            or safe.get("pipeline_id")
            or safe.get("pipeline")
            or "sparkforge"
        ),
        plan_id=str(safe.get("plan_id") or "plan:sparkforge-adapted"),
        run_id=str(safe.get("run_id") or safe.get("execution_id") or "run-sparkforge"),
        intent=intent,
        profile=profile,
        status=status,
        started_at=started_at,
        summary=summary,
        steps=tuple(steps),
        artifacts=tuple(artifacts),
        validations=tuple(validations),
        diagnostics=tuple(diagnostics),
        metadata={
            "adapter": "etlantic-sparkforge",
            "source_keys": sorted(safe.keys()),
        },
    )


def report_to_sparkforge_explain(report: PipelineRunReport) -> dict[str, Any]:
    """Dual-reporting helper: ETLantic report → SparkForge-shaped explain dict."""
    return {
        "pipeline_id": report.pipeline_id,
        "run_id": report.run_id,
        "status": report.status.value,
        "mode": report.intent.value,
        "steps": [
            {
                "name": s.step_name,
                "status": s.status.value,
                "records_in": s.records_in,
                "records_out": s.records_out,
            }
            for s in report.steps
        ],
        "validations": [v.to_dict() for v in report.validations],
        "summary": report.summary.to_dict(),
    }
