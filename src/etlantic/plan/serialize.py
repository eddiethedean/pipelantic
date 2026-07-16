"""Canonical serialization and fingerprinting for PipelinePlan."""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Any

from etlantic.plan.model import PipelinePlan


def canonical_plan_dict(plan: PipelinePlan) -> dict[str, Any]:
    """Return a deterministically ordered plan dict for hashing."""
    data = copy.deepcopy(plan.to_dict())
    # Derived / fill-in fields excluded from the content hash.
    data = {k: v for k, v in data.items() if k not in {"fingerprint", "plan_id"}}
    for item in data.get("output_resolutions") or []:
        artifact = item.get("artifact") or {}
        artifact.pop("cache_key", None)
    return _sort_structure(data)


def canonical_plan_json(plan: PipelinePlan) -> str:
    """Return canonical JSON bytes as a UTF-8 string."""
    return json.dumps(
        canonical_plan_dict(plan),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def plan_fingerprint(plan: PipelinePlan) -> str:
    """Compute a stable SHA-256 fingerprint of the canonical plan."""
    payload = canonical_plan_json(plan).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def plan_to_json(plan: PipelinePlan, *, indent: int | None = 2) -> str:
    """Serialize a plan including its fingerprint."""
    data = plan.to_dict()
    if indent is None:
        return json.dumps(data, sort_keys=True, separators=(",", ":"))
    return json.dumps(data, indent=indent, sort_keys=True) + "\n"


def plan_from_json(text: str, *, verify: bool = True) -> PipelinePlan:
    """Deserialize a plan from JSON text.

    When ``verify`` is True (default), recompute the fingerprint and reject
    tampered plans.
    """
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("PipelinePlan JSON must be an object")
    plan = PipelinePlan.from_dict(data)
    if verify:
        expected = plan_fingerprint(plan)
        if plan.fingerprint != expected:
            raise ValueError(
                f"PipelinePlan fingerprint mismatch: "
                f"embedded={plan.fingerprint!r} computed={expected!r}"
            )
    return plan


def _sort_structure(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _sort_structure(value[k]) for k in sorted(value)}
    if isinstance(value, list):
        return [_sort_structure(v) for v in value]
    return value
