"""PipelineRuntime — registries, lifespan, middleware, resources."""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from dataclasses import dataclass, field
from typing import Any

from etlantic.lifecycle.callbacks import CallbackRegistry
from etlantic.lifecycle.middleware import MiddlewareStack
from etlantic.lifecycle.resources import ResourceManager
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
    memory: MemoryStorage = field(default_factory=MemoryStorage)
    callables: CallableStorage = field(default_factory=CallableStorage)
    _entered: bool = False

    def __post_init__(self) -> None:
        if (
            "env" not in self.secret_providers
            and "env-secrets" not in self.secret_providers
        ):
            env = EnvSecretProvider()
            self.secret_providers["env"] = env
            self.secret_providers["env-secrets"] = env
        if not self.dataframe_plugins:
            try:
                from etlantic.dataframe.discovery import (
                    discover_dataframe_plugins,
                    register_discovered_plugins,
                )

                discovered = discover_dataframe_plugins()
                self.dataframe_plugins.update(discovered)
                register_discovered_plugins(self.registry, plugins=discovered)
            except Exception as exc:
                import logging
                import warnings

                msg = f"Dataframe plugin discovery failed during runtime init: {exc}"
                logging.getLogger(__name__).warning(msg)
                warnings.warn(msg, RuntimeWarning, stacklevel=2)
        if not self.sql_plugins:
            try:
                from etlantic.sql.discovery import (
                    discover_sql_plugins,
                )
                from etlantic.sql.discovery import (
                    register_discovered_plugins as register_sql_plugins,
                )

                discovered_sql = discover_sql_plugins()
                self.sql_plugins.update(discovered_sql)
                register_sql_plugins(self.registry, plugins=discovered_sql)
            except Exception as exc:
                import logging
                import warnings

                msg = f"SQL plugin discovery failed during runtime init: {exc}"
                logging.getLogger(__name__).warning(msg)
                warnings.warn(msg, RuntimeWarning, stacklevel=2)
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
