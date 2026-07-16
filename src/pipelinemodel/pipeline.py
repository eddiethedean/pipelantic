"""Pipeline authoring: Source, Sink, Pipeline, and subpipelines."""

from __future__ import annotations

import inspect
import itertools
from dataclasses import dataclass, field
from typing import Any, ClassVar, TypeVar

from pipelinemodel.contracts import is_data_contract_type
from pipelinemodel.identity import contract_id, node_id, pipeline_id
from pipelinemodel.model import (
    Edge,
    LogicalGraph,
    Node,
    NodeKind,
    ParameterSpec,
    PortSpec,
)
from pipelinemodel.refs import OutputRef, as_output_ref
from pipelinemodel.transformation import Step

T = TypeVar("T")

_subpipeline_key_counter = itertools.count(1)
_source_key_counter = itertools.count(1)


def _class_annotations(cls: type[Any]) -> dict[str, Any]:
    """Return evaluated class annotations (supports postponed evaluation)."""
    try:
        return inspect.get_annotations(cls, eval_str=True)
    except Exception:
        return dict(getattr(cls, "__annotations__", {}))


class _TypedFactory:
    """Callable ``Source[T]`` / ``Sink[T]`` factory that also works as an annotation."""

    __slots__ = ("__args__", "__origin__", "contract_type", "origin")

    def __init__(self, origin: type[Any], contract_type: type[Any]) -> None:
        self.origin = origin
        self.contract_type = contract_type
        self.__origin__ = origin
        self.__args__ = (contract_type,)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.origin(*args, contract_type=self.contract_type, **kwargs)

    def __repr__(self) -> str:
        name = getattr(self.contract_type, "__name__", self.contract_type)
        return f"{self.origin.__name__}[{name}]"


@dataclass
class Source:
    """A typed logical data origin in a pipeline."""

    binding: str
    contract_type: type[Any] | None = None
    name: str | None = None
    pipeline_id: str | None = None
    producer_key: str = field(
        default_factory=lambda: f"source-{next(_source_key_counter)}"
    )

    def __class_getitem__(cls, item: type[Any]) -> _TypedFactory:
        return _TypedFactory(cls, item)

    @property
    def result(self) -> OutputRef[Any]:
        """Default output reference for this source."""
        return self.as_output_ref()

    def as_output_ref(self, *, default_port: str = "result") -> OutputRef[Any]:
        """Return an OutputRef for this source's produced dataset."""
        name = self.name or ""
        return OutputRef(
            node_name=name,
            port_name=default_port,
            contract_type=self.contract_type,
            pipeline_id=self.pipeline_id,
            node_kind="source",
            producer_key=self.producer_key,
        )

    def bind(self, name: str, *, pipeline_id: str | None = None) -> Source:
        """Return a source bound to a node name within a pipeline."""
        return Source(
            binding=self.binding,
            contract_type=self.contract_type,
            name=name,
            pipeline_id=pipeline_id,
            producer_key=self.producer_key,
        )


@dataclass
class Sink:
    """A typed logical data destination in a pipeline."""

    input: Any
    binding: str
    contract_type: type[Any] | None = None
    name: str | None = None
    pipeline_id: str | None = None

    def __class_getitem__(cls, item: type[Any]) -> _TypedFactory:
        return _TypedFactory(cls, item)

    def bind(self, name: str, *, pipeline_id: str | None = None) -> Sink:
        """Return a sink bound to a node name within a pipeline."""
        return Sink(
            input=self.input,
            binding=self.binding,
            contract_type=self.contract_type,
            name=name,
            pipeline_id=pipeline_id,
        )


@dataclass
class SubpipelineInstance:
    """An embedded child pipeline with parent-side bindings."""

    pipeline_cls: type[Pipeline]
    bindings: dict[str, Any]
    name: str | None = None
    pipeline_id: str | None = None
    producer_key: str = field(
        default_factory=lambda: f"subpipeline-{next(_subpipeline_key_counter)}"
    )
    _outputs: dict[str, OutputRef[Any]] = field(default_factory=dict, repr=False)

    def bind_name(
        self, name: str, *, pipeline_id: str | None = None
    ) -> SubpipelineInstance:
        """Bind this subpipeline instance to a parent node name."""
        child_graph = self.pipeline_cls.build_graph()
        outputs: dict[str, OutputRef[Any]] = {}
        for node in child_graph.nodes:
            if node.kind is NodeKind.SINK:
                outputs[node.name] = OutputRef(
                    node_name=name,
                    port_name=node.name,
                    contract_type=node.contract_type,
                    pipeline_id=pipeline_id,
                    node_kind="subpipeline",
                    producer_key=self.producer_key,
                )
        return SubpipelineInstance(
            pipeline_cls=self.pipeline_cls,
            bindings=dict(self.bindings),
            name=name,
            pipeline_id=pipeline_id,
            producer_key=self.producer_key,
            _outputs=outputs,
        )

    def __getattr__(self, item: str) -> OutputRef[Any]:
        if item.startswith("_"):
            raise AttributeError(item)
        if item in self._outputs:
            return self._outputs[item]
        child = self.pipeline_cls.build_graph()
        for node in child.nodes:
            if node.kind is NodeKind.SINK and node.name == item:
                return OutputRef(
                    node_name=self.name or "",
                    port_name=item,
                    contract_type=node.contract_type,
                    pipeline_id=self.pipeline_id,
                    node_kind="subpipeline",
                    producer_key=self.producer_key,
                )
        available = ", ".join(sorted(self._outputs)) or "(none)"
        msg = f"Subpipeline has no public output {item!r}. Available: {available}"
        raise AttributeError(msg)


class _PipelineNamespace(dict[str, Any]):
    """Class body namespace that records declaration order of pipeline members."""

    def __init__(self) -> None:
        super().__init__()
        self._member_order: list[str] = []

    def __setitem__(self, key: str, value: Any) -> None:
        if (
            not key.startswith("_")
            and key not in self
            and isinstance(value, (Source, Sink, Step, SubpipelineInstance))
        ):
            self._member_order.append(key)
        super().__setitem__(key, value)


class _PipelineMeta(type):
    """Metaclass that preserves pipeline member declaration order."""

    @classmethod
    def __prepare__(
        mcs, name: str, bases: tuple[type, ...], **kwargs: Any
    ) -> _PipelineNamespace:
        return _PipelineNamespace()

    def __new__(
        mcs,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        **kwargs: Any,
    ) -> _PipelineMeta:
        order = list(getattr(namespace, "_member_order", []))
        cls = super().__new__(mcs, name, bases, dict(namespace))
        cls.__member_order__ = order  # type: ignore[attr-defined]
        return cls


class Pipeline(metaclass=_PipelineMeta):
    """Declarative typed pipeline graph.

    Subclasses declare ``Source``, transformation ``Step``, ``Sink``, and
    optional subpipeline members. Importing a pipeline does not execute it.
    """

    __member_order__: ClassVar[list[str]] = []
    __pipeline_members__: ClassVar[dict[str, Any]] = {}
    _cached_graph: ClassVar[LogicalGraph | None] = None

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if cls is Pipeline:
            return
        members = _collect_pipeline_members(cls)
        cls.__pipeline_members__ = members
        cls._cached_graph = None

    @classmethod
    def identity(cls) -> str:
        """Stable pipeline identity."""
        return pipeline_id(cls)

    @classmethod
    def build_graph(cls) -> LogicalGraph:
        """Build (and cache) the immutable logical graph for this pipeline."""
        if cls._cached_graph is not None:
            return cls._cached_graph
        graph = _build_logical_graph(cls)
        cls._cached_graph = graph
        return graph

    @classmethod
    def inspect(cls) -> LogicalGraph:
        """Return the read-only logical graph for this pipeline."""
        from pipelinemodel.inspection import inspect_pipeline

        return inspect_pipeline(cls)

    @classmethod
    def validate(cls):  # type: ignore[no-untyped-def]
        """Validate the pipeline and return a structured report."""
        from pipelinemodel.validation import validate_pipeline

        return validate_pipeline(cls)

    @classmethod
    def to_mermaid(cls) -> str:
        """Generate a Mermaid flowchart from the logical graph."""
        from pipelinemodel.mermaid import graph_to_mermaid

        return graph_to_mermaid(cls.build_graph())

    @classmethod
    def subpipeline(cls, **bindings: Any) -> SubpipelineInstance:
        """Embed this pipeline as a reusable subpipeline in a parent."""
        return SubpipelineInstance(pipeline_cls=cls, bindings=dict(bindings))


def _annotation_contract(cls: type[Any], name: str) -> type[Any] | None:
    """Extract a contract type from a Source[T] / Sink[T] class annotation."""
    annotations = _class_annotations(cls)
    annotation = annotations.get(name)
    if annotation is None:
        return None
    if isinstance(annotation, _TypedFactory) and is_data_contract_type(
        annotation.contract_type
    ):
        return annotation.contract_type
    contract = getattr(annotation, "contract_type", None)
    if contract is not None and is_data_contract_type(contract):
        return contract
    args = getattr(annotation, "__args__", None)
    if args and is_data_contract_type(args[0]):
        return args[0]
    return None


def _collect_pipeline_members(cls: type[Pipeline]) -> dict[str, Any]:
    """Collect Source/Step/Sink/Subpipeline members in declaration order."""
    order = list(getattr(cls, "__member_order__", []))
    members: dict[str, Any] = {}

    names = order or [
        k
        for k, v in cls.__dict__.items()
        if not k.startswith("_")
        and isinstance(v, (Source, Sink, Step, SubpipelineInstance))
    ]

    seen: set[str] = set()
    ordered_names: list[str] = []
    for name in names:
        if name not in seen and name in cls.__dict__:
            seen.add(name)
            ordered_names.append(name)
    for name, value in cls.__dict__.items():
        if (
            name not in seen
            and not name.startswith("_")
            and isinstance(value, (Source, Sink, Step, SubpipelineInstance))
        ):
            seen.add(name)
            ordered_names.append(name)

    pid = pipeline_id(cls)
    for name in ordered_names:
        value = cls.__dict__[name]
        if isinstance(value, Source):
            contract = value.contract_type or _annotation_contract(cls, name)
            members[name] = Source(
                binding=value.binding,
                contract_type=contract,
                name=name,
                pipeline_id=pid,
                producer_key=value.producer_key,
            )
        elif isinstance(value, Sink):
            contract = value.contract_type or _annotation_contract(cls, name)
            members[name] = Sink(
                input=value.input,
                binding=value.binding,
                contract_type=contract,
                name=name,
                pipeline_id=pid,
            )
        elif isinstance(value, (Step, SubpipelineInstance)):
            members[name] = value.bind_name(name, pipeline_id=pid)

    cls.__member_order__ = list(members.keys())
    return members


def _build_logical_graph(cls: type[Pipeline]) -> LogicalGraph:
    """Construct a deterministic LogicalGraph from a Pipeline class."""
    members = cls.__pipeline_members__
    pid = pipeline_id(cls)
    nodes: list[Node] = []
    edges: list[Edge] = []

    # First pass: create nodes
    for name, member in members.items():
        nid = node_id(pid, name)
        if isinstance(member, Source):
            ctype = member.contract_type
            cid = contract_id(ctype) if ctype is not None else None
            nodes.append(
                Node(
                    name=name,
                    kind=NodeKind.SOURCE,
                    identity=nid,
                    contract_type=ctype,
                    contract_id=cid,
                    binding=member.binding,
                    outputs=(
                        PortSpec(
                            name="result",
                            direction="output",
                            contract_type=ctype,
                            contract_id=cid,
                        ),
                    ),
                )
            )
        elif isinstance(member, Step):
            transform = member.transformation
            inputs = tuple(
                PortSpec(
                    name=p.name,
                    direction="input",
                    contract_type=p.contract_type,
                    contract_id=contract_id(p.contract_type)
                    if p.contract_type is not None
                    else None,
                )
                for p in transform.inputs()
            )
            outputs = tuple(
                PortSpec(
                    name=p.name,
                    direction="output",
                    contract_type=p.contract_type,
                    contract_id=contract_id(p.contract_type)
                    if p.contract_type is not None
                    else None,
                )
                for p in transform.outputs()
            )
            params = tuple(
                ParameterSpec(
                    name=p.name,
                    value_type=p.contract_type,
                    default=p.default,
                    has_default=p.has_default,
                    value=member.parameters.get(p.name, ...),
                    has_value=p.name in member.parameters,
                )
                for p in transform.parameters()
            )
            nodes.append(
                Node(
                    name=name,
                    kind=NodeKind.STEP,
                    identity=nid,
                    transformation_id=transform.identity(),
                    transformation_name=transform.__name__,
                    inputs=inputs,
                    outputs=outputs,
                    parameters=params,
                )
            )
        elif isinstance(member, Sink):
            ctype = member.contract_type
            cid = contract_id(ctype) if ctype is not None else None
            nodes.append(
                Node(
                    name=name,
                    kind=NodeKind.SINK,
                    identity=nid,
                    contract_type=ctype,
                    contract_id=cid,
                    binding=member.binding,
                    inputs=(
                        PortSpec(
                            name="input",
                            direction="input",
                            contract_type=ctype,
                            contract_id=cid,
                        ),
                    ),
                )
            )
        elif isinstance(member, SubpipelineInstance):
            nested = member.pipeline_cls.build_graph()
            # Public inputs = child sources; public outputs = child sinks
            inputs = tuple(
                PortSpec(
                    name=n.name,
                    direction="input",
                    contract_type=n.contract_type,
                    contract_id=n.contract_id,
                )
                for n in nested.nodes
                if n.kind is NodeKind.SOURCE
            )
            outputs = tuple(
                PortSpec(
                    name=n.name,
                    direction="output",
                    contract_type=n.contract_type,
                    contract_id=n.contract_id,
                )
                for n in nested.nodes
                if n.kind is NodeKind.SINK
            )
            nodes.append(
                Node(
                    name=name,
                    kind=NodeKind.SUBPIPELINE,
                    identity=nid,
                    nested_pipeline_id=nested.pipeline_id,
                    nested_graph=nested,
                    inputs=inputs,
                    outputs=outputs,
                )
            )

    node_by_name = {n.name: n for n in nodes}

    # Second pass: edges from step bindings and sinks
    for name, member in members.items():
        if isinstance(member, Step):
            for port_name, raw in member.bindings.items():
                producer = _resolve_binding_ref(
                    raw, members=members, pipeline_cls=cls, port_hint=port_name
                )
                if producer is None:
                    continue
                consumer_port = next(
                    (p for p in node_by_name[name].inputs if p.name == port_name),
                    None,
                )
                edges.append(
                    Edge(
                        producer_node=producer.node_name,
                        producer_port=producer.port_name,
                        consumer_node=name,
                        consumer_port=port_name,
                        producer_contract_id=contract_id(producer.contract_type)
                        if producer.contract_type is not None
                        else None,
                        consumer_contract_id=consumer_port.contract_id
                        if consumer_port
                        else None,
                    )
                )
        elif isinstance(member, Sink):
            producer = _resolve_binding_ref(
                member.input, members=members, pipeline_cls=cls, port_hint="input"
            )
            if producer is not None:
                edges.append(
                    Edge(
                        producer_node=producer.node_name,
                        producer_port=producer.port_name,
                        consumer_node=name,
                        consumer_port="input",
                        producer_contract_id=contract_id(producer.contract_type)
                        if producer.contract_type is not None
                        else None,
                        consumer_contract_id=node_by_name[name].contract_id,
                    )
                )
        elif isinstance(member, SubpipelineInstance):
            for port_name, raw in member.bindings.items():
                producer = _resolve_binding_ref(
                    raw, members=members, pipeline_cls=cls, port_hint=port_name
                )
                if producer is None:
                    continue
                edges.append(
                    Edge(
                        producer_node=producer.node_name,
                        producer_port=producer.port_name,
                        consumer_node=name,
                        consumer_port=port_name,
                        producer_contract_id=contract_id(producer.contract_type)
                        if producer.contract_type is not None
                        else None,
                        consumer_contract_id=next(
                            (
                                p.contract_id
                                for p in node_by_name[name].inputs
                                if p.name == port_name
                            ),
                            None,
                        ),
                    )
                )

    return LogicalGraph(
        pipeline_id=pid,
        pipeline_name=cls.__name__,
        nodes=tuple(nodes),
        edges=tuple(edges),
    )


def _resolve_binding_ref(
    value: Any,
    *,
    members: dict[str, Any],
    pipeline_cls: type[Pipeline],
    port_hint: str,
) -> OutputRef[Any] | None:
    """Resolve a step/sink/subpipeline binding to a concrete OutputRef."""
    pid = pipeline_id(pipeline_cls)

    if isinstance(value, OutputRef) and value.node_name:
        return value if value.pipeline_id else value.bind_pipeline(pid)

    if isinstance(value, OutputRef) and value.producer_key:
        for member in members.values():
            if (
                isinstance(member, Step)
                and member.producer_key == value.producer_key
                and value.port_name in member.output_refs
            ):
                return member.output_refs[value.port_name]
            if isinstance(member, Source) and member.producer_key == value.producer_key:
                return member.as_output_ref()
            if (
                isinstance(member, SubpipelineInstance)
                and member.producer_key == value.producer_key
            ):
                if value.port_name in member._outputs:
                    return member._outputs[value.port_name]
                # Rebuild from nested sinks if outputs not yet populated
                for node in member.pipeline_cls.build_graph().nodes:
                    if (
                        node.kind is NodeKind.SINK
                        and node.name == value.port_name
                        and member.name
                    ):
                        return OutputRef(
                            node_name=member.name,
                            port_name=node.name,
                            contract_type=node.contract_type,
                            pipeline_id=member.pipeline_id,
                            node_kind="subpipeline",
                            producer_key=member.producer_key,
                        )
    if isinstance(value, Source):
        for member in members.values():
            if not isinstance(member, Source):
                continue
            if value.name and member.name == value.name:
                return member.as_output_ref()
        for member in members.values():
            if (
                isinstance(member, Source)
                and member.binding == value.binding
                and (
                    value.contract_type is None
                    or member.contract_type is value.contract_type
                )
            ):
                return member.as_output_ref()
        return value.as_output_ref()

    if isinstance(value, Step):
        for member in members.values():
            if isinstance(member, Step) and member.producer_key == value.producer_key:
                return member.as_output_ref()
        return value.as_output_ref()

    if isinstance(value, OutputRef):
        matches: list[OutputRef[Any]] = []
        for member in members.values():
            if isinstance(member, Step) and value.port_name in member.output_refs:
                candidate = member.output_refs[value.port_name]
                if (
                    value.contract_type is None
                    or candidate.contract_type is value.contract_type
                ):
                    matches.append(candidate)
            elif isinstance(member, Source) and value.port_name in {"result", "output"}:
                if (
                    value.contract_type is None
                    or member.contract_type is value.contract_type
                ):
                    matches.append(member.as_output_ref())
        if len(matches) == 1:
            return matches[0]
        if matches:
            return matches[0]
        return None

    return as_output_ref(value)
