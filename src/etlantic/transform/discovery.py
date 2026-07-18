"""Entry-point discovery for portable transform compilers."""

from __future__ import annotations

import logging
import warnings
from importlib.metadata import entry_points
from typing import Any

from etlantic.registry import PluginDescriptor, RegistryBundle
from etlantic.transform.compiler import PortableTransformCompiler

TRANSFORM_COMPILER_ENTRY_POINT = "etlantic.transform_compilers"
_LOG = logging.getLogger(__name__)


def discover_transform_compilers() -> dict[str, PortableTransformCompiler]:
    """Load compilers registered under ``etlantic.transform_compilers``.

    Returns engine name → compiler instance. Broken entry points are skipped
    with a warning (planning fails closed when the selected engine lacks a
    compiler and policy requires portable compilation).
    """
    found: dict[str, PortableTransformCompiler] = {}
    try:
        eps = entry_points(group=TRANSFORM_COMPILER_ENTRY_POINT)
    except TypeError:  # pragma: no cover - older importlib API
        eps = entry_points().get(TRANSFORM_COMPILER_ENTRY_POINT, [])  # type: ignore[attr-defined]
    for ep in eps:
        try:
            factory = ep.load()
            compiler = factory() if callable(factory) else factory
            engine = getattr(getattr(compiler, "info", None), "engine", None) or ep.name
            engine_key = str(engine)
            if engine_key in found:
                warnings.warn(
                    f"Multiple transform compilers for engine {engine_key!r}; "
                    f"entry point {ep.name!r} overrides the previous registration.",
                    RuntimeWarning,
                    stacklevel=2,
                )
            found[engine_key] = compiler
        except Exception as exc:
            msg = f"Failed to load transform compiler entry point {ep.name!r}: {exc}"
            _LOG.warning(msg)
            warnings.warn(msg, RuntimeWarning, stacklevel=2)
            continue
    return found


def register_discovered_compilers(
    registry: RegistryBundle,
    *,
    compilers: dict[str, PortableTransformCompiler] | None = None,
) -> dict[str, PortableTransformCompiler]:
    """Register discovered transform compilers into a planning registry."""
    discovered = compilers if compilers is not None else discover_transform_compilers()
    for engine, compiler in discovered.items():
        info = compiler.info
        registry.register_plugin(
            PluginDescriptor(
                name=info.name,
                kind="transform_compiler",
                version=info.version,
                engine=info.engine or engine,
                capabilities=None,
                metadata={
                    "compiler_protocol": info.compiler_protocol,
                    "dtcs_plan_versions": list(info.dtcs_plan_versions),
                    "transform_capabilities": info.capabilities.to_dict(),
                },
            )
        )
    return discovered


def load_transform_compiler(engine: str) -> PortableTransformCompiler | None:
    """Return a discovered compiler for ``engine``, or None."""
    return discover_transform_compilers().get(engine)


def compiler_registry_snapshot() -> list[dict[str, Any]]:
    """Return serializable descriptors for discovered compilers."""
    return [c.info.to_dict() for c in discover_transform_compilers().values()]
