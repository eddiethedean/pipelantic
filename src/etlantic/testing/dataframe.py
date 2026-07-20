"""Reusable dataframe plugin conformance helpers."""

from __future__ import annotations

from typing import Any

from etlantic.capabilities import PluginCapabilities
from etlantic.dataframe.protocol import (
    DATAFRAME_PROTOCOL_VERSION,
    ArtifactOwnership,
    DataframeExecutionContext,
    DataframePlugin,
    ValidationDecision,
)


def assert_plugin_info(plugin: DataframePlugin, *, engine: str) -> None:
    """Assert a dataframe plugin advertises the expected engine and protocol."""
    info = plugin.info
    assert info.engine == engine
    assert info.protocol_version == DATAFRAME_PROTOCOL_VERSION
    assert info.capabilities is not None
    assert info.capabilities.supports("dataframe")
    assert info.capabilities.supports("eager")


def assert_roundtrip_records(
    plugin: DataframePlugin,
    *,
    rows: list[dict[str, Any]],
    contract_type: type[Any] | None = None,
) -> None:
    """Assert materialize → validate → to_records preserves row dicts."""
    context = DataframeExecutionContext(
        run_id="conformance",
        pipeline_id="conformance",
        plan_id="plan",
        step_name="step",
        engine=plugin.info.engine,
        collect=True,
    )
    frame = plugin.materialize_input(
        rows, contract_type=contract_type, context=context, port_name="in"
    )
    frame, decision, *_rest = plugin.validate_frame(
        frame,
        contract_type=contract_type,
        context=context,
        boundary="input_validation",
        port_name="in",
    )
    assert decision in {
        ValidationDecision.PASSED,
        ValidationDecision.SKIPPED,
        ValidationDecision.WARNED,
        ValidationDecision.OBSERVED,
    }
    records = plugin.to_records(frame, contract_type=contract_type)
    got = [r.model_dump() if hasattr(r, "model_dump") else dict(r) for r in records]
    assert got == rows


def run_conformance_suite(
    plugin: DataframePlugin,
    *,
    engine: str,
    sample_rows: list[dict[str, Any]],
    contract_type: type[Any] | None = None,
) -> None:
    """Minimal conformance checks for third-party dataframe plugins."""
    assert_plugin_info(plugin, engine=engine)
    caps: PluginCapabilities | None = plugin.info.capabilities
    assert caps is not None
    if engine == "pandas":
        assert caps.supports("lazy") is False
    assert_roundtrip_records(plugin, rows=sample_rows, contract_type=contract_type)
    context = DataframeExecutionContext(
        run_id="conformance",
        pipeline_id="conformance",
        plan_id="plan",
        step_name="step",
        engine=plugin.info.engine,
        collect=False,
        ownership=(
            ArtifactOwnership.COPIED if engine == "pandas" else ArtifactOwnership.SHARED
        ),
    )
    frame = plugin.materialize_input(
        sample_rows, contract_type=contract_type, context=context, port_name="in"
    )
    owned = plugin.ensure_ownership(
        frame, ownership=ArtifactOwnership.COPIED, context=context
    )
    assert owned is not None
    schema = plugin.inspect_schema(frame, identity="conformance:in")
    assert schema is not None
    assert "fields" in schema or "fingerprint" in schema
    # Collect discipline: LazyFrame must stay lazy when collect=False.
    lazy_candidate = frame
    if caps.supports("lazy") and hasattr(frame, "lazy"):
        lazy_candidate = frame.lazy()
    kept = plugin.collect_if_needed(lazy_candidate, context=context)
    if caps.supports("lazy") and type(lazy_candidate).__name__ == "LazyFrame":
        assert type(kept).__name__ == "LazyFrame"
    context_collect = DataframeExecutionContext(
        run_id="conformance",
        pipeline_id="conformance",
        plan_id="plan",
        step_name="step",
        engine=plugin.info.engine,
        collect=True,
    )
    collected = plugin.collect_if_needed(lazy_candidate, context=context_collect)
    assert plugin.row_count(collected) == len(sample_rows)
