"""PipelinePlan IR package."""

from pipelantic.plan.artifacts import ArtifactRef, ArtifactStrategy
from pipelantic.plan.explain import explain_plan
from pipelantic.plan.model import PLAN_SCHEMA, PipelinePlan
from pipelantic.plan.planner import plan_pipeline, plan_pipeline_with_report
from pipelantic.plan.serialize import (
    canonical_plan_json,
    plan_fingerprint,
    plan_from_json,
    plan_to_json,
)
from pipelantic.plan.slicing import (
    dependency_closure,
    run_one_selection,
    run_until_selection,
)

__all__ = [
    "PLAN_SCHEMA",
    "ArtifactRef",
    "ArtifactStrategy",
    "PipelinePlan",
    "canonical_plan_json",
    "dependency_closure",
    "explain_plan",
    "plan_fingerprint",
    "plan_from_json",
    "plan_pipeline",
    "plan_pipeline_with_report",
    "plan_to_json",
    "run_one_selection",
    "run_until_selection",
]
