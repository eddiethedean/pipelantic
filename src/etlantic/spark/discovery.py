"""Entry-point discovery for Spark plugins and providers."""

from __future__ import annotations

import logging
import warnings
from importlib.metadata import entry_points
from typing import Any

from etlantic.registry import PluginDescriptor, RegistryBundle
from etlantic.spark.protocol import SparkPlugin
from etlantic.spark.provider import SparkProvider

SPARK_PLUGIN_ENTRY_POINT = "etlantic.spark_plugins"
SPARK_PROVIDER_ENTRY_POINT = "etlantic.spark_providers"
_LOG = logging.getLogger(__name__)


def _iter_entry_points(group: str) -> Any:
    try:
        return entry_points(group=group)
    except TypeError:  # pragma: no cover
        return entry_points().get(group, [])  # type: ignore[attr-defined]


def discover_spark_plugins() -> dict[str, SparkPlugin]:
    """Load Spark plugins registered under the entry-point group."""
    found: dict[str, SparkPlugin] = {}
    for ep in _iter_entry_points(SPARK_PLUGIN_ENTRY_POINT):
        try:
            factory = ep.load()
            plugin = factory() if callable(factory) else factory
            engine = getattr(getattr(plugin, "info", None), "engine", None) or ep.name
            found[str(engine)] = plugin
        except Exception as exc:
            msg = f"Failed to load Spark plugin entry point {ep.name!r}: {exc}"
            _LOG.warning(msg)
            warnings.warn(msg, RuntimeWarning, stacklevel=2)
            continue
    return found


def discover_spark_providers() -> dict[str, SparkProvider]:
    """Load Spark providers registered under the entry-point group."""
    found: dict[str, SparkProvider] = {}
    for ep in _iter_entry_points(SPARK_PROVIDER_ENTRY_POINT):
        try:
            factory = ep.load()
            provider = factory() if callable(factory) else factory
            name = getattr(getattr(provider, "info", None), "name", None) or ep.name
            found[str(name)] = provider
        except Exception as exc:
            msg = f"Failed to load Spark provider entry point {ep.name!r}: {exc}"
            _LOG.warning(msg)
            warnings.warn(msg, RuntimeWarning, stacklevel=2)
            continue
    return found


def register_discovered_plugins(
    registry: RegistryBundle,
    *,
    plugins: dict[str, SparkPlugin] | None = None,
) -> dict[str, SparkPlugin]:
    """Register discovered Spark plugins into a planning registry."""
    discovered = plugins if plugins is not None else discover_spark_plugins()
    for engine, plugin in discovered.items():
        info = plugin.info
        caps = info.capabilities or plugin.capabilities()
        registry.register_plugin(
            PluginDescriptor(
                name=info.name,
                kind="spark",
                version=info.version,
                engine=info.engine or engine,
                capabilities=caps,
                metadata={
                    "protocol_version": info.protocol_version,
                    "streaming_stability": info.streaming_stability,
                },
            )
        )
    return discovered


def load_spark_plugin(engine: str = "pyspark") -> SparkPlugin | None:
    """Return a discovered plugin for ``engine``, or None."""
    plugins = discover_spark_plugins()
    if engine in plugins:
        return plugins[engine]
    # Alias spark ↔ pyspark
    if engine == "spark":
        return plugins.get("pyspark")
    if engine == "pyspark":
        return plugins.get("spark")
    return None


def load_spark_provider(name: str = "local") -> SparkProvider | None:
    """Return a discovered provider by name, or None."""
    return discover_spark_providers().get(name)


def plugin_registry_snapshot() -> list[dict[str, Any]]:
    """Return serializable descriptors for discovered Spark plugins."""
    return [plugin.info.to_dict() for plugin in discover_spark_plugins().values()]
