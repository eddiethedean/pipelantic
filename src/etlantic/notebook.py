"""Optional notebook / IPython display helpers (0.9)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from etlantic.mermaid import graph_to_mermaid
from etlantic.model import LogicalGraph
from etlantic.plan.model import PipelinePlan
from etlantic.profile import Profile, resolve_profile
from etlantic.reports.model import PipelineRunReport
from etlantic.runtime.request import RunSelection
from etlantic.viz import graph_to_html, logical_graph_to_ir


def _text_graph(graph: LogicalGraph) -> str:
    lines = [f"Pipeline {graph.pipeline_name} ({graph.pipeline_id})"]
    for node in graph.nodes:
        lines.append(f"  - {node.kind.value}: {node.name}")
    for edge in graph.edges:
        lines.append(
            f"  {edge.producer_node}.{edge.producer_port} -> "
            f"{edge.consumer_node}.{edge.consumer_port}"
        )
    return "\n".join(lines)


class PipelineDisplay:
    """Plain-text / HTML representations for a Pipeline class or LogicalGraph."""

    def __init__(self, target: Any) -> None:
        if hasattr(target, "inspect"):
            self.graph = target.inspect()
            self.name = getattr(target, "__name__", self.graph.pipeline_name)
        elif isinstance(target, LogicalGraph):
            self.graph = target
            self.name = target.pipeline_name
        else:
            raise TypeError("Expected Pipeline subclass or LogicalGraph")

    def _repr_pretty_(self, p: Any, cycle: bool) -> None:
        p.text(self.__str__())

    def __str__(self) -> str:
        return _text_graph(self.graph)

    def _repr_html_(self) -> str:
        return graph_to_html(logical_graph_to_ir(self.graph))

    def mermaid(self) -> str:
        return graph_to_mermaid(self.graph)


class PlanDisplay:
    def __init__(self, plan: PipelinePlan) -> None:
        self.plan = plan

    def __str__(self) -> str:
        return (
            f"plan_id={self.plan.plan_id}\n"
            f"fingerprint={self.plan.fingerprint}\n"
            f"profile={self.plan.profile_name}\n"
            f"nodes={len(self.plan.logical_graph.nodes)}"
        )

    def _repr_html_(self) -> str:
        from html import escape

        return f"<pre>{escape(str(self))}</pre>" + graph_to_html(
            logical_graph_to_ir(self.plan.logical_graph)
        )


class ReportDisplay:
    def __init__(self, report: PipelineRunReport) -> None:
        self.report = report

    def __str__(self) -> str:
        return self.report.to_text()

    def _repr_html_(self) -> str:
        return self.report.to_html()


@dataclass
class NotebookSession:
    """Explicit notebook session helper (no hidden kernel globals)."""

    profile: Profile | str = "local"
    selection: RunSelection = field(default_factory=RunSelection.all)
    artifacts: dict[str, Any] = field(default_factory=dict)

    def resolved_profile(self) -> Profile:
        return resolve_profile(self.profile)

    def set_profile(self, profile: Profile | str) -> None:
        self.profile = profile

    def select(
        self, *, run_one: str | None = None, run_until: str | None = None
    ) -> None:
        if run_one and run_until:
            raise ValueError("Use only one of run_one or run_until")
        if run_one:
            self.selection = RunSelection.only(run_one)
        elif run_until:
            self.selection = RunSelection.until(run_until)
        else:
            self.selection = RunSelection.all()

    def remember(self, name: str, value: Any) -> None:
        self.artifacts[name] = value

    def display_pipeline(self, pipeline_cls: type[Any]) -> PipelineDisplay:
        disp = PipelineDisplay(pipeline_cls)
        self.remember("last_pipeline_display", disp)
        return disp

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile": self.resolved_profile().name,
            "selection": {
                "kind": self.selection.kind,
                "nodes": list(self.selection.nodes),
                "start": self.selection.start,
                "end": self.selection.end,
            },
            "artifact_keys": sorted(self.artifacts),
        }
