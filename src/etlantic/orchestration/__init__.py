"""External orchestration protocols (``etlantic.orchestration/1``).

Compile secret-free :class:`~etlantic.plan.model.PipelinePlan` objects into
orchestrator artifacts via :func:`~etlantic.orchestration.compile.compile_plan`.
Install ``etlantic-airflow`` for the reference Airflow compiler.
"""

from __future__ import annotations

from etlantic.orchestration.artifacts import (
    DEFAULT_MAX_INLINE_BYTES,
    ArtifactTransportPolicy,
    validate_artifact_for_transport,
    xcom_safe_payload,
)
from etlantic.orchestration.compile import (
    OrchestrationCompilationError,
    compile_plan,
    explain_compilation,
)
from etlantic.orchestration.discovery import (
    ORCHESTRATOR_PLUGIN_ENTRY_POINT,
    discover_orchestrator_plugins,
    load_orchestrator_plugin,
    plugin_registry_snapshot,
    register_discovered_plugins,
)
from etlantic.orchestration.lifecycle import (
    CancellationResult,
    CorrelationKeys,
    PollResult,
    SubmissionResult,
    SubmissionStatus,
    comparable_report_shape,
    correlate_poll_to_report,
)
from etlantic.orchestration.mapping import (
    context_from_profile,
    dag_id_for_plan,
    execution_from_profile,
    map_plan_to_tasks,
    schedule_from_profile,
)
from etlantic.orchestration.protocol import (
    ORCHESTRATION_PROTOCOL_VERSION,
    ORCHESTRATOR_ENGINES,
    CompilationContext,
    CompilationDiagnostic,
    CompiledOrchestrationArtifact,
    CompiledTask,
    ExecutionIntent,
    OrchestrationPhase,
    OrchestratorPlugin,
    OrchestratorPluginInfo,
    ScheduleIntent,
    TaskRetryPolicy,
)
from etlantic.orchestration.reliability import (
    apply_reliability_to_task,
    reliability_metadata,
    resolve_task_retry,
)

__all__ = [
    "DEFAULT_MAX_INLINE_BYTES",
    "ORCHESTRATION_PROTOCOL_VERSION",
    "ORCHESTRATOR_ENGINES",
    "ORCHESTRATOR_PLUGIN_ENTRY_POINT",
    "ArtifactTransportPolicy",
    "CancellationResult",
    "CompilationContext",
    "CompilationDiagnostic",
    "CompiledOrchestrationArtifact",
    "CompiledTask",
    "CorrelationKeys",
    "ExecutionIntent",
    "OrchestrationCompilationError",
    "OrchestrationPhase",
    "OrchestratorPlugin",
    "OrchestratorPluginInfo",
    "PollResult",
    "ScheduleIntent",
    "SubmissionResult",
    "SubmissionStatus",
    "TaskRetryPolicy",
    "apply_reliability_to_task",
    "comparable_report_shape",
    "compile_plan",
    "context_from_profile",
    "correlate_poll_to_report",
    "dag_id_for_plan",
    "discover_orchestrator_plugins",
    "execution_from_profile",
    "explain_compilation",
    "load_orchestrator_plugin",
    "map_plan_to_tasks",
    "plugin_registry_snapshot",
    "register_discovered_plugins",
    "reliability_metadata",
    "resolve_task_retry",
    "schedule_from_profile",
    "validate_artifact_for_transport",
    "xcom_safe_payload",
]
