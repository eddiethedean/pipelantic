"""Evidence gating tests for zero-copy reporting."""

from __future__ import annotations

import pytest

from etlantic.interchange.tabular import (
    CopyEligibility,
    InterchangeEvidence,
    InterchangeMechanism,
)


@pytest.mark.parametrize(
    ("eligibility", "copy_observed", "expected"),
    [
        (CopyEligibility.ELIGIBLE, False, True),
        (CopyEligibility.ELIGIBLE, True, False),
        (CopyEligibility.ELIGIBLE, None, False),
        (CopyEligibility.COPY_REQUIRED, False, False),
        (CopyEligibility.UNKNOWN, False, False),
    ],
)
def test_zero_copy_requires_plan_and_observation(
    eligibility: CopyEligibility,
    copy_observed: bool | None,
    expected: bool,
) -> None:
    evidence = InterchangeEvidence(
        evidence_id="boundary-1",
        mechanism=InterchangeMechanism.ARROW_C_STREAM,
        copy_observed=copy_observed,
        zero_copy_reported=False,
        fallback_reason=None,
        cleanup_status="complete",
        notes="",
    )
    assert evidence.can_report_zero_copy(eligibility) is expected
