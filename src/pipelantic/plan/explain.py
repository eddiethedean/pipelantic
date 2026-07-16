"""Structured plan explain output."""

from __future__ import annotations

from typing import Any

from pipelantic.plan.model import PipelinePlan


def explain_plan(plan: PipelinePlan) -> dict[str, Any]:
    """Return a structured, tooling-friendly explanation of a plan."""
    region_by_node: dict[str, str] = {}
    for region in plan.regions:
        for name in region.node_names:
            region_by_node[name] = region.identity

    steps = []
    for node in plan.logical_graph.nodes:
        if plan.selected_nodes is not None and node.name not in plan.selected_nodes:
            continue
        steps.append(
            {
                "node": node.name,
                "kind": node.kind.value,
                "region": region_by_node.get(node.name),
                "physical_unit": plan.logical_to_physical.get(node.name),
                "implementation": (
                    plan.implementations[node.name].to_dict()
                    if node.name in plan.implementations
                    else None
                ),
                "binding": node.binding,
            }
        )

    return {
        "plan_id": plan.plan_id,
        "pipeline_id": plan.pipeline_id,
        "profile": plan.profile_name,
        "fingerprint": plan.fingerprint,
        "security_domain": plan.security_domain,
        "regions": [r.to_dict() for r in plan.regions],
        "materialization_boundaries": [
            b.to_dict() for b in plan.materialization_boundaries
        ],
        "output_resolutions": [o.to_dict() for o in plan.output_resolutions],
        "capability_decisions": list(plan.capability_decisions),
        "steps": steps,
        "selected_nodes": (
            list(plan.selected_nodes) if plan.selected_nodes is not None else None
        ),
    }
