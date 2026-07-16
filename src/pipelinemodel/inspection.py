"""Pipeline inspection helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pipelinemodel.model import LogicalGraph

if TYPE_CHECKING:
    from pipelinemodel.pipeline import Pipeline


def inspect_pipeline(pipeline_cls: type[Pipeline]) -> LogicalGraph:
    """Return the immutable logical graph for a pipeline class.

    Repeated calls return an equivalent graph (cached on the class).
    """
    return pipeline_cls.build_graph()
