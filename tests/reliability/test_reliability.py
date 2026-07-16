"""Reliability model smoke tests."""

from __future__ import annotations

from pipelantic.reliability import (
    FreshnessExpectation,
    IdempotencyDeclaration,
    MaterializationIntent,
    MaterializationMode,
    WriteIntent,
    WriteMode,
    environment_identity,
    fingerprint_mapping,
)


def test_reliability_identities() -> None:
    freshness = FreshnessExpectation(subject_id="customers", max_age_seconds=3600)
    assert freshness.identity().startswith("freshness:")
    write = WriteIntent(subject_id="curated", mode=WriteMode.MERGE, keys=("id",))
    assert write.to_dict()["mode"] == "merge"
    mat = MaterializationIntent(subject_id="curated", mode=MaterializationMode.PUBLISH)
    assert "publish" in mat.identity()
    idem = IdempotencyDeclaration(subject_id="curated", keys=("id",))
    assert idem.keys == ("id",)
    assert environment_identity(profile="prod", security_domain="production")
    assert len(fingerprint_mapping({"a": 1})) == 64
