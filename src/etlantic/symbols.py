"""Stable symbol identities for models, steps, ports, bindings, and profiles."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from etlantic.identity import (
    contract_id,
    node_id,
    pipeline_id,
    port_id,
    qualified_type_id,
    transformation_id,
)


@dataclass(frozen=True, slots=True)
class SymbolRef:
    """A stable, human-readable symbol identity for diagnostics and tooling."""

    kind: str
    identity: str
    display_name: str
    path: tuple[str, ...] = ()

    def as_object_ref(self) -> str:
        """Return a compact object reference string for SourceLocation."""
        return f"{self.kind}:{self.identity}"


def pipeline_symbol(pipeline_cls: type[Any]) -> SymbolRef:
    """Symbol for a pipeline class."""
    return SymbolRef(
        kind="pipeline",
        identity=pipeline_id(pipeline_cls),
        display_name=pipeline_cls.__name__,
        path=("pipeline",),
    )


def transformation_symbol(transformation_cls: type[Any]) -> SymbolRef:
    """Symbol for a transformation class."""
    return SymbolRef(
        kind="transformation",
        identity=transformation_id(transformation_cls),
        display_name=transformation_cls.__name__,
        path=("transformation",),
    )


def contract_symbol(contract_type: type[Any]) -> SymbolRef:
    """Symbol for a data contract class."""
    return SymbolRef(
        kind="contract",
        identity=contract_id(contract_type),
        display_name=getattr(contract_type, "__name__", str(contract_type)),
        path=("contract",),
    )


def node_symbol(pipeline: str, node_name: str, *, kind: str = "node") -> SymbolRef:
    """Symbol for a pipeline node."""
    return SymbolRef(
        kind=kind,
        identity=node_id(pipeline, node_name),
        display_name=node_name,
        path=("pipeline", node_name),
    )


def port_symbol(
    pipeline: str,
    node_name: str,
    port_name: str,
    *,
    direction: str = "port",
) -> SymbolRef:
    """Symbol for a node port."""
    nid = node_id(pipeline, node_name)
    return SymbolRef(
        kind=direction,
        identity=port_id(nid, port_name),
        display_name=f"{node_name}.{port_name}",
        path=("pipeline", node_name, port_name),
    )


def binding_symbol(binding: str) -> SymbolRef:
    """Symbol for a logical source/sink binding name."""
    return SymbolRef(
        kind="binding",
        identity=f"binding:{binding}",
        display_name=binding,
        path=("binding", binding),
    )


def profile_symbol(profile_name: str) -> SymbolRef:
    """Symbol for a named profile."""
    return SymbolRef(
        kind="profile",
        identity=f"profile:{profile_name}",
        display_name=profile_name,
        path=("profile", profile_name),
    )


def type_symbol(obj: type[Any] | Any) -> SymbolRef:
    """Generic symbol for an arbitrary type or object."""
    name = getattr(obj, "__name__", type(obj).__name__)
    return SymbolRef(
        kind="type",
        identity=qualified_type_id(obj),
        display_name=str(name),
        path=("type",),
    )
