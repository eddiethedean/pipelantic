"""Truth-table tests for tabular interchange selection."""

from __future__ import annotations

import pytest

from etlantic.capabilities import PluginCapabilities
from etlantic.interchange.tabular import (
    InterchangeMechanism,
    InterchangeSelectionError,
    select_mechanism,
)


@pytest.mark.parametrize(
    ("caps", "durable", "collecting", "expected"),
    [
        (
            {"arrow_c_stream"},
            False,
            False,
            InterchangeMechanism.ARROW_C_STREAM,
        ),
        (
            {"arrow_c_data"},
            False,
            True,
            InterchangeMechanism.ARROW_C_DATA,
        ),
        (
            {"arrow_ipc_stream", "arrow_ipc_file"},
            False,
            False,
            InterchangeMechanism.ARROW_IPC_STREAM,
        ),
        (
            {"arrow_ipc_file"},
            False,
            True,
            InterchangeMechanism.ARROW_IPC_FILE,
        ),
        (
            {"parquet_artifact", "storage"},
            True,
            False,
            InterchangeMechanism.PARQUET_ARTIFACT,
        ),
    ],
)
def test_selects_truth_table_mechanism(
    caps: set[str],
    durable: bool,
    collecting: bool,
    expected: InterchangeMechanism,
) -> None:
    mechanism, reason = select_mechanism(
        caps,
        frozenset(caps),
        durable=durable,
        already_collecting=collecting,
        pyarrow_available=True,
    )
    assert mechanism is expected
    assert reason is None


def test_pyarrow_absence_uses_explicit_native_fallback() -> None:
    caps = PluginCapabilities(
        engine="test",
        extras=frozenset({"native_fallback"}),
    )
    mechanism, reason = select_mechanism(
        caps,
        caps,
        durable=False,
        already_collecting=False,
        pyarrow_available=False,
    )
    assert mechanism is InterchangeMechanism.NATIVE_FALLBACK
    assert reason == "pyarrow_unavailable"


def test_mismatch_uses_records_with_reason() -> None:
    mechanism, reason = select_mechanism(
        {"arrow_c_stream"},
        {"arrow_c_data"},
        durable=False,
        already_collecting=False,
        pyarrow_available=True,
    )
    assert mechanism is InterchangeMechanism.RECORDS_FALLBACK
    assert reason == "no_compatible_arrow_mechanism"


def test_lossy_mapping_fails_before_selection() -> None:
    with pytest.raises(InterchangeSelectionError):
        select_mechanism(
            {"records_fallback"},
            {"records_fallback"},
            durable=False,
            already_collecting=True,
            pyarrow_available=False,
            mapping_lossy=True,
        )
