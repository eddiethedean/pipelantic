"""SQL / Spark / Delta / write-policy compatibility mappings."""

from __future__ import annotations

from typing import Any

from etlantic.capabilities import PluginCapabilities
from etlantic.diagnostics import Diagnostic, Severity
from etlantic.reliability import WriteMode

# SparkForge write vocabulary → ETLantic WriteMode
_WRITE_MODE_MAP: dict[str, WriteMode] = {
    "append": WriteMode.APPEND,
    "overwrite": WriteMode.OVERWRITE,
    "overwrite_partitions": WriteMode.OVERWRITE,
    "merge": WriteMode.MERGE,
    "upsert": WriteMode.UPSERT,
    "no_write": WriteMode.NO_WRITE,
    "skip": WriteMode.NO_WRITE,
    "none": WriteMode.NO_WRITE,
    "": WriteMode.OVERWRITE,
}

# Delta operations require spark_delta (and related) capabilities.
_DELTA_CAPABILITY: dict[str, str] = {
    "merge": "spark_delta",
    "optimize": "spark_delta",
    "vacuum": "spark_delta",
    "history": "spark_delta",
    "time_travel": "spark_delta",
}


def write_mode_from_sparkforge(raw: str | None) -> WriteMode:
    """Map a SparkForge write-mode string to ETLantic WriteMode."""
    key = (raw or "overwrite").strip().lower()
    if key not in _WRITE_MODE_MAP:
        raise ValueError(f"Unsupported SparkForge write mode: {raw!r}")
    return _WRITE_MODE_MAP[key]


def retry_policy_from_sparkforge(raw: dict[str, Any] | None) -> dict[str, Any]:
    """Normalize SparkForge retry config into portable intent metadata."""
    data = dict(raw or {})
    return {
        "max_attempts": int(data.get("max_attempts") or data.get("retries") or 1),
        "retry_delay_seconds": float(
            data.get("retry_delay_seconds") or data.get("delay") or 0.0
        ),
        "retry_safe": bool(data.get("retry_safe", True)),
    }


def assert_delta_capabilities(
    operations: list[str],
    *,
    capabilities: PluginCapabilities | None = None,
) -> list[Diagnostic]:
    """Fail closed when declared Delta ops are unsupported by capabilities.

    When ``capabilities`` is None (planning without a live plugin), require
    that operations are listed but emit errors — callers must supply a plugin
    that supports ``spark_delta`` before execution.
    """
    diagnostics: list[Diagnostic] = []
    for op in operations:
        key = op.strip().lower()
        required = _DELTA_CAPABILITY.get(key)
        if required is None:
            diagnostics.append(
                Diagnostic(
                    code="PMSF321",
                    severity=Severity.ERROR,
                    message=f"Unknown Delta operation {op!r}.",
                    path=("delta_operations", op),
                    phase="sparkforge_adapter",
                )
            )
            continue
        if capabilities is None:
            diagnostics.append(
                Diagnostic(
                    code="PMSF322",
                    severity=Severity.ERROR,
                    message=(
                        f"Delta operation {op!r} requires capability {required!r}; "
                        "no Spark plugin capabilities were supplied (fail closed)."
                    ),
                    path=("delta_operations", op),
                    phase="sparkforge_adapter",
                )
            )
            continue
        if not capabilities.supports(required):
            diagnostics.append(
                Diagnostic(
                    code="PMSF323",
                    severity=Severity.ERROR,
                    message=(
                        f"Delta operation {op!r} requires capability {required!r} "
                        "which the selected Spark plugin does not declare."
                    ),
                    path=("delta_operations", op),
                    phase="sparkforge_adapter",
                )
            )
    return diagnostics


COMPATIBILITY_MATRIX: dict[str, dict[str, str]] = {
    "write": {k: v.value for k, v in _WRITE_MODE_MAP.items() if k},
    "delta": dict(_DELTA_CAPABILITY),
    "engines": {
        "spark": "Profile.spark_engine=pyspark",
        "pyspark": "Profile.spark_engine=pyspark",
        "sql": "Profile.sql_engine=sql",
        "delta": "Profile.spark_engine=pyspark + spark_delta capability",
    },
}
