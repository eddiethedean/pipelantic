"""Fail-closed tests for interchange descriptor validation."""

from __future__ import annotations

import pytest

from etlantic.interchange.tabular import (
    SCHEMA,
    CopyEligibility,
    InterchangeDescriptor,
    InterchangeDescriptorError,
    InterchangeMechanism,
    validate_descriptor,
)


def _descriptor_data() -> dict[str, object]:
    return {
        "schema": SCHEMA,
        "mechanism": "arrow_c_stream",
        "producer_engine": "polars",
        "consumer_engine": "pandas",
        "producer_caps": ["arrow_c_stream"],
        "consumer_caps": ["arrow_c_stream"],
        "schema_fingerprint": "sha256:logical",
        "ownership": "producer",
        "batching": "stream:65536",
        "collection": False,
        "copy_eligibility": "eligible",
        "fallback_reason": None,
        "evidence_refs": [],
    }


def test_valid_descriptor_round_trips() -> None:
    descriptor = validate_descriptor(_descriptor_data())
    assert descriptor.mechanism is InterchangeMechanism.ARROW_C_STREAM
    assert descriptor.copy_eligibility is CopyEligibility.ELIGIBLE
    assert InterchangeDescriptor.from_dict(descriptor.to_dict()) == descriptor
    assert "schema_fingerprint" not in descriptor.fingerprint_inputs()
    assert "evidence_refs" not in descriptor.fingerprint_inputs()


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("schema", "etlantic.interchange/2"),
        ("mechanism", "invented_arrow"),
        ("copy_eligibility", "probably"),
        ("collection", 1),
    ],
)
def test_invented_or_invalid_values_fail_closed(
    field: str,
    value: object,
) -> None:
    data = _descriptor_data()
    data[field] = value
    with pytest.raises(InterchangeDescriptorError):
        validate_descriptor(data)


def test_unknown_fields_fail_closed() -> None:
    data = _descriptor_data()
    data["live_arrow_handle"] = object()
    with pytest.raises(InterchangeDescriptorError):
        validate_descriptor(data)


def test_fallback_requires_reason() -> None:
    data = _descriptor_data()
    data["mechanism"] = "records_fallback"
    with pytest.raises(InterchangeDescriptorError):
        validate_descriptor(data)
