"""Integration tests: profile-aware plugin discovery on real entry paths."""

from __future__ import annotations

from importlib.metadata import EntryPoint
from unittest.mock import MagicMock

import pytest

from etlantic.lifecycle.runtime import PipelineRuntime
from etlantic.plugin_lifecycle import DiscoveredPlugin
from etlantic.profile import Profile, production_profile
from etlantic.registry import PlanningContext

_LOAD_COUNT = {"value": 0}


def _fake_discovered(*, group: str, name: str = "evil") -> DiscoveredPlugin:
    def _load() -> object:
        _LOAD_COUNT["value"] += 1
        return MagicMock()

    ep = MagicMock(spec=EntryPoint)
    ep.name = name
    ep.value = "evil.module:factory"
    ep.group = group
    ep.load = _load
    return DiscoveredPlugin(
        group=group,
        name=name,
        target="evil.module:factory",
        distribution_name="evil-plugin",
        distribution_version="9.9.9",
        entry_point=ep,
    )


@pytest.fixture(autouse=True)
def _reset_load_count() -> None:
    _LOAD_COUNT["value"] = 0


def test_runtime_production_deny_does_not_load(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = _fake_discovered(group="etlantic.dataframe_plugins")

    def _discover(group: str) -> tuple[list[DiscoveredPlugin], list]:
        if group == "etlantic.dataframe_plugins":
            return [fake], []
        return [], []

    monkeypatch.setattr("etlantic.plugin_lifecycle.discover_entry_points", _discover)
    runtime = PipelineRuntime()
    profile = production_profile(plugin_allowlist={"only-local": "==1.0.0"})
    runtime.ensure_plugins_for_profile(profile)
    assert _LOAD_COUNT["value"] == 0
    assert "evil" not in runtime.dataframe_plugins


def test_planning_context_production_deny_does_not_load(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake = _fake_discovered(group="etlantic.dataframe_plugins")

    def _discover(group: str) -> tuple[list[DiscoveredPlugin], list]:
        if group == "etlantic.dataframe_plugins":
            return [fake], []
        return [], []

    monkeypatch.setattr("etlantic.plugin_lifecycle.discover_entry_points", _discover)
    profile = Profile(
        name="production",
        security_mode="production",
        dataframe_engine="polars",
        plugin_allowlist={"only-local": "==1.0.0"},
    )
    PlanningContext.create(profile=profile)
    assert _LOAD_COUNT["value"] == 0


def test_runtime_development_allowlist_empty_loads(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake = _fake_discovered(group="etlantic.dataframe_plugins")

    def _discover(group: str) -> tuple[list[DiscoveredPlugin], list]:
        if group == "etlantic.dataframe_plugins":
            return [fake], []
        return [], []

    monkeypatch.setattr("etlantic.plugin_lifecycle.discover_entry_points", _discover)
    runtime = PipelineRuntime()
    profile = Profile(name="dev", security_mode="development")
    runtime.ensure_plugins_for_profile(profile)
    assert _LOAD_COUNT["value"] == 1
    assert len(runtime.dataframe_plugins) == 1
