"""Graph slicing for run-one / run-until planning selections."""

from __future__ import annotations

from pipelantic.model import LogicalGraph


def dependency_closure(
    graph: LogicalGraph,
    targets: set[str] | frozenset[str] | list[str],
) -> tuple[str, ...]:
    """Return declaration-ordered upstream closure for ``targets`` (inclusive)."""
    wanted = set(targets)
    if not wanted:
        return ()
    known = {n.name for n in graph.nodes}
    missing = wanted - known
    if missing:
        raise ValueError(f"Unknown step(s): {', '.join(sorted(missing))}")

    producers: dict[str, set[str]] = {n.name: set() for n in graph.nodes}
    for edge in graph.edges:
        producers.setdefault(edge.consumer_node, set()).add(edge.producer_node)

    seen: set[str] = set()
    stack = list(wanted)
    while stack:
        node = stack.pop()
        if node in seen:
            continue
        seen.add(node)
        for upstream in producers.get(node, ()):
            if upstream not in seen:
                stack.append(upstream)

    return tuple(n.name for n in graph.nodes if n.name in seen)


def validate_selection_target(graph: LogicalGraph, step_name: str) -> None:
    """Raise ValueError when ``step_name`` is not a node in ``graph``."""
    if not any(n.name == step_name for n in graph.nodes):
        raise ValueError(f"Unknown step {step_name!r}")


def run_one_selection(graph: LogicalGraph, step_name: str) -> tuple[str, ...]:
    """Select a single step and its required upstream closure."""
    validate_selection_target(graph, step_name)
    return dependency_closure(graph, {step_name})


def run_until_selection(graph: LogicalGraph, step_name: str) -> tuple[str, ...]:
    """Select declaration-order prefix through ``step_name`` (inclusive).

    Includes parallel siblings declared earlier than the target, not only the
    upstream dependency closure.
    """
    validate_selection_target(graph, step_name)
    selected: list[str] = []
    for node in graph.nodes:
        selected.append(node.name)
        if node.name == step_name:
            return tuple(selected)
    raise ValueError(f"Unknown step {step_name!r}")


def slice_graph(graph: LogicalGraph, selected: tuple[str, ...]) -> LogicalGraph:
    """Return a LogicalGraph containing only ``selected`` nodes and internal edges."""
    selected_set = set(selected)
    nodes = tuple(n for n in graph.nodes if n.name in selected_set)
    edges = tuple(
        e
        for e in graph.edges
        if e.producer_node in selected_set and e.consumer_node in selected_set
    )
    return LogicalGraph(
        pipeline_id=graph.pipeline_id,
        pipeline_name=graph.pipeline_name,
        nodes=nodes,
        edges=edges,
        metadata={**dict(graph.metadata), "sliced": True, "selected": list(selected)},
    )
