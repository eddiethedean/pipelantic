"""Experimental DataFusion plugin (Gate B / 0.19+)."""

from __future__ import annotations

__version__ = "0.19.0"

STREAMING_STABILITY = "experimental"


def create_plugin():
    """Entry point for dataframe plugin discovery."""
    from etlantic_datafusion.plugin import DataFusionPlugin

    return DataFusionPlugin()


def create_transform_compiler():
    """Entry point for portable transform compiler discovery."""
    from etlantic_datafusion.compiler import DataFusionTransformCompiler

    return DataFusionTransformCompiler()


__all__ = [
    "STREAMING_STABILITY",
    "__version__",
    "create_plugin",
    "create_transform_compiler",
]
