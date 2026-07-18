"""Portable planning policy tests with an in-process stub compiler."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import pytest

from etlantic import (
    Data,
    Input,
    Output,
    Parameter,
    Pipeline,
    Sink,
    Source,
    Transformation,
)
from etlantic.exceptions import PipelineValidationError
from etlantic.plan.explain import explain_plan
from etlantic.plan.planner import plan_pipeline
from etlantic.profile import Profile
from etlantic.registry import PlanningContext, builtin_stub_registry
from etlantic.transform import functions as F
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


class RawCustomer(Data):
    customer_id: int
    email: str
    age: int


class Customer(Data):
    customer_id: int
    email: str
    age: int


class NormalizeCustomers(Transformation):
    customers: Input[RawCustomer]
    minimum_age: Parameter[int] = 18
    result: Output[Customer]


@NormalizeCustomers.portable
def _normalize(customers, minimum_age):
    return (
        customers.filter(F.col("age") >= minimum_age)
        .withColumn("email", F.lower(F.col("email")))
        .select("customer_id", "email", "age")
    )


@NormalizeCustomers.implementation("polars")
def _normalize_native(customers):
    return customers


class KernelPipeline(Pipeline):
    raw: Source[RawCustomer] = Source(binding="customers")
    normalized = NormalizeCustomers.step(customers=raw)
    curated: Sink[Customer] = Sink(input=normalized.result, binding="out")


class StubKernelCompiler:
    """In-process compiler claiming only kernel actions/functions."""

    def __init__(self, *, support_all: bool = True) -> None:
        self.support_all = support_all
        caps = TransformCapabilities(
            profiles=frozenset({KERNEL_PROFILE_V1}),
            actions=frozenset(
                {
                    "dtcs:filter",
                    "dtcs:project",
                    "dtcs:with_fields",
                    "dtcs:drop_fields",
                    "dtcs:rename_fields",
                }
            ),
            functions=frozenset({"dtcs:lower"}),
        )
        self._info = TransformCompilerInfo(
            name="stub-polars",
            version="0.0.0",
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
        if not self.support_all:
            from etlantic.transform.compiler import TransformSupportFinding

            return TransformSupportReport(
                supported=False,
                findings=(
                    TransformSupportFinding(
                        code="PMXFORM301",
                        requirement="action:dtcs:filter",
                        reason="stub refuses all plans",
                    ),
                ),
            )
        return match_requirements(requirements, self._info.capabilities)

    def compile(
        self,
        definition: Mapping[str, Any],
        *,
        context: TransformCompileContext,
        requirements: Mapping[str, Sequence[str]] | None = None,
    ) -> CompiledTransform:
        return CompiledTransform(
            compiler_name=self._info.name,
            compiler_version=self._info.version,
            engine="polars",
            ir_fingerprint="0" * 64,
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
        return TransformOutputBundle(valid={"result": next(iter(inputs.values()))})


@pytest.fixture
def stub_compiler(monkeypatch: pytest.MonkeyPatch) -> StubKernelCompiler:
    stub = StubKernelCompiler()

    def _discover() -> dict[str, Any]:
        return {"polars": stub}

    monkeypatch.setattr(
        "etlantic.transform.discovery.discover_transform_compilers",
        _discover,
    )
    monkeypatch.setattr(
        "etlantic.transform.discovery.load_transform_compiler",
        lambda engine: stub if engine == "polars" else None,
    )
    return stub


def _polars_context() -> PlanningContext:
    profile = Profile(
        name="polars-test",
        dataframe_engine="polars",
        portable_transform_policy="prefer",
    )
    registry = builtin_stub_registry()
    from etlantic.capabilities import PluginCapabilities
    from etlantic.registry import PluginDescriptor

    registry.register_plugin(
        PluginDescriptor(
            name="etlantic-polars",
            kind="dataframe",
            version="0.0.0",
            engine="polars",
            capabilities=PluginCapabilities(
                engine="polars",
                dataframe=True,
                eager=True,
                lazy=True,
            ),
        )
    )
    return PlanningContext(profile=profile, registry=registry)


def test_prefer_selects_portable_compiled(stub_compiler: StubKernelCompiler) -> None:
    plan = plan_pipeline(KernelPipeline, context=_polars_context())
    impl = plan.implementations["normalized"]
    assert impl.kind == "portable_compiled"
    assert impl.ir_fingerprint
    assert impl.portable_plan is not None
    assert impl.compiler_name == "stub-polars"
    explained = explain_plan(plan)
    step = next(s for s in explained["steps"] if s["node"] == "normalized")
    assert step["implementation_kind"] == "portable_compiled"
    assert step["ir_fingerprint"] == impl.ir_fingerprint
    assert step["compiler"]["name"] == "stub-polars"


def test_native_policy_ignores_portable(stub_compiler: StubKernelCompiler) -> None:
    ctx = _polars_context()
    ctx = PlanningContext(
        profile=ctx.profile.with_updates(portable_transform_policy="native"),
        registry=ctx.registry,
    )
    plan = plan_pipeline(KernelPipeline, context=ctx)
    impl = plan.implementations["normalized"]
    assert impl.kind == "native"
    assert impl.portable_plan is None


def test_require_fails_when_unsupported(monkeypatch: pytest.MonkeyPatch) -> None:
    stub = StubKernelCompiler(support_all=False)

    def _discover() -> dict[str, Any]:
        return {"polars": stub}

    monkeypatch.setattr(
        "etlantic.transform.discovery.discover_transform_compilers",
        _discover,
    )
    monkeypatch.setattr(
        "etlantic.transform.discovery.load_transform_compiler",
        lambda engine: stub if engine == "polars" else None,
    )

    ctx = _polars_context()
    ctx = PlanningContext(
        profile=ctx.profile.with_updates(portable_transform_policy="require"),
        registry=ctx.registry,
    )
    with pytest.raises(PipelineValidationError) as exc:
        plan_pipeline(KernelPipeline, context=ctx)
    assert "stub refuses" in str(exc.value)
    assert "PMXFORM301" in {
        d.code for d in (exc.value.report.diagnostics if exc.value.report else ())
    }


def test_prefer_falls_back_when_unsupported(monkeypatch: pytest.MonkeyPatch) -> None:
    stub = StubKernelCompiler(support_all=False)

    def _discover() -> dict[str, Any]:
        return {"polars": stub}

    monkeypatch.setattr(
        "etlantic.transform.discovery.discover_transform_compilers",
        _discover,
    )
    monkeypatch.setattr(
        "etlantic.transform.discovery.load_transform_compiler",
        lambda engine: stub if engine == "polars" else None,
    )
    plan = plan_pipeline(KernelPipeline, context=_polars_context())
    impl = plan.implementations["normalized"]
    assert impl.kind == "native"
    assert impl.fallback_reason is not None
    assert "portable unsupported" in impl.fallback_reason
