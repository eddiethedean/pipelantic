"""Declarative plugin group specifications."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class PluginGroupSpec:
    """One entry-point group and how to register discovered plugins."""

    entry_point_group: str
    runtime_attr: str
    key_fn: Callable[[Any, Any], str] | None = None
    # register_kind: dataframe | sql | spark | orchestrator | scheduler | compiler
    register_kind: str = "none"
