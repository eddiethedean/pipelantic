"""Scoped registries for plugins, implementations, bindings, and providers.

Registries belong to a PlanningContext instance (ADR-004), never process globals.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from etlantic.capabilities import PluginCapabilities
from etlantic.profile import Profile, resolve_profile
from etlantic.secrets import SecretRef


@dataclass(frozen=True, slots=True)
class PluginDescriptor:
    """Installed plugin metadata for planning (no live handles)."""

    name: str
    kind: str
    version: str = "0.0.0"
    engine: str | None = None
    capabilities: PluginCapabilities | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize plugin descriptor."""
        return {
            "name": self.name,
            "kind": self.kind,
            "version": self.version,
            "engine": self.engine,
            "capabilities": (
                self.capabilities.to_dict() if self.capabilities else None
            ),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class ImplementationDescriptor:
    """Resolved implementation selection for a transformation/engine."""

    transformation_id: str
    engine: str
    identity: str
    is_async: bool = False
    kind: str = "native"  # "native" | "portable_compiled"
    ir_fingerprint: str | None = None
    compiler_name: str | None = None
    compiler_version: str | None = None
    compiler_protocol: str | None = None
    requirements: dict[str, list[str]] = field(default_factory=dict)
    support_summary: dict[str, Any] = field(default_factory=dict)
    fallback_reason: str | None = None
    # Bounded canonical dtcs.transform-plan/2 (data-only); never live objects.
    portable_plan: dict[str, Any] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize implementation descriptor."""
        return {
            "transformation_id": self.transformation_id,
            "engine": self.engine,
            "identity": self.identity,
            "is_async": self.is_async,
            "kind": self.kind,
            "ir_fingerprint": self.ir_fingerprint,
            "compiler_name": self.compiler_name,
            "compiler_version": self.compiler_version,
            "compiler_protocol": self.compiler_protocol,
            "requirements": {
                key: list(values) for key, values in self.requirements.items()
            },
            "support_summary": dict(self.support_summary),
            "fallback_reason": self.fallback_reason,
            "portable_plan": dict(self.portable_plan) if self.portable_plan else None,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ImplementationDescriptor:
        """Deserialize implementation descriptor."""
        requirements_raw = data.get("requirements") or {}
        return cls(
            transformation_id=str(data["transformation_id"]),
            engine=str(data["engine"]),
            identity=str(data["identity"]),
            is_async=bool(data.get("is_async", False)),
            kind=str(data.get("kind") or "native"),
            ir_fingerprint=data.get("ir_fingerprint"),
            compiler_name=data.get("compiler_name"),
            compiler_version=data.get("compiler_version"),
            compiler_protocol=data.get("compiler_protocol"),
            requirements={
                str(k): [str(x) for x in (v or [])]
                for k, v in dict(requirements_raw).items()
            },
            support_summary=dict(data.get("support_summary") or {}),
            fallback_reason=data.get("fallback_reason"),
            portable_plan=(
                dict(data["portable_plan"])
                if isinstance(data.get("portable_plan"), dict)
                else None
            ),
            metadata=dict(data.get("metadata") or {}),
        )


@dataclass(frozen=True, slots=True)
class BindingDescriptor:
    """Logical binding resolved to a provider descriptor (not credentials)."""

    binding: str
    provider: str
    kind: str = "resource"
    location: str | None = None
    secret_ref: SecretRef | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize binding descriptor."""
        return {
            "binding": self.binding,
            "provider": self.provider,
            "kind": self.kind,
            "location": self.location,
            "secret_ref": self.secret_ref.to_dict() if self.secret_ref else None,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BindingDescriptor:
        """Deserialize binding descriptor."""
        secret_raw = data.get("secret_ref")
        return cls(
            binding=str(data["binding"]),
            provider=str(data["provider"]),
            kind=str(data.get("kind") or "resource"),
            location=data.get("location"),
            secret_ref=(
                SecretRef.from_dict(secret_raw)
                if isinstance(secret_raw, dict)
                else None
            ),
            metadata=dict(data.get("metadata") or {}),
        )


@dataclass
class RegistryBundle:
    """Mutable, scoped registries used during planning."""

    plugins: dict[str, PluginDescriptor] = field(default_factory=dict)
    implementations: dict[str, ImplementationDescriptor] = field(default_factory=dict)
    bindings: dict[str, BindingDescriptor] = field(default_factory=dict)
    secret_providers: dict[str, PluginDescriptor] = field(default_factory=dict)
    engines: dict[str, PluginCapabilities] = field(default_factory=dict)

    def register_plugin(self, descriptor: PluginDescriptor) -> None:
        """Register a plugin descriptor."""
        self.plugins[descriptor.name] = descriptor
        if descriptor.capabilities is not None and descriptor.engine:
            self.engines[descriptor.engine] = descriptor.capabilities
        if descriptor.kind == "secret_provider":
            self.secret_providers[descriptor.name] = descriptor

    def register_binding(self, descriptor: BindingDescriptor) -> None:
        """Register a binding descriptor."""
        self.bindings[descriptor.binding] = descriptor

    def register_implementation(self, descriptor: ImplementationDescriptor) -> None:
        """Register an implementation descriptor keyed by transform+engine."""
        key = f"{descriptor.transformation_id}::{descriptor.engine}"
        self.implementations[key] = descriptor


def builtin_stub_registry() -> RegistryBundle:
    """Return a registry with in-tree stub plugins for local planning tests.

    ``local`` is the in-process Python-records path (not a dataframe engine).
    Polars/Pandas plugins register themselves via entry points or explicit
    ``register_plugin`` calls when installed.
    """
    registry = RegistryBundle()
    local_caps = PluginCapabilities(
        engine="local",
        async_execution=True,
        dataframe=False,
        eager=True,
        lazy=False,
        schema_inspection=True,
        cancellation=True,
        extras=frozenset({"python", "records"}),
    )
    null_caps = PluginCapabilities(
        engine="null",
        dataframe=False,
        eager=True,
        extras=frozenset({"noop"}),
    )
    registry.register_plugin(
        PluginDescriptor(
            name="local",
            kind="runtime",
            version="0.20.0",
            engine="local",
            capabilities=local_caps,
        )
    )
    registry.register_plugin(
        PluginDescriptor(
            name="null",
            kind="runtime",
            version="0.20.0",
            engine="null",
            capabilities=null_caps,
        )
    )
    registry.register_plugin(
        PluginDescriptor(
            name="env-secrets",
            kind="secret_provider",
            version="0.20.0",
            engine="env",
            capabilities=PluginCapabilities(
                engine="env",
                secret_provider=True,
                dataframe=False,
                eager=False,
            ),
        )
    )
    return registry


@dataclass
class PlanningContext:
    """Scoped planning inputs: profile + registries (no live resources)."""

    profile: Profile
    registry: RegistryBundle = field(default_factory=builtin_stub_registry)
    required_capabilities: list[str] = field(default_factory=list)
    allow_capability_fallback: bool = False
    fallback_engine: str | None = "null"
    selection: dict[str, Any] = field(default_factory=dict)
    plugin_trust_records: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        profile: str | Profile | None = None,
        *,
        registry: RegistryBundle | None = None,
        required_capabilities: list[str] | None = None,
        allow_capability_fallback: bool = False,
        allow_adhoc_profile: bool = False,
    ) -> PlanningContext:
        """Build a planning context from a profile name/object.

        When ``dataframe_engine`` is ``polars`` or ``pandas`` and no custom
        registry is supplied, discovered entry-point plugins are registered
        onto a stub registry so plan-only paths work without a runtime.
        When ``sql_engine`` is ``sql``, discovered SQL plugins are registered
        the same way. When ``spark_engine`` is ``pyspark``/``spark``,
        discovered Spark plugins are registered the same way.
        """
        resolved = (
            profile
            if isinstance(profile, Profile)
            else resolve_profile(profile, allow_adhoc_profile=allow_adhoc_profile)
        )
        caps = list(required_capabilities) if required_capabilities is not None else []
        engine = resolved.dataframe_engine or "local"
        sql_engine = resolved.sql_engine
        spark_engine = resolved.spark_engine
        if not caps and engine in {"polars", "pandas"}:
            caps = ["dataframe", "eager"]
            if engine == "polars":
                caps.append("lazy")
        if not caps and sql_engine == "sql":
            caps = ["sql", "transactions", "sql_catalog_inspect"]
            caps.extend(resolved.required_sql_capabilities)
        if not caps and spark_engine in {"pyspark", "spark"}:
            caps = ["spark", "lazy", "schema_inspection"]
            caps.extend(resolved.required_spark_capabilities)
            if resolved.spark_streaming:
                caps.extend(["streaming", "spark_streaming"])
        reg = registry
        trust_records: list[dict[str, Any]] = []
        if reg is None:
            reg = builtin_stub_registry()
            from etlantic.plugin_lifecycle import discover_evaluate_authorize_load

            if engine in {"polars", "pandas"}:
                from etlantic.dataframe.discovery import (
                    DATAFRAME_PLUGIN_ENTRY_POINT,
                    register_discovered_plugins,
                )

                result = discover_evaluate_authorize_load(
                    DATAFRAME_PLUGIN_ENTRY_POINT, profile=resolved
                )
                trust_records.extend(result.trust_records)
                register_discovered_plugins(
                    reg, plugins=result.loaded, profile=resolved
                )
            if sql_engine == "sql":
                from etlantic.sql.discovery import (
                    SQL_PLUGIN_ENTRY_POINT,
                )
                from etlantic.sql.discovery import (
                    register_discovered_plugins as register_sql,
                )

                result = discover_evaluate_authorize_load(
                    SQL_PLUGIN_ENTRY_POINT, profile=resolved
                )
                trust_records.extend(result.trust_records)
                register_sql(reg, plugins=result.loaded, profile=resolved)
            if spark_engine in {"pyspark", "spark"}:
                from etlantic.spark.discovery import (
                    SPARK_PLUGIN_ENTRY_POINT,
                )
                from etlantic.spark.discovery import (
                    register_discovered_plugins as register_spark,
                )

                result = discover_evaluate_authorize_load(
                    SPARK_PLUGIN_ENTRY_POINT, profile=resolved
                )
                trust_records.extend(result.trust_records)
                register_spark(reg, plugins=result.loaded, profile=resolved)
            if engine in {"polars", "pandas"} or spark_engine in {"pyspark", "spark"}:
                from etlantic.transform.discovery import (
                    TRANSFORM_COMPILER_ENTRY_POINT,
                    register_discovered_compilers,
                )
                from etlantic.transform.discovery import (
                    _key as transform_key,
                )

                result = discover_evaluate_authorize_load(
                    TRANSFORM_COMPILER_ENTRY_POINT,
                    profile=resolved,
                    key_fn=transform_key,
                )
                trust_records.extend(result.trust_records)
                register_discovered_compilers(
                    reg, compilers=result.loaded, profile=resolved
                )
        return cls(
            profile=resolved,
            registry=reg,
            required_capabilities=caps,
            allow_capability_fallback=allow_capability_fallback,
            plugin_trust_records=trust_records,
        )
