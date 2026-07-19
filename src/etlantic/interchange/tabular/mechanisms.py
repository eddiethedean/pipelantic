"""Versioned tabular interchange mechanism vocabulary."""

from __future__ import annotations

from enum import StrEnum

SCHEMA = "etlantic.interchange/1"


class InterchangeMechanism(StrEnum):
    """Supported physical mechanisms for tabular interchange."""

    ARROW_C_DATA = "arrow_c_data"
    ARROW_C_STREAM = "arrow_c_stream"
    ARROW_IPC_STREAM = "arrow_ipc_stream"
    ARROW_IPC_FILE = "arrow_ipc_file"
    PARQUET_ARTIFACT = "parquet_artifact"
    RECORDS_FALLBACK = "records_fallback"
    NATIVE_FALLBACK = "native_fallback"
