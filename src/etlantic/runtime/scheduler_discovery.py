"""Entry-point discovery for direct-execution scheduler plugins."""

from __future__ import annotations

import logging
import warnings
from importlib.metadata import entry_points
from typing import Any

from etlantic.registry import PluginDescriptor, RegistryBundle
from etlantic.runtime.scheduler import (
    SCHEDULER_PROTOCOL,
    ExecutionScheduler,
    LocalScheduler,
)

SCHEDULER_PLUGIN_ENTRY_POINT = "etlantic.scheduler_plugins"
_LOG = logging.getLogger(__name__)

# Compile-only engines must never be treated as ExecutionScheduler names.
_COMPILE_ONLY = frozenset({"airflow"})


def _iter_entry_points(group: str) -> Any:
    try:
        return entry_points(group=group)
    except TypeError:  # pragma: no cover
        return entry_points().get(group, [])  # type: ignore[attr-defined]


def discover_scheduler_plugins() -> dict[str, ExecutionScheduler]:
    """Load scheduler plugins registered under the entry-point group."""
    found: dict[str, ExecutionScheduler] = {}
    for ep in _iter_entry_points(SCHEDULER_PLUGIN_ENTRY_POINT):
        try:
            factory = ep.load()
            plugin = factory() if callable(factory) else factory
            name = getattr(getattr(plugin, "info", None), "name", None) or ep.name
            key = str(name)
            if key in _COMPILE_ONLY:
                warnings.warn(
                    f"Ignoring scheduler entry point {ep.name!r}: {key!r} is a "
                    "compile-only orchestrator name, not an ExecutionScheduler.",
                    RuntimeWarning,
                    stacklevel=2,
                )
                continue
            found[key] = plugin
        except Exception as exc:
            msg = f"Failed to load scheduler plugin entry point {ep.name!r}: {exc}"
            _LOG.warning(msg)
            warnings.warn(msg, RuntimeWarning, stacklevel=2)
            continue
    return found


def register_discovered_plugins(
    registry: RegistryBundle,
    *,
    plugins: dict[str, ExecutionScheduler] | None = None,
) -> dict[str, ExecutionScheduler]:
    """Register discovered scheduler plugins into a planning registry."""
    discovered = plugins if plugins is not None else discover_scheduler_plugins()
    for name, plugin in discovered.items():
        info = plugin.info
        registry.register_plugin(
            PluginDescriptor(
                name=info.name,
                kind="scheduler",
                version=info.version,
                engine=info.name or name,
                capabilities={
                    "direct_execution": info.direct_execution,
                    "external_compilation": info.external_compilation,
                },
                metadata={"protocol_version": info.scheduler_protocol},
            )
        )
    return discovered


def builtin_local_scheduler() -> LocalScheduler:
    """Return the built-in zero-install local scheduler."""
    return LocalScheduler()


def resolve_scheduler(
    name: str,
    *,
    plugins: dict[str, ExecutionScheduler] | None = None,
) -> ExecutionScheduler:
    """Resolve a scheduler by profile/orchestrator name (fail closed)."""
    key = str(name or "local").strip() or "local"
    if key in _COMPILE_ONLY:
        from etlantic.exceptions import ETLanticError

        raise ETLanticError(
            f"Orchestrator {key!r} is a compile target (etlantic.orchestration/1), "
            "not a direct-execution scheduler. Use LocalScheduler or an "
            f"{SCHEDULER_PROTOCOL} plugin such as prefect, or compile with "
            "`etlantic compile --target airflow`."
        )
    if key == "local":
        return builtin_local_scheduler()
    discovered = plugins if plugins is not None else discover_scheduler_plugins()
    plugin = discovered.get(key)
    if plugin is None:
        from etlantic.exceptions import ETLanticError

        raise ETLanticError(
            f"No ExecutionScheduler named {key!r} is installed. Install the "
            f"optional plugin (for example etlantic-prefect) or set "
            "Profile(orchestrator='local')."
        )
    return plugin


def load_scheduler_plugin(name: str) -> ExecutionScheduler | None:
    """Return a discovered scheduler plugin for ``name``, or None."""
    if name == "local":
        return builtin_local_scheduler()
    return discover_scheduler_plugins().get(name)


def plugin_registry_snapshot() -> list[dict[str, Any]]:
    """Return serializable descriptors for discovered scheduler plugins."""
    local = builtin_local_scheduler()
    items = [local.info.to_dict()]
    items.extend(
        plugin.info.to_dict() for plugin in discover_scheduler_plugins().values()
    )
    return items
