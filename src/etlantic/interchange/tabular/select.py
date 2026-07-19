"""Pure capability-driven selection of tabular interchange mechanisms."""

from __future__ import annotations

from collections.abc import Set
from typing import Protocol

from etlantic.interchange.tabular.errors import InterchangeSelectionError
from etlantic.interchange.tabular.mechanisms import InterchangeMechanism


class SupportsCapability(Protocol):
    """Structural capability interface accepted by mechanism selection."""

    def supports(self, requirement: str) -> bool:
        """Return whether this object advertises a capability."""
        ...


CapabilitySource = Set[str] | SupportsCapability


def _supports(capabilities: CapabilitySource, mechanism: str) -> bool:
    if isinstance(capabilities, Set):
        return mechanism in capabilities
    extras = getattr(capabilities, "extras", ())
    if mechanism in extras:
        return True
    return bool(capabilities.supports(mechanism))


def _both(
    producer_caps: CapabilitySource,
    consumer_caps: CapabilitySource,
    mechanism: InterchangeMechanism | str,
) -> bool:
    name = mechanism.value if isinstance(mechanism, InterchangeMechanism) else mechanism
    return _supports(producer_caps, name) and _supports(consumer_caps, name)


def _fallback(
    producer_caps: CapabilitySource,
    consumer_caps: CapabilitySource,
    reason: str,
) -> tuple[InterchangeMechanism, str]:
    if _both(
        producer_caps,
        consumer_caps,
        InterchangeMechanism.NATIVE_FALLBACK,
    ):
        return InterchangeMechanism.NATIVE_FALLBACK, reason
    return InterchangeMechanism.RECORDS_FALLBACK, reason


def select_mechanism(
    producer_caps: CapabilitySource,
    consumer_caps: CapabilitySource,
    *,
    durable: bool,
    already_collecting: bool,
    pyarrow_available: bool,
    mapping_lossy: bool = False,
) -> tuple[InterchangeMechanism, str | None]:
    """Select the Gate A mechanism from declared capabilities.

    Lossy logical mappings fail before a fallback or physical mutation can
    occur. All fallback selections carry an explicit reason.
    """
    if mapping_lossy:
        raise InterchangeSelectionError(
            "Tabular interchange would lose required logical semantics."
        )

    if not pyarrow_available:
        return _fallback(
            producer_caps,
            consumer_caps,
            "pyarrow_unavailable",
        )

    if durable:
        parquet_supported = _both(
            producer_caps,
            consumer_caps,
            InterchangeMechanism.PARQUET_ARTIFACT,
        )
        if parquet_supported and _both(producer_caps, consumer_caps, "storage"):
            return InterchangeMechanism.PARQUET_ARTIFACT, None
        return _fallback(
            producer_caps,
            consumer_caps,
            "durable_artifact_capability_missing",
        )

    if not already_collecting and _both(
        producer_caps,
        consumer_caps,
        InterchangeMechanism.ARROW_C_STREAM,
    ):
        return InterchangeMechanism.ARROW_C_STREAM, None

    if already_collecting and _both(
        producer_caps,
        consumer_caps,
        InterchangeMechanism.ARROW_C_DATA,
    ):
        return InterchangeMechanism.ARROW_C_DATA, None

    if _both(
        producer_caps,
        consumer_caps,
        InterchangeMechanism.ARROW_IPC_STREAM,
    ):
        return InterchangeMechanism.ARROW_IPC_STREAM, None

    if _both(
        producer_caps,
        consumer_caps,
        InterchangeMechanism.ARROW_IPC_FILE,
    ):
        return InterchangeMechanism.ARROW_IPC_FILE, None

    return _fallback(
        producer_caps,
        consumer_caps,
        "no_compatible_arrow_mechanism",
    )
