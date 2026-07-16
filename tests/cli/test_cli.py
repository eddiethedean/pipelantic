"""CLI smoke tests."""

from __future__ import annotations

from typer.testing import CliRunner

from pipelantic.cli import app

runner = CliRunner()


def test_cli_version() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "0.3.0" in result.stdout


def test_cli_validate_and_plan() -> None:
    target = "tests.fixtures.sample_pipeline:SamplePipeline"
    result = runner.invoke(app, ["validate", target, "--profile", "local"])
    assert result.exit_code == 0
    result = runner.invoke(
        app, ["plan", target, "--profile", "local", "--format", "json"]
    )
    assert result.exit_code == 0, result.stderr
    assert "pipelantic.plan/1" in result.stdout


def test_cli_plan_explain() -> None:
    target = "tests.fixtures.sample_pipeline:SamplePipeline"
    result = runner.invoke(
        app, ["plan", "explain", target, "--profile", "local", "--format", "json"]
    )
    assert result.exit_code == 0, result.stderr
    assert "fingerprint" in result.stdout
    assert "steps" in result.stdout


def test_cli_conflicting_selection_flags() -> None:
    target = "tests.fixtures.sample_pipeline:SamplePipeline"
    result = runner.invoke(
        app,
        [
            "plan",
            target,
            "--run-one",
            "step",
            "--run-until",
            "step",
        ],
    )
    assert result.exit_code != 0
    assert "run-one" in (result.stderr + result.stdout).lower()
