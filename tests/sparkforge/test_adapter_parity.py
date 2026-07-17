"""SparkForge adapter parity tests (IR fixtures — no SparkForge install required)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

pytest.importorskip("etlantic_sparkforge")

from etlantic.plan import explain_plan, plan_pipeline
from etlantic.reliability import WriteMode
from etlantic.runtime.request import MaterializationPolicy, RunIntent
from etlantic_sparkforge import (
    COMPATIBILITY_MATRIX,
    AdapterError,
    SparkForgePipelineSpec,
    adapt_pipeline,
    adapt_run_result,
    assert_delta_capabilities,
    debug_request_from_sparkforge,
    intent_from_sparkforge,
    report_to_sparkforge_explain,
    selection_from_sparkforge,
    write_mode_from_sparkforge,
)

pytestmark = pytest.mark.sparkforge

FIXTURES = Path(__file__).parent / "fixtures"


def _load_ecommerce() -> SparkForgePipelineSpec:
    data = json.loads((FIXTURES / "ecommerce.json").read_text(encoding="utf-8"))
    return SparkForgePipelineSpec.from_dict(data)


def test_adapt_ecommerce_pipeline_parity() -> None:
    spec = _load_ecommerce()
    result = adapt_pipeline(spec)
    graph = result.pipeline_cls.inspect()
    names = [n.name for n in graph.nodes]
    expected = spec.metadata["expected_node_order"]
    assert names == expected
    assert result.layer_by_node["orders"] == "bronze"
    assert result.layer_by_node["clean_orders"] == "silver"
    assert result.layer_by_node["order_kpis"] == "gold"
    # Core graph kinds are never medallion enums.
    assert all(n.kind.value in {"source", "step", "sink"} for n in graph.nodes)
    report = result.pipeline_cls.validate(profile=result.profile)
    assert report.valid


def test_dependency_closure_and_plan_explain() -> None:
    result = adapt_pipeline(_load_ecommerce())
    plan = plan_pipeline(result.pipeline_cls, profile=result.profile)
    assert plan is not None
    explained = explain_plan(plan)
    assert "fingerprint" in explained or "plan_id" in explained or "steps" in explained
    assert plan.logical_graph.nodes


def test_write_intent_parity() -> None:
    result = adapt_pipeline(_load_ecommerce())
    by_subject = {w.subject_id: w.mode for w in result.write_intents}
    assert by_subject["silver_orders"] is WriteMode.OVERWRITE
    assert by_subject["gold_order_kpis"] is WriteMode.MERGE
    expected = _load_ecommerce().metadata["expected_write_modes"]
    assert by_subject["silver_orders"].value == expected["silver_orders"]
    assert by_subject["gold_order_kpis"].value == expected["gold_order_kpis"]


def test_validation_policy_thresholds() -> None:
    result = adapt_pipeline(_load_ecommerce())
    meta = result.validation_policy.metadata
    assert meta["min_accept_rate_ingest"] == 90.0
    assert meta["min_accept_rate_clean"] == 95.0
    assert meta["min_accept_rate_publish"] == 98.0


def test_runtime_mapping() -> None:
    assert intent_from_sparkforge("initial_load") is RunIntent.INITIALIZE
    assert intent_from_sparkforge("incremental") is RunIntent.INCREMENTAL
    assert intent_from_sparkforge("validation_only") is RunIntent.VALIDATE
    assert selection_from_sparkforge(run_until="clean_orders").kind == "until"
    assert selection_from_sparkforge(run_one="orders").kind == "only"
    req = debug_request_from_sparkforge(mode="full_refresh", skip_writes=True)
    assert req.intent is RunIntent.REFRESH
    assert req.no_write is True
    assert req.materialization is MaterializationPolicy.NONE


def test_report_normalization_and_redaction() -> None:
    payload = {
        "status": "succeeded",
        "pipeline": "ecommerce",
        "run_id": "sf-1",
        "mode": "incremental",
        "password": "should-not-leak",
        "steps": [
            {"name": "orders", "status": "succeeded", "records_out": 10},
            {"name": "clean_orders", "status": "succeeded", "records_out": 9},
        ],
        "validations": [
            {
                "step": "orders",
                "status": "passed",
                "total": 10,
                "invalid": 0,
            }
        ],
        "tables": [{"table": "silver_orders", "count": 9}],
        "secrets": {"api_key": "xyz"},
    }
    report = adapt_run_result(payload)
    dumped = report.to_dict()
    text = json.dumps(dumped)
    assert "should-not-leak" not in text
    assert "xyz" not in text
    assert report.status.value == "succeeded"
    assert len(report.steps) == 2
    assert report.intent is RunIntent.INCREMENTAL
    explain = report_to_sparkforge_explain(report)
    assert explain["run_id"] == "sf-1"
    assert explain["mode"] == "incremental"


def test_delta_fail_closed_without_capabilities() -> None:
    diags = assert_delta_capabilities(["merge", "vacuum"])
    assert any(d.code == "PMSF322" for d in diags)
    assert all(d.severity.value == "error" for d in diags)


def test_delta_ops_in_spec_fail_adapt() -> None:
    data = json.loads((FIXTURES / "ecommerce.json").read_text(encoding="utf-8"))
    data["metadata"] = {**data.get("metadata", {}), "delta_operations": ["merge"]}
    spec = SparkForgePipelineSpec.from_dict(data)
    with pytest.raises(AdapterError) as exc:
        adapt_pipeline(spec)
    assert exc.value.code == "PMSF320"


def test_cycle_fail_closed() -> None:
    data = {
        "name": "cyclic",
        "steps": [
            {
                "name": "a",
                "kind": "silver_transform",
                "layer": "silver",
                "source": "b",
            },
            {
                "name": "b",
                "kind": "silver_transform",
                "layer": "silver",
                "source": "a",
            },
        ],
    }
    with pytest.raises(AdapterError):
        adapt_pipeline(SparkForgePipelineSpec.from_dict(data))


def test_compatibility_matrix_present() -> None:
    assert "write" in COMPATIBILITY_MATRIX
    assert write_mode_from_sparkforge("append") is WriteMode.APPEND


def test_core_has_no_medallion_enums() -> None:
    import inspect

    import etlantic

    src = Path(inspect.getfile(etlantic)).parent
    offenders: list[str] = []
    for path in src.rglob("*.py"):
        text = path.read_text(encoding="utf-8").lower()
        # Allow comments about SparkForge boundary in docs strings sparingly —
        # fail if identifiers introduce medallion types.
        if "class bronze" in text or "class silver" in text or "class gold" in text:
            offenders.append(str(path))
        if "layerkind" in text or "medallionlayer" in text:
            offenders.append(str(path))
    assert offenders == []
