"""Observed evidence for a tabular interchange boundary."""

from __future__ import annotations

from dataclasses import dataclass

from etlantic.interchange.tabular.descriptor import CopyEligibility
from etlantic.interchange.tabular.mechanisms import InterchangeMechanism


@dataclass(frozen=True, slots=True)
class InterchangeEvidence:
    """Runtime observations used to substantiate interchange claims."""

    evidence_id: str
    mechanism: InterchangeMechanism
    copy_observed: bool | None
    zero_copy_reported: bool
    fallback_reason: str | None
    cleanup_status: str
    notes: str

    def can_report_zero_copy(self, eligibility: CopyEligibility) -> bool:
        """Return whether planned eligibility and observations prove zero copy."""
        return eligibility is CopyEligibility.ELIGIBLE and self.copy_observed is False
