"""Artifact references and materialization strategies for PipelinePlan."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from etlantic.plan.freeze import mutable_copy


class ArtifactStrategy(StrEnum):
    """How a logical OutputRef is realized for consumers."""

    IN_MEMORY = "in_memory"
    LAZY = "lazy"
    DURABLE = "durable"
    EXTERNAL = "external"


@dataclass(frozen=True, slots=True)
class ArtifactRef:
    """Runtime/durable artifact identity (secret-free)."""

    identity: str
    logical_output: str
    strategy: ArtifactStrategy
    security_domain: str = "default"
    cache_key: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize artifact reference."""
        return {
            "identity": self.identity,
            "logical_output": self.logical_output,
            "strategy": self.strategy.value,
            "security_domain": self.security_domain,
            "cache_key": self.cache_key,
            "metadata": mutable_copy(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ArtifactRef:
        """Deserialize artifact reference."""
        return cls(
            identity=str(data["identity"]),
            logical_output=str(data["logical_output"]),
            strategy=ArtifactStrategy(str(data["strategy"])),
            security_domain=str(data.get("security_domain") or "default"),
            cache_key=data.get("cache_key"),
            metadata=dict(data.get("metadata") or {}),
        )


def artifact_identity(
    *,
    pipeline_id: str,
    node_name: str,
    port_name: str,
    security_domain: str,
) -> str:
    """Deterministic artifact identity including security domain."""
    return f"artifact:{security_domain}/{pipeline_id}/{node_name}.{port_name}"


def cache_identity(
    *,
    pipeline_id: str,
    node_name: str,
    port_name: str,
    security_domain: str,
    plan_fingerprint: str,
    ir_fingerprint: str | None = None,
    compiler_fingerprint: str | None = None,
) -> str:
    """Deterministic cache key that cannot cross security domains."""
    parts = [
        f"cache:{security_domain}/{pipeline_id}/",
        f"{node_name}.{port_name}@{plan_fingerprint}",
    ]
    if ir_fingerprint:
        parts.append(f"+ir:{ir_fingerprint}")
    if compiler_fingerprint:
        parts.append(f"+cc:{compiler_fingerprint}")
    return "".join(parts)
