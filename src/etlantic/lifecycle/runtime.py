"""PipelineRuntime — registries, lifespan, middleware, resources."""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from dataclasses import dataclass, field
from typing import Any

from etlantic.diagnostics import Diagnostic
from etlantic.lifecycle.callbacks import CallbackRegistry
from etlantic.lifecycle.middleware import MiddlewareStack
from etlantic.lifecycle.resources import ResourceManager
from etlantic.plugins.coordinator import PluginDiscoveryCoordinator, profile_plugin_key
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
        key = profile_plugin_key(profile)
        if self._configured_profile_key == key:
            return list(self._plugin_diagnostics)

        coordinator = PluginDiscoveryCoordinator()
        result = coordinator.discover_for_profile(
            profile,
            registry=self.registry,
            register_to_registry=True,
            include_runtime_groups=True,
            include_transform_compilers=True,
        )
        for key, plugin in result.dataframe_plugins.items():
            self.dataframe_plugins.setdefault(key, plugin)
        for key, plugin in result.sql_plugins.items():
            self.sql_plugins.setdefault(key, plugin)
        for key, plugin in result.spark_plugins.items():
            self.spark_plugins.setdefault(key, plugin)
        for key, provider in result.spark_providers.items():
            self.spark_providers.setdefault(key, provider)
        for key, plugin in result.orchestrator_plugins.items():
            self.orchestrator_plugins.setdefault(key, plugin)
        for key, plugin in result.scheduler_plugins.items():
            self.scheduler_plugins.setdefault(key, plugin)
        self._configured_profile_key = key
        self._plugin_diagnostics = list(result.diagnostics)
        return list(result.diagnostics)

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
