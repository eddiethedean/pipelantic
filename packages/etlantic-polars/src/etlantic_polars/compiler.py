"""Polars portable transform compiler (kernel claim only)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from etlantic.transform.capabilities import match_requirements
from etlantic.transform.compiler import (
    COMPILER_PROTOCOL,
    CompiledTransform,
    TransformCapabilities,
    TransformCompileContext,
    TransformCompilerInfo,
    TransformExecutionContext,
    TransformOutputBundle,
    TransformPlanningContext,
    TransformSupportReport,
)
from etlantic.transform.protocol import KERNEL_PROFILE_V1
from etlantic_polars.lowering.actions import KERNEL_ACTIONS, apply_action

__version__ = "0.12.0"

# Kernel scalar / string / numeric functions claimed in 0.12.
KERNEL_FUNCTIONS = frozenset(
    {
        "dtcs:lower",
        "dtcs:upper",
        "dtcs:concat",
        "dtcs:concat_ws",
        "dtcs:substr",
        "dtcs:replace",
        "dtcs:length",
        "dtcs:contains",
        "dtcs:starts_with",
        "dtcs:ends_with",
        "dtcs:case_when",
        "dtcs:coalesce",
        "dtcs:if_null",
        "dtcs:null_if",
        "dtcs:is_null",
        "dtcs:abs",
        "dtcs:round",
        "dtcs:floor",
        "dtcs:ceil",
        "dtcs:power",
        "dtcs:sqrt",
        "dtcs:least",
        "dtcs:greatest",
        "dtcs:cast",
    }
)


def create_transform_compiler() -> PolarsTransformCompiler:
    """Entry-point factory for ``etlantic.transform_compilers``."""
    return PolarsTransformCompiler()


class PolarsTransformCompiler:
    """Compile ``dtcs.transform-plan/2`` kernel IR to Polars expressions."""

    def __init__(self) -> None:
        caps = TransformCapabilities(
            profiles=frozenset({KERNEL_PROFILE_V1}),
            actions=KERNEL_ACTIONS,
            functions=KERNEL_FUNCTIONS,
            lazy=True,
            eager=True,
        )
        self._info = TransformCompilerInfo(
            name="etlantic-polars",
            version=__version__,
            engine="polars",
            compiler_protocol=COMPILER_PROTOCOL,
            capabilities=caps,
        )

    @property
    def info(self) -> TransformCompilerInfo:
        return self._info

    def analyze(
        self,
        definition: Mapping[str, Any],
        *,
        context: TransformPlanningContext,
        requirements: Mapping[str, Sequence[str]] | None = None,
    ) -> TransformSupportReport:
        req = dict(requirements or {})
        if not req:
            from etlantic.transform.capabilities import requirements_from_plan

            req = requirements_from_plan(dict(definition))
        return match_requirements(req, self._info.capabilities)

    def compile(
        self,
        definition: Mapping[str, Any],
        *,
        context: TransformCompileContext,
        requirements: Mapping[str, Sequence[str]] | None = None,
    ) -> CompiledTransform:
        report = self.analyze(
            definition,
            context=TransformPlanningContext(
                pipeline_id=context.pipeline_id,
                step_name=context.step_name,
                profile_name=context.profile_name,
                engine=context.engine,
            ),
            requirements=requirements,
        )
        if not report.supported:
            findings = "; ".join(
                f"{f.requirement}: {f.reason}" for f in report.findings
            )
            raise ValueError(f"Cannot compile unsupported plan: {findings}")
        import hashlib
        import json

        from etlantic.transform.protocol import PLAN_PROTOCOL

        canonical = json.dumps(definition, sort_keys=True, separators=(",", ":"))
        fingerprint = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        outputs = tuple((definition.get("outputs") or {}).keys()) or ("result",)
        params = tuple((definition.get("parameters") or {}).keys())
        return CompiledTransform(
            compiler_name=self._info.name,
            compiler_version=self._info.version,
            engine="polars",
            ir_fingerprint=fingerprint,
            output_ports=outputs,
            parameter_names=params,
            explain={
                "planIdentity": definition.get("planIdentity") or PLAN_PROTOCOL,
                "profile": definition.get("profile"),
                "actions": [
                    (a.get("kind") or {}).get("action")
                    for a in (definition.get("actions") or [])
                ],
            },
            native_plan=dict(definition),
        )

    async def execute(
        self,
        compiled: CompiledTransform,
        *,
        inputs: Mapping[str, Any],
        parameters: Mapping[str, Any],
        context: TransformExecutionContext,
    ) -> TransformOutputBundle:
        plan = compiled.native_plan
        if not isinstance(plan, dict):
            raise ValueError("Compiled transform missing native plan")
        frames: dict[str, Any] = {}
        for name, value in inputs.items():
            frames[name] = value
        # Also key by declared input ids when they differ from port names.
        for input_id in plan.get("inputs") or {}:
            if input_id not in frames and len(inputs) == 1:
                frames[input_id] = next(iter(inputs.values()))

        for action in plan.get("actions") or []:
            kind = action.get("kind") or {}
            action_id = str(kind.get("id") or action.get("id"))
            target = kind.get("target")
            if target not in frames:
                raise KeyError(f"Missing action target frame {target!r}")
            frames[action_id] = apply_action(
                frames[target],
                action,
                parameters=dict(parameters),
            )

        # Resolve outputs via lineage dependencies ending at output id.
        valid: dict[str, Any] = {}
        lineage = (plan.get("requirements") or {}).get("dependencies") or []
        for out_name in compiled.output_ports:
            source = None
            for dep in lineage:
                if dep.get("to") == out_name:
                    source = dep.get("from")
                    break
            if source is None:
                # Fallback: last action result.
                actions = plan.get("actions") or []
                if actions:
                    last = actions[-1].get("kind") or {}
                    source = last.get("id") or actions[-1].get("id")
            if source is None or source not in frames:
                raise KeyError(f"Cannot resolve output {out_name!r}")
            valid[out_name] = frames[source]

        return TransformOutputBundle(valid=valid, metrics={"engine": "polars"})
