"""Plugin allowlist / version-pin enforcement (0.9)."""

from __future__ import annotations

from typing import Any

from packaging.specifiers import InvalidSpecifier, SpecifierSet
from packaging.version import InvalidVersion, Version

from etlantic.diagnostics import Diagnostic, Severity
from etlantic.profile import Profile


def _is_production_profile(profile: Profile) -> bool:
    name = profile.name.lower()
    if name in {"production", "prod", "staging"}:
        return True
    domain = (profile.security_domain or "").lower()
    return domain in {"production", "prod"}


def plugin_allowed(
    *,
    name: str,
    version: str | None,
    allowlist: dict[str, str | None],
) -> bool:
    """Return True when ``name`` is permitted by ``allowlist`` (and pin)."""
    if name not in allowlist:
        return False
    pin = allowlist.get(name)
    if pin is None or pin == "":
        return True
    if version is None:
        return False
    try:
        return Version(version) in SpecifierSet(pin)
    except (InvalidVersion, InvalidSpecifier):
        return False


def filter_plugins_by_allowlist(
    plugins: dict[str, Any],
    profile: Profile,
    *,
    name_attr: str = "name",
    version_attr: str = "version",
) -> tuple[dict[str, Any], list[Diagnostic]]:
    """Filter discovered plugins using profile allowlist.

    Production profiles fail closed when the allowlist is empty or a plugin is
    not listed / does not match the version pin. Non-production profiles with an
    empty allowlist remain unrestricted.
    """
    allowlist = dict(profile.plugin_allowlist or {})
    production = _is_production_profile(profile)
    diagnostics: list[Diagnostic] = []

    if not allowlist:
        if production:
            diagnostics.append(
                Diagnostic(
                    code="PMPLUG401",
                    severity=Severity.ERROR,
                    message=(
                        f"Production profile {profile.name!r} requires a non-empty "
                        "plugin_allowlist; rejecting all discovered plugins."
                    ),
                    path=("profile", "plugin_allowlist"),
                    phase="plugin_trust",
                )
            )
            return {}, diagnostics
        return dict(plugins), diagnostics

    kept: dict[str, Any] = {}
    for key, plugin in plugins.items():
        info = getattr(plugin, "info", None)
        pname = (
            getattr(info, name_attr, None)
            or getattr(info, "engine", None)
            or getattr(plugin, name_attr, None)
            or key
        )
        pversion = (
            getattr(info, version_attr, None)
            or getattr(plugin, version_attr, None)
            or None
        )
        if plugin_allowed(
            name=str(pname), version=pversion, allowlist=allowlist
        ) or plugin_allowed(name=str(key), version=pversion, allowlist=allowlist):
            kept[key] = plugin
        else:
            diagnostics.append(
                Diagnostic(
                    code="PMPLUG402",
                    severity=Severity.ERROR if production else Severity.WARNING,
                    message=(
                        f"Plugin {pname!r} (version={pversion!r}) is not permitted "
                        f"by profile {profile.name!r} plugin_allowlist."
                    ),
                    path=("plugin", str(pname)),
                    phase="plugin_trust",
                )
            )
    return kept, diagnostics


def assert_plugin_trust(
    plugins: dict[str, Any],
    profile: Profile,
) -> dict[str, Any]:
    """Filter plugins and raise when production trust fails closed."""
    from etlantic.exceptions import ETLanticError

    kept, diagnostics = filter_plugins_by_allowlist(plugins, profile)
    errors = [d for d in diagnostics if d.severity is Severity.ERROR]
    if errors:
        raise ETLanticError(
            "; ".join(d.message for d in errors),
        )
    return kept
