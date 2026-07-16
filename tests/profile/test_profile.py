"""Profile and SecretRef tests."""

from __future__ import annotations

from pathlib import Path

from pipelantic.profile import (
    development_profile,
    load_profile,
    production_profile,
    resolve_profile,
    write_profile,
)
from pipelantic.secrets import SecretRef


def test_profile_templates() -> None:
    assert development_profile().name == "development"
    assert production_profile().security_domain == "production"
    assert resolve_profile("local").name in {"local", "development"}


def test_profile_round_trip(tmp_path: Path) -> None:
    profile = development_profile(
        name="demo",
        bindings={"customers": "csv://customers"},
        secrets={
            "token": SecretRef(provider="env-secrets", name="api", key="token"),
        },
    )
    path = write_profile(profile, tmp_path / "demo.json")
    loaded = load_profile(path)
    assert loaded.name == "demo"
    assert loaded.bindings["customers"] == "csv://customers"
    assert loaded.secrets["token"].provider == "env-secrets"


def test_secret_ref_identity() -> None:
    ref = SecretRef(provider="vault", name="db", key="password", version="v1")
    assert "vault" in ref.identity()
    assert ref.to_dict()["key"] == "password"
