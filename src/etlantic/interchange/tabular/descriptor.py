"""Immutable descriptor for a planned tabular interchange boundary."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from etlantic.interchange.tabular.mechanisms import (
    SCHEMA,
    InterchangeMechanism,
)


class CopyEligibility(StrEnum):
    """Planned copy behavior for an interchange boundary."""

    ELIGIBLE = "eligible"
    COPY_REQUIRED = "copy_required"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class InterchangeDescriptor:
    """Secret-free physical interchange decision recorded in a plan."""

    schema: str
    mechanism: InterchangeMechanism
    producer_engine: str
    consumer_engine: str
    producer_caps: tuple[str, ...]
    consumer_caps: tuple[str, ...]
    schema_fingerprint: str
    ownership: str
    batching: str
    collection: bool
    copy_eligibility: CopyEligibility
    fallback_reason: str | None
    evidence_refs: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        """Serialize the descriptor using only JSON-compatible values."""
        return {
            "schema": self.schema,
            "mechanism": self.mechanism.value,
            "producer_engine": self.producer_engine,
            "consumer_engine": self.consumer_engine,
            "producer_caps": list(self.producer_caps),
            "consumer_caps": list(self.consumer_caps),
            "schema_fingerprint": self.schema_fingerprint,
            "ownership": self.ownership,
            "batching": self.batching,
            "collection": self.collection,
            "copy_eligibility": self.copy_eligibility.value,
            "fallback_reason": self.fallback_reason,
            "evidence_refs": list(self.evidence_refs),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> InterchangeDescriptor:
        """Validate and deserialize an interchange descriptor."""
        from etlantic.interchange.tabular.validate import validate_descriptor

        return validate_descriptor(data)

    def fingerprint_inputs(self) -> dict[str, Any]:
        """Return normalized decision inputs suitable for stable hashing."""
        return {
            "schema": SCHEMA,
            "mechanism": self.mechanism.value,
            "producer_engine": self.producer_engine,
            "consumer_engine": self.consumer_engine,
            "producer_caps": sorted(self.producer_caps),
            "consumer_caps": sorted(self.consumer_caps),
            "ownership": self.ownership,
            "batching": self.batching,
            "collection": self.collection,
            "copy_eligibility": self.copy_eligibility.value,
            "fallback_reason": self.fallback_reason,
        }
