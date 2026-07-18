"""CLI smoke and workflow tests."""

from __future__ import annotations

import json
import re
from importlib.metadata import version
from pathlib import Path

import pytest
import typer
from typer.testing import CliRunner

from etlantic.cli import _build_selection, app

runner = CliRunner(env={"NO_COLOR": "1", "TERM": "dumb"})
_ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;]*m")
_TARGET = "tests.fixtures.sample_pipeline:SamplePipeline"


def _plain_output(result: object) -> str:
    stderr = getattr(result, "stderr", "") or ""
    stdout = getattr(result, "stdout", "") or ""
    return _ANSI_ESCAPE.sub("", stderr + stdout).lower()


def test_cli_version() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert version("etlantic") in result.stdout


def test_cli_validate_sarif() -> None:
    result = runner.invoke(
        app, ["validate", _TARGET, "--profile", "local", "--format", "sarif"]
    )
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["version"] == "2.1.0"
    assert "$schema" in payload or payload.get("runs")


def test_cli_plugin_list() -> None:
    result = runner.invoke(app, ["plugin", "list", "--format", "json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert "plugins" in payload


def test_cli_generate(tmp_path: Path) -> None:
    out = tmp_path / "contracts"
    result = runner.invoke(
        app,
        ["generate", _TARGET, "--output", str(out), "--format", "json"],
    )
    assert result.exit_code == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload.get("ok") is True
    assert out.exists()


def test_cli_viz_lineage() -> None:
    result = runner.invoke(app, ["viz", "lineage", _TARGET, "--format", "json"])
    assert result.exit_code == 0, result.stdout + result.stderr
    assert "etlantic.lineage/1" in result.stdout


def test_cli_validate_and_plan() -> None:
    result = runner.invoke(app, ["validate", _TARGET, "--profile", "local"])
    assert result.exit_code == 0
    result = runner.invoke(
        app, ["plan", _TARGET, "--profile", "local", "--format", "json"]
    )
    assert result.exit_code == 0, result.stderr
    payload = json.loads(result.stdout)
    assert "fingerprint" in payload
    assert "plan_id" in payload
    assert "logical_graph" in payload


def test_cli_plan_explain() -> None:
    result = runner.invoke(
        app, ["plan", "explain", _TARGET, "--profile", "local", "--format", "json"]
    )
    assert result.exit_code == 0, result.stderr
    payload = json.loads(result.stdout)
    assert "fingerprint" in payload
    assert "steps" in payload


def test_cli_run_json() -> None:
    result = runner.invoke(
        app,
        [
            "run",
            _TARGET,
            "--profile",
            "development",
            "--format",
            "json",
            "--no-write",
        ],
    )
    assert result.exit_code == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "succeeded"


def test_cli_diff_emits_structured_report() -> None:
    result = runner.invoke(
        app,
        ["diff", _TARGET, _TARGET, "--kind", "pipeline", "--format", "json"],
    )
    # Same pipeline may still emit compatibility diagnostics depending on DPCS
    # normalization; the CLI must always return a structured report payload.
    assert result.stdout.strip(), result.stderr
    payload = json.loads(result.stdout)
    assert "valid" in payload
    assert "diagnostics" in payload
    assert isinstance(payload["diagnostics"], list)


def test_cli_inspect() -> None:
    result = runner.invoke(app, ["inspect", _TARGET, "--format", "json"])
    assert result.exit_code == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert "nodes" in payload or "pipeline" in str(payload).lower()


def test_build_selection_rejects_conflicting_flags() -> None:
    with pytest.raises(typer.BadParameter, match="only one"):
        _build_selection(run_one="step", run_until="step", nodes=None)


def test_cli_conflicting_selection_flags() -> None:
    result = runner.invoke(
        app,
        [
            "plan",
            _TARGET,
            "--run-one=step",
            "--run-until=step",
        ],
    )
    assert result.exit_code != 0
    output = _plain_output(result)
    assert "only one" in output
