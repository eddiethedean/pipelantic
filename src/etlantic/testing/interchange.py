"""Lightweight conformance smoke tests for tabular interchange capabilities."""

from __future__ import annotations

import hashlib
import json

from etlantic.capabilities import PluginCapabilities
from etlantic.dataframe.arrow import arrow_available
from etlantic.interchange.tabular import (
    SCHEMA,
    CopyEligibility,
    InterchangeDescriptor,
    InterchangeMechanism,
    select_mechanism,
)


def run_tabular_interchange_conformance_smoke(
    producer_caps: PluginCapabilities,
    consumer_caps: PluginCapabilities,
) -> InterchangeDescriptor:
    """Select and round-trip a descriptor from two capability declarations."""
    mechanism, fallback_reason = select_mechanism(
        producer_caps,
        consumer_caps,
        durable=False,
        already_collecting=True,
        pyarrow_available=arrow_available(),
    )
    fingerprint_payload = {
        "consumer_engine": consumer_caps.engine,
        "mechanism": mechanism.value,
        "producer_engine": producer_caps.engine,
    }
    schema_fingerprint = hashlib.sha256(
        json.dumps(fingerprint_payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    copy_required = not producer_caps.thread_safe or mechanism in {
        InterchangeMechanism.NATIVE_FALLBACK,
        InterchangeMechanism.RECORDS_FALLBACK,
    }
    descriptor = InterchangeDescriptor(
        schema=SCHEMA,
        mechanism=mechanism,
        producer_engine=producer_caps.engine,
        consumer_engine=consumer_caps.engine,
        producer_caps=tuple(sorted(producer_caps.interchange_mechanisms)),
        consumer_caps=tuple(sorted(consumer_caps.interchange_mechanisms)),
        schema_fingerprint=schema_fingerprint,
        ownership="copied" if copy_required else "shared",
        batching="collected",
        collection=True,
        copy_eligibility=(
            CopyEligibility.COPY_REQUIRED if copy_required else CopyEligibility.UNKNOWN
        ),
        fallback_reason=fallback_reason,
        evidence_refs=(),
    )
    round_tripped = InterchangeDescriptor.from_dict(descriptor.to_dict())
    if round_tripped != descriptor:
        raise AssertionError("Interchange descriptor round-trip changed values")
    return round_tripped


__all__ = ["run_tabular_interchange_conformance_smoke"]
