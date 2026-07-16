"""PipelinePlan IR package."""

from etlantic.plan.artifacts import ArtifactRef, ArtifactStrategy
from etlantic.plan.explain import explain_plan
from etlantic.plan.model import PLAN_SCHEMA, PipelinePlan
from etlantic.plan.planner import plan_pipeline, plan_pipeline_with_report
from etlantic.plan.serialize import (
    canonical_plan_json,
    plan_fingerprint,
    plan_from_json,
    plan_to_json,
)
from etlantic.plan.slicing import (
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
