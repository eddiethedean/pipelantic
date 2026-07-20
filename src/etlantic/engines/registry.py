"""Central engine family registry and priority resolution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from etlantic.engines.protocol import EngineFamily
from etlantic.profile import Profile


@dataclass(frozen=True, slots=True)
class _BuiltinFamily:
    name: str
    aliases: frozenset[str]
    entry_point_group: str | None
    capability_defaults: tuple[str, ...] = ()

    def matches(self, engine: str) -> bool:
        return engine in self.aliases

    def default_capabilities(self, profile: Profile) -> list[str]:
        caps = list(self.capability_defaults)
        if self.name == "sql":
            caps.extend(profile.required_sql_capabilities)
        elif self.name == "spark":
            caps.extend(profile.required_spark_capabilities)
            if profile.spark_streaming:
                caps.extend(["streaming", "spark_streaming"])
        elif self.name == "dataframe":
            engine = profile.dataframe_engine or "local"
            if engine == "polars":
                caps.append("lazy")
        return caps


_LOCAL = _BuiltinFamily("local", frozenset({"local", "null"}), None, ())
_DATAFRAME = _BuiltinFamily(
    "dataframe",
    frozenset({"polars", "pandas"}),
    "etlantic.dataframe_plugins",
    ("dataframe", "eager"),
)
_SQL = _BuiltinFamily(
    "sql",
    frozenset({"sql"}),
    "etlantic.sql_plugins",
    ("sql", "transactions", "sql_catalog_inspect"),
)
_SPARK = _BuiltinFamily(
    "spark",
    frozenset({"pyspark", "spark"}),
    "etlantic.spark_plugins",
    ("spark", "lazy", "schema_inspection"),
)

_BUILTIN_FAMILIES: tuple[_BuiltinFamily, ...] = (
    _LOCAL,
    _DATAFRAME,
    _SQL,
    _SPARK,
)

# spark → sql → dataframe/local (single priority implementation)
_PRIORITY: tuple[_BuiltinFamily, ...] = (_SPARK, _SQL, _DATAFRAME, _LOCAL)


class EngineRegistry:
    """Resolve engine families and profile-primary engines."""

    def __init__(self, families: tuple[EngineFamily, ...] | None = None) -> None:
        self._families = families or _BUILTIN_FAMILIES

    def resolve_family(self, engine: str) -> EngineFamily | None:
        for family in self._families:
            if family.matches(engine):
                return family
        return None

    def primary_family(self, profile: Profile) -> EngineFamily:
        if profile.spark_engine:
            return _SPARK
        if profile.sql_engine:
            return _SQL
        return (
            _DATAFRAME if (profile.dataframe_engine or "local") != "local" else _LOCAL
        )

    def primary_engine(self, profile: Profile) -> str:
        if profile.spark_engine:
            return profile.spark_engine
        if profile.sql_engine:
            return profile.sql_engine
        return profile.dataframe_engine or "local"

    def primary_engine_field(self, profile: Profile) -> str:
        if profile.spark_engine:
            return "spark_engine"
        if profile.sql_engine:
            return "sql_engine"
        return "dataframe_engine"

    def default_capabilities(self, profile: Profile) -> list[str]:
        return self.primary_family(profile).default_capabilities(profile)

    def is_dataframe_engine(
        self,
        engine: str,
        engines: dict[str, Any] | None = None,
    ) -> bool:
        from etlantic.capabilities import PluginCapabilities
        from etlantic.dataframe.protocol import DATAFRAME_ENGINES

        capabilities = (engines or {}).get(engine)
        if isinstance(capabilities, PluginCapabilities) and capabilities.dataframe:
            return True
        if capabilities is not None and getattr(capabilities, "dataframe", False):
            return True
        return engine in DATAFRAME_ENGINES

    def is_sql_engine(self, engine: str) -> bool:
        from etlantic.sql.protocol import SQL_ENGINES

        return engine in SQL_ENGINES

    def is_spark_engine(self, engine: str) -> bool:
        from etlantic.spark.protocol import SPARK_ENGINES

        return engine in SPARK_ENGINES

    def normalize_spark_alias(self, engine: str) -> str:
        if engine == "spark":
            return "pyspark"
        return engine


_DEFAULT_REGISTRY = EngineRegistry()


def get_engine_registry() -> EngineRegistry:
    return _DEFAULT_REGISTRY
