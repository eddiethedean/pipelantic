"""Local storage bindings for ETLantic 0.4."""

from __future__ import annotations

from etlantic.storage.callable_binding import CallableStorage
from etlantic.storage.csv_binding import CsvStorage
from etlantic.storage.json_binding import JsonStorage
from etlantic.storage.memory import MemoryStorage
from etlantic.storage.null import NullStorage
from etlantic.storage.protocol import StorageBinding, as_records, records_to_dicts

__all__ = [
    "CallableStorage",
    "CsvStorage",
    "JsonStorage",
    "MemoryStorage",
    "NullStorage",
    "StorageBinding",
    "as_records",
    "records_to_dicts",
]
