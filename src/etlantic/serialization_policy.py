"""Unsafe serialization prohibitions across loaders and plugin boundaries (0.20)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from etlantic.diagnostics import Diagnostic, Severity
from etlantic.exceptions import ETLanticError

# Formats that can construct arbitrary Python objects or execute code.
UNSAFE_SUFFIXES = frozenset(
    {
        ".pkl",
        ".pickle",
        ".joblib",
        ".npy",
        ".npz",
        ".dill",
        ".cloudpickle",
    }
)
UNSAFE_MODULE_MARKERS = frozenset(
    {
        "pickle",
        "_pickle",
        "cPickle",
        "joblib",
        "dill",
        "cloudpickle",
        "yaml.unsafe_load",
        "yaml.load",
    }
)


class UnsafeSerializationError(ETLanticError):
    """Raised when a prohibited serialization format is requested."""


def is_unsafe_path(path: str | Path) -> bool:
    """Return True when the path suffix is a prohibited executable format."""
    suffix = Path(path).suffix.casefold()
    return suffix in UNSAFE_SUFFIXES


def assert_safe_load_path(path: str | Path) -> None:
    """Refuse paths that imply unsafe deserialization."""
    if is_unsafe_path(path):
        raise UnsafeSerializationError(
            f"Refusing unsafe serialization format for path: {path}"
        )


def assert_safe_loader_name(name: str) -> None:
    """Refuse known unsafe loader/module identifiers."""
    lowered = name.strip().casefold()
    for marker in UNSAFE_MODULE_MARKERS:
        if marker.casefold() in lowered:
            raise UnsafeSerializationError(
                f"Refusing unsafe loader {name!r}; use JSON or approved text formats."
            )


def loads_json_only(text: str) -> Any:
    """Parse JSON only — never pickle/YAML object loaders."""
    return json.loads(text)


def serialization_diagnostics(path: str | Path) -> list[Diagnostic]:
    """Return diagnostics when ``path`` looks unsafe."""
    if not is_unsafe_path(path):
        return []
    return [
        Diagnostic(
            code="PMSEC060",
            severity=Severity.ERROR,
            message=f"Unsafe serialization format prohibited: {path}",
            phase="serialization",
            path=("serialization", str(path)),
            help="Use JSON, ODCS/DTCS/DPCS text, or other non-executable formats.",
        )
    ]
