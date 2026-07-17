"""Optional sparkless backend for JVM-free local runs and tests.

Call :func:`install` before importing ``pyspark`` to route PySpark imports
to sparkless when ``ETLANTIC_SPARK_BACKEND=sparkless`` or
``SPARKLESS_TEST_MODE`` is set to a non-``pyspark`` value.
"""

from __future__ import annotations

import os
import sys
import types


def should_use_sparkless() -> bool:
    """Return True when sparkless should back PySpark imports."""
    backend = os.environ.get("ETLANTIC_SPARK_BACKEND", "").strip().lower()
    if backend == "sparkless":
        return True
    if backend == "pyspark":
        return False
    if "SPARKLESS_TEST_MODE" not in os.environ:
        return False
    return os.environ["SPARKLESS_TEST_MODE"].strip().lower() != "pyspark"


def install() -> bool:
    """Install a ``pyspark`` → sparkless module shim if appropriate.

    Returns True when the shim is active.
    """
    if not should_use_sparkless():
        return False

    existing = sys.modules.get("pyspark")
    if existing is not None and getattr(existing, "_etlantic_sparkless_shim", False):
        return True
    if existing is not None:
        return False

    try:
        import sparkless.sql as sparkless_sql
        import sparkless.sql.functions as sparkless_functions
        import sparkless.sql.types as sparkless_types
    except ImportError:
        return False

    pyspark = types.ModuleType("pyspark")
    pyspark.__dict__["_etlantic_sparkless_shim"] = True
    pyspark.__path__ = []  # type: ignore[attr-defined]

    sql = types.ModuleType("pyspark.sql")
    sql.__path__ = []  # type: ignore[attr-defined]
    for name in dir(sparkless_sql):
        if not name.startswith("_"):
            setattr(sql, name, getattr(sparkless_sql, name))
    sql.functions = sparkless_functions
    sql.types = sparkless_types

    pyspark.sql = sql  # type: ignore[attr-defined]
    sys.modules["pyspark"] = pyspark
    sys.modules["pyspark.sql"] = sql
    sys.modules["pyspark.sql.functions"] = sparkless_functions
    sys.modules["pyspark.sql.types"] = sparkless_types
    return True
