"""Stable identity helpers for pipelines, nodes, ports, and contracts."""

from __future__ import annotations

from typing import Any


def qualified_type_id(obj: type[Any] | Any) -> str:
    """Return a stable identity for a class or object type.

    Format: ``{module}:{qualname}``. Never uses memory addresses.
    """
    if not isinstance(obj, type):
        obj = type(obj)
    module = getattr(obj, "__module__", None) or "<unknown>"
    qualname = getattr(obj, "__qualname__", None) or getattr(obj, "__name__", "?")
    return f"{module}:{qualname}"


def pipeline_id(pipeline_cls: type[Any]) -> str:
    """Stable identity for a pipeline class."""
    return qualified_type_id(pipeline_cls)


def transformation_id(transformation_cls: type[Any]) -> str:
    """Stable identity for a transformation class."""
    return qualified_type_id(transformation_cls)


def contract_id(contract_type: type[Any]) -> str:
    """Stable identity for a data-contract type."""
    return qualified_type_id(contract_type)


def node_id(pipeline: str, node_name: str) -> str:
    """Stable identity for a node within a pipeline."""
    return f"{pipeline}/{node_name}"


def port_id(node: str, port_name: str) -> str:
    """Stable identity for a port on a node."""
    return f"{node}:{port_name}"


def implementation_id(transform: str, engine: str) -> str:
    """Stable identity for a registered transformation implementation."""
    return f"{transform}/{engine}"
