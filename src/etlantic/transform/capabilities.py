"""Requirement extraction and capability matching for portable IR."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from etlantic.transform.compiler import (
    TransformCapabilities,
    TransformSupportFinding,
    TransformSupportReport,
)
from etlantic.transform.protocol import (
    DEFAULT_PROFILE,
    KERNEL_PROFILE_V1,
    KERNEL_PROFILE_V2,
)

# Profiles that are plan-shape / metadata aliases of the kernel claim.
_KERNEL_PROFILE_ALIASES = frozenset(
    {
        KERNEL_PROFILE_V1,
        KERNEL_PROFILE_V2,
        DEFAULT_PROFILE,
    }
)


def extract_requirements(
    *,
    actions: set[str],
    functions: set[str],
    profiles: set[str],
) -> dict[str, list[str]]:
    """Return sorted requirement lists for a portable definition."""
    profile_set = set(profiles) | {
        KERNEL_PROFILE_V1,
        KERNEL_PROFILE_V2,
        DEFAULT_PROFILE,
    }
    return {
        "profiles": sorted(profile_set),
        "actions": sorted(actions),
        "functions": sorted(functions),
    }


def requirements_from_plan(plan: dict[str, Any]) -> dict[str, list[str]]:
    """Best-effort extraction from an exported portable plan."""
    actions: set[str] = set()
    functions: set[str] = set()
    for item in plan.get("actions") or []:
        kind = item.get("kind") or {}
        action = kind.get("action")
        if isinstance(action, str):
            actions.add(action)
        _collect_call_callees(item, functions)
    for output in (plan.get("outputs") or {}).values():
        if isinstance(output, dict):
            _collect_call_callees(output, functions)
    profiles = {plan.get("profile")} if plan.get("profile") else set()
    return extract_requirements(
        actions=actions,
        functions=functions,
        profiles=profiles,  # type: ignore[arg-type]
    )


def _collect_call_callees(node: Any, functions: set[str]) -> None:
    if isinstance(node, dict):
        if node.get("kind") == "call" and isinstance(node.get("callee"), str):
            functions.add(str(node["callee"]))
        for value in node.values():
            _collect_call_callees(value, functions)
    elif isinstance(node, list):
        for item in node:
            _collect_call_callees(item, functions)


def match_requirements(
    requirements: Mapping[str, Sequence[str]] | None,
    capabilities: TransformCapabilities,
    *,
    allow_kernel_profile_alias: bool = True,
) -> TransformSupportReport:
    """Compare plan requirements against advertised compiler capabilities.

    When ``allow_kernel_profile_alias`` is true, requiring kernel ``/2`` (or
    the default plan-v2 profile) is satisfied by a compiler that claims
    ``portable-relational-kernel/1`` only — without granting extra relational
    ops.
    """
    req = requirements or {}
    findings: list[TransformSupportFinding] = []

    claimed_profiles = set(capabilities.profiles)
    if allow_kernel_profile_alias and KERNEL_PROFILE_V1 in claimed_profiles:
        claimed_profiles |= _KERNEL_PROFILE_ALIASES

    for profile in req.get("profiles") or ():
        if profile not in claimed_profiles:
            # Kernel-only compilers may see only kernel aliases as required.
            if (
                allow_kernel_profile_alias
                and profile in _KERNEL_PROFILE_ALIASES
                and KERNEL_PROFILE_V1 in capabilities.profiles
            ):
                continue
            findings.append(
                TransformSupportFinding(
                    code="PMXFORM301",
                    requirement=f"profile:{profile}",
                    reason="profile is not claimed by the compiler",
                    expression_path=None,
                )
            )

    for action in req.get("actions") or ():
        if capabilities.actions and action not in capabilities.actions:
            findings.append(
                TransformSupportFinding(
                    code="PMXFORM301",
                    requirement=f"action:{action}",
                    reason="action is not implemented",
                    expression_path=None,
                )
            )

    for function in req.get("functions") or ():
        if capabilities.functions and function not in capabilities.functions:
            findings.append(
                TransformSupportFinding(
                    code="PMXFORM301",
                    requirement=f"function:{function}",
                    reason="function is not implemented",
                    expression_path=None,
                )
            )

    return TransformSupportReport(
        supported=not findings,
        findings=tuple(findings),
    )
