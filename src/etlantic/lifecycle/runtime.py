"""PipelineRuntime — registries, lifespan, middleware, resources."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from dataclasses import dataclass, field
from typing import Any

from etlantic.diagnostics import Diagnostic, Severity
from etlantic.lifecycle.callbacks import CallbackRegistry
from etlantic.lifecycle.middleware import MiddlewareStack
from etlantic.lifecycle.resources import ResourceManager
from etlantic.profile import Profile
from etlantic.registry import RegistryBundle, builtin_stub_registry
from etlantic.reports.store import ReportStore
from etlantic.runtime.events import EventBus
from etlantic.secrets.cache import SecretCache
from etlantic.secrets.env import EnvSecretProvider
from etlantic.secrets.provider import SecretProvider
from etlantic.storage.callable_binding import CallableStorage
from etlantic.storage.csv_binding import CsvStorage
from etlantic.storage.json_binding import JsonStorage
from etlantic.storage.memory import MemoryStorage
from etlantic.storage.null import NullStorage
from etlantic.storage.protocol import StorageBinding

Lifespan = Callable[["PipelineRuntime"], AbstractAsyncContextManager[Any]]


def _profile_plugin_key(profile: Profile) -> str:
    """Stable key for profile-scoped plugin discovery idempotency."""
    payload = {
        "name": profile.name,
        "security_mode": profile.security_mode,
        "plugin_allowlist": dict(profile.plugin_allowlist or {}),
        "require_plugin_probe": profile.require_plugin_probe,
    }
    return json.dumps(payload, sort_keys=True)


@dataclass
class PipelineRuntime:
    """Process-scoped runtime coordinating local execution."""

    lifespan: Lifespan | None = None
    registry: RegistryBundle = field(default_factory=builtin_stub_registry)
    resources: ResourceManager = field(default_factory=ResourceManager)
    callbacks: CallbackRegistry = field(default_factory=CallbackRegistry)
    reports: ReportStore = field(default_factory=ReportStore)
    events: EventBus = field(default_factory=EventBus)
    secret_cache: SecretCache = field(default_factory=SecretCache)
    run_middleware: MiddlewareStack = field(default_factory=MiddlewareStack)
    step_middleware: MiddlewareStack = field(default_factory=MiddlewareStack)
    provider_middleware: MiddlewareStack = field(default_factory=MiddlewareStack)
    secret_providers: dict[str, SecretProvider] = field(default_factory=dict)
    storage: dict[str, StorageBinding] = field(default_factory=dict)
    dataframe_plugins: dict[str, Any] = field(default_factory=dict)
    sql_plugins: dict[str, Any] = field(default_factory=dict)
    spark_plugins: dict[str, Any] = field(default_factory=dict)
    spark_providers: dict[str, Any] = field(default_factory=dict)
    orchestrator_plugins: dict[str, Any] = field(default_factory=dict)
    scheduler_plugins: dict[str, Any] = field(default_factory=dict)
    memory: MemoryStorage = field(default_factory=MemoryStorage)
    callables: CallableStorage = field(default_factory=CallableStorage)
    _entered: bool = False
    _configured_profile_key: str | None = field(default=None, repr=False)
    _plugin_diagnostics: list[Diagnostic] = field(default_factory=list, repr=False)

    def __post_init__(self) -> None:
        if (
            "env" not in self.secret_providers
            and "env-secrets" not in self.secret_providers
        ):
            env = EnvSecretProvider()
            self.secret_providers["env"] = env
            self.secret_providers["env-secrets"] = env
        if not self.storage:
            self.storage = {
                "memory": self.memory,
                "local": self.memory,
                "python": self.memory,
                "callable": self.callables,
                "json": JsonStorage(),
                "csv": CsvStorage(),
                "null": NullStorage(),
            }
        else:
            self.storage.setdefault("memory", self.memory)
            self.storage.setdefault("local", self.memory)
            self.storage.setdefault("python", self.memory)

    def ensure_plugins_for_profile(self, profile: Profile) -> list[Diagnostic]:
        """Discover and load plugins authorized for ``profile`` (0.20).

        Idempotent per profile key. No entry points are imported until this
        method runs (or manual ``register_*_plugin`` calls).
        """
        key = _profile_plugin_key(profile)
        if self._configured_profile_key == key:
            return list(self._plugin_diagnostics)

        diagnostics: list[Diagnostic] = []
        from etlantic.dataframe.discovery import (
            DATAFRAME_PLUGIN_ENTRY_POINT,
            register_discovered_plugins,
        )
        from etlantic.orchestration.discovery import ORCHESTRATOR_PLUGIN_ENTRY_POINT
        from etlantic.plugin_lifecycle import discover_evaluate_authorize_load
        from etlantic.runtime.scheduler_discovery import SCHEDULER_PLUGIN_ENTRY_POINT
        from etlantic.spark.discovery import (
            SPARK_PLUGIN_ENTRY_POINT,
            SPARK_PROVIDER_ENTRY_POINT,
        )
        from etlantic.sql.discovery import SQL_PLUGIN_ENTRY_POINT
        from etlantic.transform.discovery import (
            TRANSFORM_COMPILER_ENTRY_POINT,
        )
        from etlantic.transform.discovery import (
            _key as transform_key,
        )

        def _df_key(item: Any, plugin: Any) -> str:
            return str(
                getattr(getattr(plugin, "info", None), "engine", None) or item.name
            )

        def _generic_key(item: Any, plugin: Any) -> str:
            return str(
                getattr(getattr(plugin, "info", None), "engine", None) or item.name
            )

        def _provider_key(item: Any, plugin: Any) -> str:
            return str(
                getattr(getattr(plugin, "info", None), "name", None) or item.name
            )

        groups: list[tuple[str, str, Callable[[Any, Any], str] | None, str]] = [
            (DATAFRAME_PLUGIN_ENTRY_POINT, "dataframe", _df_key, "dataframe_plugins"),
            (SQL_PLUGIN_ENTRY_POINT, "sql", _generic_key, "sql_plugins"),
            (SPARK_PLUGIN_ENTRY_POINT, "spark", _generic_key, "spark_plugins"),
            (
                ORCHESTRATOR_PLUGIN_ENTRY_POINT,
                "orchestrator",
                _generic_key,
                "orchestrator_plugins",
            ),
            (
                SCHEDULER_PLUGIN_ENTRY_POINT,
                "scheduler",
                None,
                "scheduler_plugins",
            ),
        ]

        for group, _label, key_fn, attr in groups:
            try:
                result = discover_evaluate_authorize_load(
                    group, profile=profile, key_fn=key_fn
                )
                diagnostics.extend(result.diagnostics)
                setattr(self, attr, dict(result.loaded))
                if attr == "dataframe_plugins":
                    register_discovered_plugins(
                        self.registry, plugins=result.loaded, profile=profile
                    )
                elif attr == "sql_plugins":
                    from etlantic.sql.discovery import (
                        register_discovered_plugins as register_sql,
                    )

                    register_sql(self.registry, plugins=result.loaded, profile=profile)
                elif attr == "spark_plugins":
                    from etlantic.spark.discovery import (
                        register_discovered_plugins as register_spark,
                    )

                    register_spark(
                        self.registry, plugins=result.loaded, profile=profile
                    )
                elif attr == "orchestrator_plugins":
                    from etlantic.orchestration.discovery import (
                        register_discovered_plugins as register_orch,
                    )

                    register_orch(self.registry, plugins=result.loaded, profile=profile)
                elif attr == "scheduler_plugins":
                    from etlantic.runtime.scheduler_discovery import (
                        register_discovered_plugins as register_sched,
                    )

                    register_sched(
                        self.registry, plugins=result.loaded, profile=profile
                    )
            except Exception as exc:
                diagnostics.append(
                    Diagnostic(
                        code="PMPLUG421",
                        severity=Severity.ERROR,
                        message=f"Plugin discovery failed for {group}: {exc}",
                        path=("plugin", group),
                        phase="plugin_load",
                    )
                )

        try:
            spark_providers = discover_evaluate_authorize_load(
                SPARK_PROVIDER_ENTRY_POINT,
                profile=profile,
                key_fn=_provider_key,
            )
            diagnostics.extend(spark_providers.diagnostics)
            self.spark_providers = dict(spark_providers.loaded)
        except Exception as exc:
            diagnostics.append(
                Diagnostic(
                    code="PMPLUG421",
                    severity=Severity.ERROR,
                    message=f"Spark provider discovery failed: {exc}",
                    path=("plugin", "spark_providers"),
                    phase="plugin_load",
                )
            )

        try:
            compilers = discover_evaluate_authorize_load(
                TRANSFORM_COMPILER_ENTRY_POINT,
                profile=profile,
                key_fn=transform_key,
            )
            diagnostics.extend(compilers.diagnostics)
            from etlantic.transform.discovery import register_discovered_compilers

            register_discovered_compilers(
                self.registry, compilers=compilers.loaded, profile=profile
            )
        except Exception as exc:
            diagnostics.append(
                Diagnostic(
                    code="PMPLUG421",
                    severity=Severity.ERROR,
                    message=f"Transform compiler discovery failed: {exc}",
                    path=("plugin", "transform_compiler"),
                    phase="plugin_load",
                )
            )

        self._configured_profile_key = key
        self._plugin_diagnostics = diagnostics
        return list(diagnostics)

    def add_run_middleware(self, middleware: Any, *, name: str | None = None) -> None:
        self.run_middleware.add(middleware, name=name)

    def add_step_middleware(self, middleware: Any, *, name: str | None = None) -> None:
        self.step_middleware.add(middleware, name=name)

    def override_resource(self, name: str, provider: Callable[..., Any]) -> None:
        self.resources.override(name, provider)

    def register_secret_provider(self, name: str, provider: SecretProvider) -> None:
        self.secret_providers[name] = provider

    def register_storage(self, name: str, binding: StorageBinding) -> None:
        self.storage[name] = binding

    def register_dataframe_plugin(self, engine: str, plugin: Any) -> None:
        """Register a live dataframe plugin and its planning descriptor."""
        from etlantic.dataframe.discovery import register_discovered_plugins

        self.dataframe_plugins[engine] = plugin
        register_discovered_plugins(self.registry, plugins={engine: plugin})

    def register_sql_plugin(self, engine: str, plugin: Any) -> None:
        """Register a live SQL plugin and its planning descriptor."""
        from etlantic.sql.discovery import register_discovered_plugins

        self.sql_plugins[engine] = plugin
        register_discovered_plugins(self.registry, plugins={engine: plugin})

    def register_spark_plugin(self, engine: str, plugin: Any) -> None:
        """Register a live Spark plugin and its planning descriptor."""
        from etlantic.spark.discovery import register_discovered_plugins

        self.spark_plugins[engine] = plugin
        register_discovered_plugins(self.registry, plugins={engine: plugin})

    def register_spark_provider(self, name: str, provider: Any) -> None:
        """Register a live Spark session provider."""
        self.spark_providers[name] = provider

    def register_orchestrator_plugin(self, engine: str, plugin: Any) -> None:
        """Register a live orchestrator plugin and its planning descriptor."""
        from etlantic.orchestration.discovery import register_discovered_plugins

        self.orchestrator_plugins[engine] = plugin
        register_discovered_plugins(self.registry, plugins={engine: plugin})

    def register_scheduler_plugin(self, name: str, plugin: Any) -> None:
        """Register a live ExecutionScheduler plugin and its planning descriptor."""
        from etlantic.runtime.scheduler_discovery import register_discovered_plugins

        self.scheduler_plugins[name] = plugin
        register_discovered_plugins(self.registry, plugins={name: plugin})

    def apply_plugin_allowlist(self, profile: Any) -> list[Any]:
        """Filter discovered plugins using ``profile.plugin_allowlist``.

        Deprecated: prefer :meth:`ensure_plugins_for_profile` which authorizes
        before import. This method re-runs profile-aware discovery.
        """
        from etlantic.profile import Profile as ProfileType

        if isinstance(profile, ProfileType):
            return self.ensure_plugins_for_profile(profile)
        from etlantic.profile import resolve_profile

        return self.ensure_plugins_for_profile(resolve_profile(profile))

    @asynccontextmanager
    async def session(self) -> AsyncIterator[PipelineRuntime]:
        """Enter runtime lifespan (if any)."""
        if self.lifespan is None:
            self._entered = True
            try:
                yield self
            finally:
                self._entered = False
                await self.resources.cleanup_scope("runtime")
            return

        async with self.lifespan(self):
            self._entered = True
            try:
                yield self
            finally:
                self._entered = False
                await self.resources.cleanup_scope("runtime")
