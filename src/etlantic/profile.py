"""Execution profiles that bind logical pipelines to environments."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path
from typing import Any, Literal

from etlantic.secrets import SecretRef

PortableTransformPolicy = Literal["require", "prefer", "native"]
SecurityMode = Literal["development", "test", "production"]

_BINDINGS_REMOVED = (
    "Profile(bindings=...) was removed in ETLantic 0.16. Use assets= instead. "
    "See docs/11_DEVELOPMENT/MIGRATION_0_15_TO_0_16.md."
)
_LEGACY_BINDINGS_DIAGNOSTIC = (
    "PMCFG110: Profile JSON used legacy 'bindings'; prefer 'assets'. "
    "See docs/11_DEVELOPMENT/MIGRATION_0_18_TO_0_19.md."
)
_UNKNOWN_PROFILE = (
    "PMCFG100: Unknown profile name {name!r}. Use a built-in template "
    "(development, local, test, production), a .json path, or pass "
    "allow_adhoc_profile=True / --allow-adhoc-profile."
)


def _normalize_assets(
    *,
    assets: dict[str, str] | None,
    bindings: dict[str, str] | None = None,
    allow_legacy_bindings: bool = False,
) -> dict[str, str]:
    """Normalize public assets= into the internal asset→provider store."""
    assets_map = {str(k): str(v) for k, v in dict(assets or {}).items()}
    bindings_map = {str(k): str(v) for k, v in dict(bindings or {}).items()}
    if bindings_map and not allow_legacy_bindings:
        raise TypeError(_BINDINGS_REMOVED)
    if assets_map and bindings_map and assets_map != bindings_map:
        raise ValueError(
            "Profile assets and bindings disagree. Provide only assets=. "
            f"assets={assets_map!r} bindings={bindings_map!r}"
        )
    return assets_map or bindings_map


@dataclass(frozen=True, slots=True, init=False)
class Profile:
    """Environment binding for planning without changing logical semantics."""

    name: str
    orchestrator: str = "local"
    dataframe_engine: str | None = "local"
    sql_engine: str | None = None
    spark_engine: str | None = None
    allow_trusted_sql: bool = False
    spark_udf_policy: str = "warn"
    spark_streaming: bool = False
    # Internal store for logical asset name → provider (plan wire name: bindings).
    bindings: dict[str, str] = field(default_factory=dict)
    implementation_overrides: dict[str, str] = field(default_factory=dict)
    secret_providers: dict[str, str] = field(default_factory=dict)
    resources: dict[str, str] = field(default_factory=dict)
    secrets: dict[str, SecretRef] = field(default_factory=dict)
    security_domain: str = "default"
    security_mode: SecurityMode = "development"
    validation_policy: str = "default"
    concurrency: int | None = None
    timeout_seconds: float | None = None
    retry_max_attempts: int | None = None
    # Portable orchestration intents (0.8); Airflow-specific types stay in plugins.
    schedule: dict[str, Any] = field(default_factory=dict)
    execution: dict[str, Any] = field(default_factory=dict)
    required_sql_capabilities: tuple[str, ...] = ()
    required_spark_capabilities: tuple[str, ...] = ()
    required_orchestrator_capabilities: tuple[str, ...] = ()
    # Production plugin trust (0.9): names → optional version pins (e.g. ">=0.9,<1").
    # Empty allowlist means unrestricted in non-production profiles; production
    # profiles fail closed when allowlist is empty or a discovered plugin is absent.
    plugin_allowlist: dict[str, str | None] = field(default_factory=dict)
    # 0.12: portable vs native selection (no silent fallback).
    portable_transform_policy: PortableTransformPolicy = "prefer"
    # 0.20: safe I/O, outbound, isolation, optional capability probe.
    tenant: str = "default"
    environment: str = "default"
    safe_io: dict[str, Any] = field(default_factory=dict)
    outbound: dict[str, Any] = field(default_factory=dict)
    require_plugin_probe: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def __init__(
        self,
        name: str,
        *,
        orchestrator: str = "local",
        dataframe_engine: str | None = "local",
        sql_engine: str | None = None,
        spark_engine: str | None = None,
        allow_trusted_sql: bool = False,
        spark_udf_policy: str = "warn",
        spark_streaming: bool = False,
        assets: dict[str, str] | None = None,
        implementation_overrides: dict[str, str] | None = None,
        secret_providers: dict[str, str] | None = None,
        resources: dict[str, str] | None = None,
        secrets: dict[str, SecretRef] | None = None,
        security_domain: str = "default",
        security_mode: SecurityMode = "development",
        validation_policy: str = "default",
        concurrency: int | None = None,
        timeout_seconds: float | None = None,
        retry_max_attempts: int | None = None,
        schedule: dict[str, Any] | None = None,
        execution: dict[str, Any] | None = None,
        required_sql_capabilities: tuple[str, ...] = (),
        required_spark_capabilities: tuple[str, ...] = (),
        required_orchestrator_capabilities: tuple[str, ...] = (),
        plugin_allowlist: dict[str, str | None] | None = None,
        portable_transform_policy: PortableTransformPolicy = "prefer",
        tenant: str = "default",
        environment: str = "default",
        safe_io: dict[str, Any] | None = None,
        outbound: dict[str, Any] | None = None,
        require_plugin_probe: bool = False,
        metadata: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        if "bindings" in kwargs:
            raise TypeError(_BINDINGS_REMOVED)
        store = _normalize_assets(assets=assets)
        mode = _parse_security_mode(security_mode)
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "orchestrator", orchestrator)
        object.__setattr__(self, "dataframe_engine", dataframe_engine)
        object.__setattr__(self, "sql_engine", sql_engine)
        object.__setattr__(self, "spark_engine", spark_engine)
        object.__setattr__(self, "allow_trusted_sql", allow_trusted_sql)
        object.__setattr__(self, "spark_udf_policy", spark_udf_policy)
        object.__setattr__(self, "spark_streaming", spark_streaming)
        object.__setattr__(self, "bindings", store)
        object.__setattr__(
            self, "implementation_overrides", dict(implementation_overrides or {})
        )
        object.__setattr__(self, "secret_providers", dict(secret_providers or {}))
        object.__setattr__(self, "resources", dict(resources or {}))
        object.__setattr__(self, "secrets", dict(secrets or {}))
        object.__setattr__(self, "security_domain", security_domain)
        object.__setattr__(self, "security_mode", mode)
        object.__setattr__(self, "validation_policy", validation_policy)
        object.__setattr__(self, "concurrency", concurrency)
        object.__setattr__(self, "timeout_seconds", timeout_seconds)
        object.__setattr__(self, "retry_max_attempts", retry_max_attempts)
        object.__setattr__(self, "schedule", dict(schedule or {}))
        object.__setattr__(self, "execution", dict(execution or {}))
        object.__setattr__(
            self, "required_sql_capabilities", tuple(required_sql_capabilities)
        )
        object.__setattr__(
            self, "required_spark_capabilities", tuple(required_spark_capabilities)
        )
        object.__setattr__(
            self,
            "required_orchestrator_capabilities",
            tuple(required_orchestrator_capabilities),
        )
        object.__setattr__(self, "plugin_allowlist", dict(plugin_allowlist or {}))
        object.__setattr__(self, "portable_transform_policy", portable_transform_policy)
        object.__setattr__(self, "tenant", str(tenant or "default"))
        object.__setattr__(self, "environment", str(environment or "default"))
        object.__setattr__(self, "safe_io", dict(safe_io or {}))
        object.__setattr__(self, "outbound", dict(outbound or {}))
        object.__setattr__(self, "require_plugin_probe", bool(require_plugin_probe))
        object.__setattr__(self, "metadata", dict(metadata or {}))

    @property
    def assets(self) -> dict[str, str]:
        """Preferred public view of logical asset → provider resolution."""
        return dict(self.bindings)

    def identity(self) -> str:
        """Stable profile identity."""
        return f"profile:{self.name}"

    def to_dict(self) -> dict[str, Any]:
        """Serialize profile for public JSON (assets only; no mirrored bindings)."""
        data = asdict(self)
        data["secrets"] = {
            key: ref.to_dict() if isinstance(ref, SecretRef) else ref
            for key, ref in self.secrets.items()
        }
        data["assets"] = dict(self.bindings)
        data.pop("bindings", None)
        for key in (
            "required_sql_capabilities",
            "required_spark_capabilities",
            "required_orchestrator_capabilities",
        ):
            if key in data and isinstance(data[key], tuple):
                data[key] = list(data[key])
        return data

    def to_plan_snapshot(self) -> dict[str, Any]:
        """Fingerprint-stable snapshot retaining the plan wire ``bindings`` shape."""
        data = asdict(self)
        data["secrets"] = {
            key: ref.to_dict() if isinstance(ref, SecretRef) else ref
            for key, ref in self.secrets.items()
        }
        # Intentionally omit ``assets`` so equivalent plans keep fingerprints.
        data["bindings"] = dict(self.bindings)
        return data

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
        *,
        accept_legacy_bindings: bool = True,
    ) -> Profile:
        """Deserialize a profile mapping.

        Accepts legacy JSON ``bindings`` keys for one-time loading of saved
        profiles; new writes via :meth:`to_dict` emit ``assets`` only. Legacy
        ``bindings`` loads emit diagnostic ``PMCFG110`` (and raise when
        ``accept_legacy_bindings`` is False).
        """
        import warnings

        secrets_raw = data.get("secrets") or {}
        if not isinstance(secrets_raw, dict):
            raise ValueError("Profile secrets must be a mapping of name → SecretRef")
        secrets: dict[str, SecretRef] = {}
        for key, value in secrets_raw.items():
            if isinstance(value, SecretRef):
                secrets[str(key)] = value
            elif isinstance(value, dict):
                secrets[str(key)] = SecretRef.from_dict(value)
            else:
                raise ValueError(
                    f"Profile secret {key!r} must be a SecretRef mapping, "
                    "not a plaintext value"
                )
        has_assets = "assets" in data and data.get("assets") is not None
        has_bindings = "bindings" in data and data.get("bindings") is not None
        if has_bindings and not has_assets:
            if not accept_legacy_bindings:
                raise ValueError(_LEGACY_BINDINGS_DIAGNOSTIC)
            warnings.warn(_LEGACY_BINDINGS_DIAGNOSTIC, UserWarning, stacklevel=2)
        store = _normalize_assets(
            assets=dict(data.get("assets") or {}) if has_assets else None,
            bindings=dict(data.get("bindings") or {}) if has_bindings else None,
            allow_legacy_bindings=True,
        )
        security_mode = data.get("security_mode")
        if security_mode is None:
            security_mode = _infer_security_mode(
                name=str(data.get("name") or ""),
                security_domain=str(data.get("security_domain") or "default"),
            )
        return cls(
            name=str(data["name"]),
            orchestrator=str(data.get("orchestrator") or "local"),
            dataframe_engine=data.get("dataframe_engine", "local"),
            sql_engine=data.get("sql_engine"),
            spark_engine=data.get("spark_engine"),
            allow_trusted_sql=bool(data.get("allow_trusted_sql", False)),
            spark_udf_policy=str(data.get("spark_udf_policy") or "warn"),
            spark_streaming=bool(data.get("spark_streaming", False)),
            assets=store,
            implementation_overrides=dict(data.get("implementation_overrides") or {}),
            secret_providers=dict(data.get("secret_providers") or {}),
            resources=dict(data.get("resources") or {}),
            secrets=secrets,
            security_domain=str(data.get("security_domain") or "default"),
            security_mode=_parse_security_mode(security_mode),
            validation_policy=str(data.get("validation_policy") or "default"),
            concurrency=data.get("concurrency"),
            timeout_seconds=data.get("timeout_seconds"),
            retry_max_attempts=data.get("retry_max_attempts"),
            schedule=dict(data.get("schedule") or {}),
            execution=dict(data.get("execution") or {}),
            required_sql_capabilities=_as_str_tuple(
                data.get("required_sql_capabilities")
            ),
            required_spark_capabilities=_as_str_tuple(
                data.get("required_spark_capabilities")
            ),
            required_orchestrator_capabilities=_as_str_tuple(
                data.get("required_orchestrator_capabilities")
            ),
            plugin_allowlist={
                str(k): (None if v in (None, "") else str(v))
                for k, v in dict(data.get("plugin_allowlist") or {}).items()
            },
            portable_transform_policy=_parse_portable_policy(
                data.get("portable_transform_policy")
            ),
            tenant=str(data.get("tenant") or "default"),
            environment=str(data.get("environment") or "default"),
            safe_io=dict(data.get("safe_io") or {}),
            outbound=dict(data.get("outbound") or {}),
            require_plugin_probe=bool(data.get("require_plugin_probe", False)),
            metadata=_validated_profile_metadata(data.get("metadata") or {}),
        )

    def with_updates(self, **kwargs: Any) -> Profile:
        """Return a copy with selected fields replaced.

        Unknown keys raise ``TypeError`` so typos like ``plugin_allow_list``
        cannot silently leave production allowlists empty. ``assets`` is the
        public authoring key for the internal bindings store.
        """
        known = {f.name for f in fields(self)} | {"assets"}
        # Reject public bindings= authoring; internal snapshot still uses bindings.
        if "bindings" in kwargs:
            raise TypeError(_BINDINGS_REMOVED)
        unknown = sorted(set(kwargs) - known)
        if unknown:
            raise TypeError(
                f"Profile.with_updates() got unexpected field(s): {', '.join(unknown)}"
            )
        current = self.to_plan_snapshot()
        if "assets" in kwargs:
            current["bindings"] = dict(kwargs.pop("assets") or {})
        # Internal snapshot uses plan-wire ``bindings``; map to assets so
        # from_dict does not emit legacy PMCFG110 for authoring round-trips.
        if "bindings" in current and "assets" not in current:
            current["assets"] = dict(current.pop("bindings") or {})
        current.update(kwargs)
        return Profile.from_dict(current)


def _validated_profile_metadata(raw: Any) -> dict[str, Any]:
    """Copy profile metadata and enforce extension size/depth budgets."""
    from etlantic.extensions import validate_extension_metadata

    metadata = dict(raw or {})
    validate_extension_metadata(metadata, path="metadata", strict=False)
    return metadata


def _as_str_tuple(value: Any) -> tuple[str, ...]:
    """Normalize capability lists without iterating bare strings by character."""
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    return tuple(str(x) for x in value)


def _parse_portable_policy(value: Any) -> PortableTransformPolicy:
    policy = str(value or "prefer")
    if policy not in {"require", "prefer", "native"}:
        raise ValueError(
            f"portable_transform_policy must be require|prefer|native, got {policy!r}"
        )
    return policy  # type: ignore[return-value]


def _parse_security_mode(value: Any) -> SecurityMode:
    mode = str(value or "development").strip().lower()
    if mode not in {"development", "test", "production"}:
        raise ValueError(
            f"security_mode must be development|test|production, got {value!r}"
        )
    return mode  # type: ignore[return-value]


def _infer_security_mode(*, name: str, security_domain: str) -> SecurityMode:
    """Best-effort inference for pre-0.19 profile JSON missing security_mode."""
    key = name.strip().lower()
    domain = security_domain.strip().lower()
    if key in {"production", "prod", "staging"} or domain in {"production", "prod"}:
        return "production"
    if key == "test" or domain == "test":
        return "test"
    return "development"


def development_profile(**overrides: Any) -> Profile:
    """Built-in development profile template."""
    base = Profile(
        name="development",
        orchestrator="local",
        dataframe_engine="local",
        security_domain="dev",
        security_mode="development",
        validation_policy="default",
    )
    return base.with_updates(**overrides) if overrides else base


def test_profile(**overrides: Any) -> Profile:
    """Built-in test profile template."""
    base = Profile(
        name="test",
        orchestrator="local",
        dataframe_engine="local",
        security_domain="test",
        security_mode="test",
        validation_policy="strict",
    )
    return base.with_updates(**overrides) if overrides else base


def production_profile(**overrides: Any) -> Profile:
    """Built-in production profile template."""
    base = Profile(
        name="production",
        orchestrator="local",
        dataframe_engine="local",
        security_domain="production",
        security_mode="production",
        validation_policy="strict",
    )
    return base.with_updates(**overrides) if overrides else base


PROFILE_TEMPLATES: dict[str, Profile] = {
    "development": development_profile(),
    "dev": development_profile(),
    "local": development_profile(name="local"),
    "test": test_profile(),
    "production": production_profile(),
    "prod": production_profile(),
}


def resolve_profile(
    profile: str | Profile | None,
    *,
    allow_adhoc_profile: bool = False,
) -> Profile:
    """Resolve a profile name, JSON path, or object to a concrete Profile.

    When ``profile`` is a string ending in ``.json`` that exists as a file,
    the profile is loaded with :func:`load_profile`. Built-in template names
    (``development``, ``production``, …) resolve to templates. Other bare
    names fail closed unless ``allow_adhoc_profile`` is True.
    """
    if profile is None:
        return development_profile(name="local")
    if isinstance(profile, Profile):
        return profile
    key = str(profile)
    path = Path(key)
    if path.suffix.casefold() == ".json":
        if not path.is_file():
            raise FileNotFoundError(f"Profile JSON path not found: {path}")
        return load_profile(path)
    if key in PROFILE_TEMPLATES:
        return PROFILE_TEMPLATES[key]
    if allow_adhoc_profile:
        return Profile(name=key, security_mode="development")
    raise ValueError(_UNKNOWN_PROFILE.format(name=key))


def write_profile(profile: Profile, path: str | Path) -> Path:
    """Write a profile as JSON through SafeIoPolicy when a parent root exists."""
    from etlantic.io_policy import SafeIoPolicy, write_text_safe

    resolved = Path(path).expanduser()
    parent = resolved.parent
    parent.mkdir(parents=True, exist_ok=True)
    policy = SafeIoPolicy.for_root(parent)
    text = json.dumps(profile.to_dict(), indent=2, sort_keys=True) + "\n"
    write_text_safe(resolved, text, policy, run_id="profile-write")
    return resolved.resolve()


def load_profile(path: str | Path) -> Profile:
    """Load a profile from a JSON file."""
    from etlantic.interchange.security import read_text_bounded

    _resolved, text = read_text_bounded(path)
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("Profile document must be a JSON object")
    return Profile.from_dict(data)
