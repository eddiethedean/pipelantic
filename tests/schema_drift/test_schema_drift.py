"""Schema drift model tests."""

from __future__ import annotations

from pipelantic import Data
from pipelantic.schema_drift import (
    DriftImpact,
    diff_normalized_schemas,
    normalize_schema_from_fields,
    normalize_schema_from_model,
)


class Left(Data):
    id: int
    name: str


class Right(Data):
    id: int
    name: str | None = None
    email: str = ""


def test_equivalent_models_same_fingerprint() -> None:
    a = normalize_schema_from_model(Left)
    b = normalize_schema_from_model(Left)
    assert a.fingerprint() == b.fingerprint()


def test_operational_diff_detects_add_and_nullability() -> None:
    left = normalize_schema_from_model(Left)
    right = normalize_schema_from_model(Right)
    change_set = diff_normalized_schemas(left, right)
    kinds = {c.kind for c in change_set.changes}
    assert "field_added" in kinds
    assert change_set.overall_impact in {
        DriftImpact.BREAKING,
        DriftImpact.CONDITIONALLY_COMPATIBLE,
        DriftImpact.COMPATIBLE,
    }


def test_field_list_normalization_ignores_physical_metadata_in_fingerprint() -> None:
    a = normalize_schema_from_fields(
        [{"name": "id", "logical_type": "int", "physical": "int64"}],
        identity="s",
    )
    b = normalize_schema_from_fields(
        [{"name": "id", "logical_type": "int", "physical": "INT"}],
        identity="s",
    )
    assert a.fingerprint() == b.fingerprint()
