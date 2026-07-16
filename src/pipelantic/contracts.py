"""Data-contract integration boundary for ContractModel.

``Data`` is Pipelantic's thin public facade over ContractModel (DD-010A).
ContractModel retains authority for data-contract semantics and ODCS.
``DataContractModel`` remains as a deprecated compatibility alias.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, TypeAlias

from contractmodel import ContractModel

# Preferred public facade (DD-010A): thin alias, not a new implementation.
Data: TypeAlias = ContractModel
# Compatibility alias (prefer ``Data``). Deprecation is emitted from the
# package root ``pipelantic.__getattr__``.
DataContractModel: TypeAlias = Data

__all__ = [
    "ContractModel",
    "Data",
    "DataContractModel",
    "is_data_contract_type",
    "load_data_contract",
    "resolve_contract_type",
    "write_odcs",
]


def is_data_contract_type(obj: Any) -> bool:
    """Return True when ``obj`` is a ContractModel-compatible data-contract class."""
    return isinstance(obj, type) and issubclass(obj, ContractModel)


def resolve_contract_type(annotation: Any) -> type[Any] | None:
    """Extract a data-contract class from a type annotation when possible.

    Returns ``None`` when the annotation is not a concrete ContractModel subclass.
    """
    if is_data_contract_type(annotation):
        return annotation
    origin = getattr(annotation, "__origin__", None)
    if origin is not None:
        args = getattr(annotation, "__args__", ())
        if len(args) == 1 and is_data_contract_type(args[0]):
            return args[0]
    return None


def load_data_contract(
    path: str | Path,
    *,
    root: str | Path | None = None,
    class_name: str | None = None,
) -> type[Data]:
    """Load an ODCS artifact into a ``Data`` (ContractModel) subclass."""
    from pipelantic.interchange.odcs import load_data_contract as _load

    return _load(path, root=root, class_name=class_name)


def write_odcs(
    model: type[Data],
    path: str | Path,
    *,
    root: str | Path | None = None,
) -> Path:
    """Write a ``Data`` class to an ODCS YAML file."""
    from pipelantic.interchange.odcs import write_odcs as _write

    return _write(model, path, root=root)
