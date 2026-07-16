"""Shared SQL pytest fixtures — honor PIPELANTIC_SQL_URL when set."""

from __future__ import annotations

import os

import pytest


@pytest.fixture
def sql_plugin():
    """Create the reference SQL plugin using env URL (SQLite fallback)."""
    pytest.importorskip("sqlalchemy")
    os.environ.setdefault("PIPELANTIC_SQL_URL", "sqlite+pysqlite:///:memory:")
    from pipelantic_sql import create_plugin

    return create_plugin()
