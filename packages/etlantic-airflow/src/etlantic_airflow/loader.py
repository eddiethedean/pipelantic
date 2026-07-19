"""Load a compiled ETLantic Airflow DAG module."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any


def load_compiled_pipeline(path: str | Path) -> Any:
    """Import a generated DAG module and return its ``dag`` object.

    Requires ``apache-airflow`` installed in the Airflow environment.
    """
    try:
        import airflow  # noqa: F401
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "Loading compiled Airflow DAGs requires apache-airflow. "
            "Install apache-airflow in the Airflow environment "
            "(not required for compile_plan)."
        ) from exc

    resolved = Path(path).resolve()
    if not resolved.is_file():
        raise FileNotFoundError(f"DAG module not found: {resolved}")

    module_name = f"etlantic_compiled_{resolved.stem}"
    spec = importlib.util.spec_from_file_location(module_name, resolved)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load DAG module from {resolved}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    dag = getattr(module, "dag", None)
    if dag is None:
        raise AttributeError(f"Module {resolved} does not define 'dag'")
    return dag


def load_compiled_module(path: str | Path) -> ModuleType:
    """Import and return the generated module (exposes ``dag`` and plan meta)."""
    load_compiled_pipeline(path)
    module_name = f"etlantic_compiled_{Path(path).resolve().stem}"
    module = sys.modules.get(module_name)
    if module is None:
        raise ImportError(f"Module {module_name} was not registered")
    return module
