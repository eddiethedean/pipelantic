"""Regression tests for 0.3 deep-dive interchange fixes."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

import pytest

from pipelantic import Data, Input, Output, Pipeline, Sink, Source, Transformation
from pipelantic.identity import identity_slug
from pipelantic.interchange.bundle import BundleError, generate_contracts
from pipelantic.interchange.diff import diff_pipelines, diff_transformations
from pipelantic.interchange.dtcs import (
    _annotation_for_dtcs_type,
    transformation_from_dtcs,
    transformation_to_dtcs,
)


class Event(Data):
    when: datetime
    score: Decimal


class Emit(Transformation):
    events: Input[Event]
    result: Output[Event]


class Left(Data):
    __published_id__ = "X"
    id: int


class Right(Data):
    __published_id__ = "x"
    id: int


class CollisionTransform(Transformation):
    left: Input[Left]
    right: Input[Right]
    result: Output[Left]


class CollisionPipeline(Pipeline):
    a: Source[Left] = Source(binding="a")
    b: Source[Right] = Source(binding="b")
    step = CollisionTransform.step(left=a, right=b)
    out: Sink[Left] = Sink(input=step.result, binding="out")


def test_annotation_for_dtcs_types() -> None:
    assert _annotation_for_dtcs_type("datetime") is datetime
    assert _annotation_for_dtcs_type("decimal") is Decimal
    assert _annotation_for_dtcs_type("binary") is bytes
    assert _annotation_for_dtcs_type("integer") is int


def test_schema_only_dtcs_preserves_datetime_decimal() -> None:
    doc = transformation_to_dtcs(Emit)
    # Strip contract ids so load falls back to schema-only synthetic types
    for port in (*doc.get("inputs", ()), *doc.get("outputs", ())):
        port.pop("pipelantic:contractId", None)
        port.pop("pipelantic:contractVersion", None)
        port.pop("contractId", None)
        ref = port.get("contractRef")
        if isinstance(ref, dict):
            ref.pop("id", None)

    loaded = transformation_from_dtcs(doc)
    out = loaded.outputs()[0]
    assert out.contract_type is not None
    fields = out.contract_type.model_fields
    assert fields["when"].annotation is datetime
    assert fields["score"].annotation is Decimal


def test_diff_pipelines_returns_report_on_garbage() -> None:
    report = diff_pipelines({"a": 1}, {"b": 2})
    assert report.has_errors
    assert any(d.code == "PMGEN311" for d in report.errors)


def test_diff_transformations_returns_report_on_garbage() -> None:
    report = diff_transformations(
        {"dtcsVersion": "1.0.0"},
        {"dtcsVersion": "1.0.0"},
    )
    assert report.has_errors
    assert any(d.code in {"PMGEN203", "PMGEN301"} for d in report.errors)


def test_bundle_rejects_slug_collision() -> None:
    assert identity_slug("X") == identity_slug("x")
    with pytest.raises(BundleError) as exc:
        generate_contracts(CollisionPipeline)
    report = exc.value.report
    assert report is not None
    assert any(d.code == "PMGEN233" for d in report.diagnostics) or (
        "collision" in str(exc.value).lower()
    )
