"""Map SparkForge IR onto ETLantic Pipeline / Profile (no medallion in core)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from etlantic import (
    Data,
    Input,
    Output,
    Pipeline,
    Sink,
    Source,
    Transformation,
)
from etlantic.diagnostics import Diagnostic, Severity, ValidationReport
from etlantic.pipeline import _PipelineNamespace
from etlantic.policy import PolicyMode, ValidationPolicy
from etlantic.profile import Profile
from etlantic.reliability import WriteIntent
from etlantic_sparkforge.compat import (
    assert_delta_capabilities,
    write_mode_from_sparkforge,
)
from etlantic_sparkforge.ir import (
    SparkForgePipelineSpec,
    StepKind,
)


class AdapterError(Exception):
    """Raised when SparkForge → ETLantic adaptation fails closed."""

    def __init__(
        self,
        message: str,
        *,
        report: ValidationReport | None = None,
        code: str = "PMSF300",
    ) -> None:
        super().__init__(message)
        self.report = report or ValidationReport()
        self.code = code


class AdaptedRow(Data):
    """Generic row contract for adapted SparkForge fixtures (planning/parity)."""

    id: int
    payload: str = ""


@dataclass(frozen=True, slots=True)
class AdaptationResult:
    """Result of adapting a SparkForge pipeline IR."""

    pipeline_cls: type[Pipeline]
    profile: Profile
    validation_policy: ValidationPolicy
    write_intents: tuple[WriteIntent, ...] = ()
    step_map: dict[str, str] = field(default_factory=dict)
    layer_by_node: dict[str, str] = field(default_factory=dict)
    diagnostics: tuple[Diagnostic, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "pipeline": self.pipeline_cls.__name__,
            "profile": self.profile.to_dict(),
            "validation_policy": self.validation_policy.to_dict(),
            "write_intents": [w.to_dict() for w in self.write_intents],
            "step_map": dict(self.step_map),
            "layer_by_node": dict(self.layer_by_node),
            "diagnostics": [
                {
                    "code": d.code,
                    "severity": d.severity.value,
                    "message": d.message,
                }
                for d in self.diagnostics
            ],
            "metadata": dict(self.metadata),
        }


def adapt_profile(
    spec: SparkForgePipelineSpec,
    *,
    name: str | None = None,
) -> Profile:
    """Build an ETLantic Profile from SparkForge builder config."""
    engine = (spec.engine or "spark").lower()
    spark_engine = "pyspark" if engine in {"spark", "pyspark", "delta"} else None
    sql_engine = "sql" if engine in {"sql", "postgres", "postgresql"} else None
    return Profile(
        name=name or f"sparkforge-{spec.schema}",
        orchestrator="local",
        dataframe_engine=None if spark_engine or sql_engine else "local",
        spark_engine=spark_engine,
        sql_engine=sql_engine,
        validation_policy=f"sparkforge-{spec.schema}",
        resources={"schema": spec.schema},
        metadata={
            "adapter": "etlantic-sparkforge",
            "source_schema": spec.schema,
            "min_accept_rates": {
                "ingest": spec.min_bronze_rate,
                "clean": spec.min_silver_rate,
                "publish": spec.min_gold_rate,
            },
            "sparkforge_layer_rates": {
                "bronze": spec.min_bronze_rate,
                "silver": spec.min_silver_rate,
                "gold": spec.min_gold_rate,
            },
        },
    )


def adapt_validation_policy(spec: SparkForgePipelineSpec) -> ValidationPolicy:
    """Map layer thresholds onto a named ValidationPolicy (metadata only)."""
    return ValidationPolicy(
        name=f"sparkforge-{spec.schema}",
        mode=PolicyMode.DEFAULT,
        metadata={
            "min_accept_rate_ingest": spec.min_bronze_rate,
            "min_accept_rate_clean": spec.min_silver_rate,
            "min_accept_rate_publish": spec.min_gold_rate,
        },
    )


def adapt_pipeline(spec: SparkForgePipelineSpec) -> AdaptationResult:
    """Map a SparkForge pipeline IR to a concrete ETLantic Pipeline subclass.

    Bronze/silver/gold remain adapter metadata on AdaptationResult.layer_by_node;
    ETLantic core never sees medallion enums.
    """
    diagnostics: list[Diagnostic] = []
    _validate_spec(spec, diagnostics)

    if any(d.severity is Severity.ERROR for d in diagnostics):
        raise AdapterError(
            "Refusing to adapt invalid SparkForge pipeline IR.",
            report=ValidationReport.from_diagnostics(diagnostics),
            code="PMSF301",
        )

    for ext in spec.legacy_engine_extensions:
        diagnostics.append(
            Diagnostic(
                code="PMSF410",
                severity=Severity.WARNING,
                message=(
                    f"Legacy SparkForge engine extension {ext!r} is deprecated; "
                    "prefer ETLantic plugins (etlantic-pyspark / etlantic-sql)."
                ),
                path=("legacy_engine_extensions", ext),
                phase="sparkforge_adapter",
            )
        )

    delta_ops = list(spec.metadata.get("delta_operations") or ())
    if delta_ops:
        diagnostics.extend(assert_delta_capabilities(delta_ops))
        if any(d.severity is Severity.ERROR for d in diagnostics):
            raise AdapterError(
                "Delta capability requirements not met.",
                report=ValidationReport.from_diagnostics(diagnostics),
                code="PMSF320",
            )

    ns = _PipelineNamespace()
    annotations: dict[str, Any] = {}
    ns["__annotations__"] = annotations
    step_map: dict[str, str] = {}
    layer_by_node: dict[str, str] = {}
    write_intents: list[WriteIntent] = []
    previous: Source | Any = None

    for step in spec.steps:
        if step.kind is StepKind.BRONZE_RULES:
            binding = step.table_name or step.name
            source = Source[AdaptedRow](binding=binding)
            ns[step.name] = source
            annotations[step.name] = Source[AdaptedRow]
            step_map[step.name] = f"source:{step.name}"
            layer_by_node[step.name] = step.layer.value
            previous = source
            continue

        if step.kind in {StepKind.SILVER_TRANSFORM, StepKind.GOLD_TRANSFORM}:
            if previous is None:
                diagnostics.append(
                    Diagnostic(
                        code="PMSF302",
                        severity=Severity.ERROR,
                        message=(
                            f"Transform step {step.name!r} has no upstream source."
                        ),
                        path=("steps", step.name),
                        phase="sparkforge_adapter",
                    )
                )
                continue

            transform_cls = _make_passthrough_transformation(
                step.name, transform_ref=step.transform_ref
            )
            if isinstance(previous, Source):
                step_inst = transform_cls.step(rows=previous)
            else:
                step_inst = transform_cls.step(rows=previous.result)
            ns[step.name] = step_inst
            step_map[step.name] = f"step:{step.name}"
            layer_by_node[step.name] = step.layer.value
            previous = step_inst

            sink_name = f"{step.name}_out"
            binding = step.table_name or sink_name
            mode = write_mode_from_sparkforge(step.write_mode)
            write_intents.append(
                WriteIntent(
                    subject_id=binding,
                    mode=mode,
                    metadata={"step": step.name, "layer": step.layer.value},
                )
            )
            sink = Sink[AdaptedRow](input=step_inst.result, binding=binding)
            ns[sink_name] = sink
            annotations[sink_name] = Sink[AdaptedRow]
            step_map[sink_name] = f"sink:{sink_name}"
            layer_by_node[sink_name] = step.layer.value
            continue

        diagnostics.append(
            Diagnostic(
                code="PMSF303",
                severity=Severity.ERROR,
                message=f"Unknown SparkForge step kind for {step.name!r}.",
                path=("steps", step.name),
                phase="sparkforge_adapter",
            )
        )

    if any(d.severity is Severity.ERROR for d in diagnostics):
        raise AdapterError(
            "SparkForge adaptation failed.",
            report=ValidationReport.from_diagnostics(diagnostics),
            code="PMSF301",
        )

    class_name = _safe_ident(spec.name) + "Pipeline"
    pipeline_cls = type(class_name, (Pipeline,), ns)
    return AdaptationResult(
        pipeline_cls=pipeline_cls,
        profile=adapt_profile(spec),
        validation_policy=adapt_validation_policy(spec),
        write_intents=tuple(write_intents),
        step_map=step_map,
        layer_by_node=layer_by_node,
        diagnostics=tuple(diagnostics),
        metadata={
            "adapter_version": "0.10.0",
            "source_name": spec.name,
            "schema": spec.schema,
        },
    )


def _validate_spec(spec: SparkForgePipelineSpec, diagnostics: list[Diagnostic]) -> None:
    if not spec.steps:
        diagnostics.append(
            Diagnostic(
                code="PMSF304",
                severity=Severity.ERROR,
                message="SparkForge pipeline IR has no steps.",
                path=("steps",),
                phase="sparkforge_adapter",
            )
        )
    names = [s.name for s in spec.steps]
    if len(names) != len(set(names)):
        diagnostics.append(
            Diagnostic(
                code="PMSF305",
                severity=Severity.ERROR,
                message="Duplicate SparkForge step names are not allowed.",
                path=("steps",),
                phase="sparkforge_adapter",
            )
        )
    edges: dict[str, str | None] = {s.name: s.source for s in spec.steps}
    for name in names:
        seen: set[str] = set()
        cur: str | None = name
        while cur is not None:
            if cur in seen:
                diagnostics.append(
                    Diagnostic(
                        code="PMSF306",
                        severity=Severity.ERROR,
                        message=f"Cycle detected involving step {name!r}.",
                        path=("steps", name),
                        phase="sparkforge_adapter",
                    )
                )
                break
            seen.add(cur)
            cur = edges.get(cur)


def _make_passthrough_transformation(
    name: str,
    *,
    transform_ref: str | None,
) -> type[Transformation]:
    safe = _safe_ident(name)
    ns: dict[str, Any] = {
        "__annotations__": {
            "rows": Input[AdaptedRow],
            "result": Output[AdaptedRow],
        },
        "__doc__": (
            f"Adapted SparkForge transform {name} ({transform_ref or 'passthrough'})."
        ),
    }
    transform_cls = type(safe, (Transformation,), ns)

    @transform_cls.implementation("local")
    def _passthrough(rows: list[Any]) -> list[Any]:
        return list(rows)

    @transform_cls.implementation("pyspark")
    def _passthrough_spark(rows: Any) -> Any:
        return rows

    return transform_cls


def _safe_ident(name: str) -> str:
    cleaned = "".join(ch if ch.isalnum() else "_" for ch in name)
    if not cleaned or cleaned[0].isdigit():
        cleaned = f"S_{cleaned}"
    return cleaned
