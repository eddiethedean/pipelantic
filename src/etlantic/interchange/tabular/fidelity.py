"""Pure logical-to-physical mapping fidelity checks."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum


class FidelityStatus(StrEnum):
    """Outcome of evaluating physical mapping issues."""

    ACCEPT = "accept"
    FAIL = "fail"


@dataclass(frozen=True, slots=True)
class MappingIssue:
    """A type-family mapping concern discovered before interchange."""

    type_family: str
    reason: str
    lossy: bool = True


@dataclass(frozen=True, slots=True)
class FidelityResult:
    """Aggregate result of mapping fidelity evaluation."""

    status: FidelityStatus
    reasons: tuple[str, ...] = ()

    @property
    def accepted(self) -> bool:
        """Return whether the mapping preserves required semantics."""
        return self.status is FidelityStatus.ACCEPT


def evaluate_fidelity(issues: Iterable[MappingIssue]) -> FidelityResult:
    """Return fail with reasons when any mapping issue is lossy."""
    reasons = tuple(
        f"{issue.type_family}: {issue.reason}" for issue in issues if issue.lossy
    )
    status = FidelityStatus.FAIL if reasons else FidelityStatus.ACCEPT
    return FidelityResult(status=status, reasons=reasons)


def check_mapping_fidelity(issues: Iterable[MappingIssue]) -> FidelityResult:
    """Evaluate mapping issues without side effects."""
    return evaluate_fidelity(issues)
