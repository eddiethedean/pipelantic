"""Plugin capability declarations and negotiation results."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class CapabilityDecision(StrEnum):
    """Outcome of comparing required vs available capabilities."""

    SUPPORTED = "supported"
    FALLBACK = "fallback"
    UNSUPPORTED = "unsupported"


@dataclass(frozen=True, slots=True)
class PluginCapabilities:
    """Declared capabilities of a plugin or engine."""

    engine: str
    async_execution: bool = False
    streaming: bool = False
    transactions: bool = False
    checkpoints: bool = False
    sql: bool = False
    spark: bool = False
    dataframe: bool = True
    secret_provider: bool = False
    extras: frozenset[str] = field(default_factory=frozenset)

    def supports(self, requirement: str) -> bool:
        """Return True when this capability set covers ``requirement``."""
        known = {
            "async": self.async_execution,
            "async_execution": self.async_execution,
            "streaming": self.streaming,
            "transactions": self.transactions,
            "checkpoints": self.checkpoints,
            "sql": self.sql,
            "spark": self.spark,
            "dataframe": self.dataframe,
            "secret_provider": self.secret_provider,
        }
        if requirement in known:
            return known[requirement]
        return requirement in self.extras

    def to_dict(self) -> dict[str, Any]:
        """Serialize capabilities."""
        return {
            "engine": self.engine,
            "async_execution": self.async_execution,
            "streaming": self.streaming,
            "transactions": self.transactions,
            "checkpoints": self.checkpoints,
            "sql": self.sql,
            "spark": self.spark,
            "dataframe": self.dataframe,
            "secret_provider": self.secret_provider,
            "extras": sorted(self.extras),
        }


@dataclass(frozen=True, slots=True)
class CapabilityNegotiation:
    """Record of a capability check for one requirement."""

    requirement: str
    engine: str
    decision: CapabilityDecision
    fallback_engine: str | None = None
    message: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize negotiation record."""
        return {
            "requirement": self.requirement,
            "engine": self.engine,
            "decision": self.decision.value,
            "fallback_engine": self.fallback_engine,
            "message": self.message,
        }


def negotiate_capabilities(
    *,
    requirements: list[str],
    available: PluginCapabilities,
    fallback: PluginCapabilities | None = None,
    allow_fallback: bool = False,
) -> list[CapabilityNegotiation]:
    """Negotiate required capabilities against an available engine.

    Unsupported requirements fail closed unless ``allow_fallback`` is True and
    a fallback engine covers the requirement.
    """
    results: list[CapabilityNegotiation] = []
    for requirement in requirements:
        if available.supports(requirement):
            results.append(
                CapabilityNegotiation(
                    requirement=requirement,
                    engine=available.engine,
                    decision=CapabilityDecision.SUPPORTED,
                )
            )
            continue
        if allow_fallback and fallback is not None and fallback.supports(requirement):
            results.append(
                CapabilityNegotiation(
                    requirement=requirement,
                    engine=available.engine,
                    decision=CapabilityDecision.FALLBACK,
                    fallback_engine=fallback.engine,
                    message=(
                        f"Requirement {requirement!r} unsupported by "
                        f"{available.engine}; using fallback {fallback.engine}."
                    ),
                )
            )
            continue
        results.append(
            CapabilityNegotiation(
                requirement=requirement,
                engine=available.engine,
                decision=CapabilityDecision.UNSUPPORTED,
                message=(
                    f"Requirement {requirement!r} unsupported by {available.engine}."
                ),
            )
        )
    return results
