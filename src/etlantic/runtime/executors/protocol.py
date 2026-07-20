"""Engine executor protocol for runtime dispatch."""

from __future__ import annotations

from typing import Any, Protocol


class EngineExecutor(Protocol):
    """Execute sources, steps, and sinks for one engine family."""

    def matches(self, engine: str) -> bool: ...

    async def execute_source(self, ctx: Any, node: Any, **kwargs: Any) -> Any: ...

    async def execute_step(self, ctx: Any, node: Any, **kwargs: Any) -> Any: ...

    async def execute_sink(self, ctx: Any, node: Any, **kwargs: Any) -> Any: ...
