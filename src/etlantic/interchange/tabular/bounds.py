"""Resource bounds for local tabular interchange."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class InterchangeBounds:
    """Initial Gate A batching and buffering limits."""

    max_batch_rows: int = 65_536
    max_in_flight_batches: int = 2
    max_buffered_bytes: int = 64 * 1024 * 1024
