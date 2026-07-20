"""Optional isolated capability probe for plugins (0.20).

Process isolation is containment with budgets — not a complete sandbox.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from etlantic.diagnostics import Diagnostic, Severity
from etlantic.runtime.events import SecurityEvent

_PROBE_SCRIPT = r"""
import json
import sys
import traceback

payload = json.loads(sys.stdin.read())
group = payload.get("group")
name = payload.get("name")
target = payload.get("target")
try:
    from importlib.metadata import entry_points
    try:
        eps = list(entry_points(group=group))
    except TypeError:
        eps = list(entry_points().get(group, []))
    match = next((ep for ep in eps if ep.name == name), None)
    if match is None:
        print(json.dumps({"ok": False, "error": "entry point not found"}))
        sys.exit(2)
    if match.value != target:
        print(json.dumps({"ok": False, "error": "target mismatch"}))
        sys.exit(3)
    factory = match.load()
    plugin = factory() if callable(factory) else factory
    info = getattr(plugin, "info", None)
    caps = getattr(info, "capabilities", None)
    summary = {
        "ok": True,
        "name": getattr(info, "name", name),
        "engine": getattr(info, "engine", None),
        "version": getattr(info, "version", None),
        "protocol": getattr(info, "protocol_version", None)
        or getattr(info, "protocol", None),
        "capabilities": caps.to_dict() if caps is not None and hasattr(caps, "to_dict") else None,
    }
    print(json.dumps(summary))
except Exception as exc:
    print(json.dumps({"ok": False, "error": str(exc), "trace": traceback.format_exc()[-2000:]}))
    sys.exit(1)
"""


@dataclass(frozen=True, slots=True)
class CapabilityProbeConfig:
    """Budgets for an isolated plugin capability probe."""

    enabled: bool = False
    timeout_seconds: float = 5.0
    max_output_bytes: int = 65_536

    def to_dict(self) -> dict[str, Any]:
        return {
            "enabled": self.enabled,
            "timeout_seconds": self.timeout_seconds,
            "max_output_bytes": self.max_output_bytes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> CapabilityProbeConfig:
        data = dict(data or {})
        return cls(
            enabled=bool(data.get("enabled", False)),
            timeout_seconds=float(data.get("timeout_seconds") or 5.0),
            max_output_bytes=int(data.get("max_output_bytes") or 65_536),
        )


@dataclass(frozen=True, slots=True)
class CapabilityProbeResult:
    ok: bool
    summary: dict[str, Any]
    diagnostics: tuple[Diagnostic, ...] = ()
    event: SecurityEvent | None = None


def run_capability_probe(
    *,
    group: str,
    name: str,
    target: str,
    config: CapabilityProbeConfig,
    run_id: str = "probe",
) -> CapabilityProbeResult:
    """Probe a plugin in a subprocess with strict time/output budgets.

    Contained process isolation — not a sandbox for untrusted code.
    """
    if not config.enabled:
        return CapabilityProbeResult(
            ok=True,
            summary={"skipped": True},
            event=SecurityEvent(
                kind="capability_probe",
                run_id=run_id,
                provider=name,
                outcome="skipped",
                message="Capability probe disabled.",
                subject=name,
            ),
        )

    payload = json.dumps({"group": group, "name": name, "target": target})
    try:
        completed = subprocess.run(
            [sys.executable, "-c", _PROBE_SCRIPT],
            input=payload.encode("utf-8"),
            capture_output=True,
            timeout=config.timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired:
        diag = Diagnostic(
            code="PMPLUG430",
            severity=Severity.ERROR,
            message=f"Capability probe timed out for {group}:{name}",
            phase="plugin_probe",
            path=("plugin", name),
        )
        return CapabilityProbeResult(
            ok=False,
            summary={"ok": False, "error": "timeout"},
            diagnostics=(diag,),
            event=SecurityEvent(
                kind="capability_probe",
                run_id=run_id,
                provider=name,
                outcome="denied",
                message="timeout",
                subject=name,
            ),
        )

    raw = completed.stdout[: config.max_output_bytes]
    if len(completed.stdout) > config.max_output_bytes:
        diag = Diagnostic(
            code="PMPLUG431",
            severity=Severity.ERROR,
            message=f"Capability probe output exceeded budget for {group}:{name}",
            phase="plugin_probe",
            path=("plugin", name),
        )
        return CapabilityProbeResult(
            ok=False,
            summary={"ok": False, "error": "output_budget"},
            diagnostics=(diag,),
            event=SecurityEvent(
                kind="capability_probe",
                run_id=run_id,
                provider=name,
                outcome="denied",
                message="output_budget",
                subject=name,
            ),
        )

    try:
        summary = json.loads(raw.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        summary = {"ok": False, "error": "invalid probe output"}

    ok = bool(summary.get("ok")) and completed.returncode == 0
    outcome = "allowed" if ok else "denied"
    diags: list[Diagnostic] = []
    if not ok:
        diags.append(
            Diagnostic(
                code="PMPLUG432",
                severity=Severity.ERROR,
                message=(
                    f"Capability probe failed for {group}:{name}: "
                    f"{summary.get('error', 'unknown')}"
                ),
                phase="plugin_probe",
                path=("plugin", name),
            )
        )
    return CapabilityProbeResult(
        ok=ok,
        summary=dict(summary),
        diagnostics=tuple(diags),
        event=SecurityEvent(
            kind="capability_probe",
            run_id=run_id,
            provider=name,
            outcome=outcome,
            message=str(summary.get("error") or "ok"),
            subject=name,
            metadata={"returncode": completed.returncode},
        ),
    )


def write_probe_fixture(path: str | Path, payload: dict[str, Any]) -> Path:
    """Helper for tests — write a probe request fixture."""
    resolved = Path(path)
    resolved.write_text(json.dumps(payload), encoding="utf-8")
    return resolved


def probe_temp_dir() -> tempfile.TemporaryDirectory[str]:
    return tempfile.TemporaryDirectory(prefix="etlantic-probe-")
