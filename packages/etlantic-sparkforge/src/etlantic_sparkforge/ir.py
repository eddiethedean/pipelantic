"""SparkForge-independent intermediate IR for migration mapping.

Medallion layer names live only in this adapter package — never in ETLantic core.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class LayerKind(StrEnum):
    """SparkForge medallion layer (adapter-only vocabulary)."""

    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"


class StepKind(StrEnum):
    """SparkForge step kinds represented in the compatibility IR."""

    BRONZE_RULES = "bronze_rules"
    SILVER_TRANSFORM = "silver_transform"
    GOLD_TRANSFORM = "gold_transform"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class SparkForgeStepSpec:
    """One SparkForge step in secret-free form."""

    name: str
    kind: StepKind
    layer: LayerKind
    source: str | None = None
    table_name: str | None = None
    transform_ref: str | None = None
    rules: dict[str, Any] = field(default_factory=dict)
    write_mode: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "kind": self.kind.value,
            "layer": self.layer.value,
            "source": self.source,
            "table_name": self.table_name,
            "transform_ref": self.transform_ref,
            "rules": dict(self.rules),
            "write_mode": self.write_mode,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SparkForgeStepSpec:
        kind_raw = str(data.get("kind") or StepKind.UNKNOWN.value)
        try:
            kind = StepKind(kind_raw)
        except ValueError:
            kind = StepKind.UNKNOWN
        layer_raw = str(data.get("layer") or LayerKind.BRONZE.value)
        try:
            layer = LayerKind(layer_raw)
        except ValueError:
            layer = LayerKind.BRONZE
        return cls(
            name=str(data["name"]),
            kind=kind,
            layer=layer,
            source=data.get("source"),
            table_name=data.get("table_name"),
            transform_ref=data.get("transform_ref"),
            rules=dict(data.get("rules") or {}),
            write_mode=data.get("write_mode"),
            metadata=dict(data.get("metadata") or {}),
        )


@dataclass(frozen=True, slots=True)
class SparkForgePipelineSpec:
    """Complete SparkForge pipeline description (fixture-friendly)."""

    name: str
    schema: str = "default"
    steps: tuple[SparkForgeStepSpec, ...] = ()
    min_bronze_rate: float = 90.0
    min_silver_rate: float = 95.0
    min_gold_rate: float = 98.0
    engine: str = "spark"
    legacy_engine_extensions: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "schema": self.schema,
            "steps": [s.to_dict() for s in self.steps],
            "min_bronze_rate": self.min_bronze_rate,
            "min_silver_rate": self.min_silver_rate,
            "min_gold_rate": self.min_gold_rate,
            "engine": self.engine,
            "legacy_engine_extensions": list(self.legacy_engine_extensions),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SparkForgePipelineSpec:
        steps = tuple(
            SparkForgeStepSpec.from_dict(item)
            for item in (data.get("steps") or ())
            if isinstance(item, dict)
        )
        return cls(
            name=str(data.get("name") or "AdaptedPipeline"),
            schema=str(data.get("schema") or "default"),
            steps=steps,
            min_bronze_rate=float(data.get("min_bronze_rate") or 90.0),
            min_silver_rate=float(data.get("min_silver_rate") or 95.0),
            min_gold_rate=float(data.get("min_gold_rate") or 98.0),
            engine=str(data.get("engine") or "spark"),
            legacy_engine_extensions=tuple(
                str(x) for x in (data.get("legacy_engine_extensions") or ())
            ),
            metadata=dict(data.get("metadata") or {}),
        )
