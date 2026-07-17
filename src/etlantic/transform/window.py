"""Window specification helpers for portable analytic functions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from etlantic.transform.column import ColumnExpr, coerce_column
from etlantic.transform.protocol import PROFILE_WINDOW_V1, PROFILE_WINDOW_V2


def _field_ref_column(name: str) -> ColumnExpr:
    return ColumnExpr(node={"kind": "fieldRef", "target": name}, path=name)


def _coerce_order_key(col: Any) -> ColumnExpr:
    if isinstance(col, str):
        return _field_ref_column(col)
    return coerce_column(col)


def _frame_bound(value: Any) -> Any:
    """Serialize a window frame bound to a JSON-safe value."""
    if value is None or isinstance(value, (int, float, str, bool)):
        return value
    return coerce_column(value).node


@dataclass(frozen=True, slots=True)
class WindowSpec:
    """Immutable window specification."""

    partition_by: tuple[Any, ...] = ()
    order_by: tuple[Any, ...] = ()
    frame_type: str | None = None  # rows | range
    start: Any | None = None
    end: Any | None = None
    profiles: frozenset[str] = field(
        default_factory=lambda: frozenset({PROFILE_WINDOW_V1, PROFILE_WINDOW_V2})
    )

    def partitionBy(self, *cols: Any) -> WindowSpec:
        return WindowSpec(
            partition_by=tuple(cols),
            order_by=self.order_by,
            frame_type=self.frame_type,
            start=self.start,
            end=self.end,
            profiles=self.profiles,
        )

    def orderBy(self, *cols: Any) -> WindowSpec:
        return WindowSpec(
            partition_by=self.partition_by,
            order_by=tuple(cols),
            frame_type=self.frame_type,
            start=self.start,
            end=self.end,
            profiles=self.profiles,
        )

    def rowsBetween(self, start: Any, end: Any) -> WindowSpec:
        return WindowSpec(
            partition_by=self.partition_by,
            order_by=self.order_by,
            frame_type="rows",
            start=start,
            end=end,
            profiles=self.profiles,
        )

    def rangeBetween(self, start: Any, end: Any) -> WindowSpec:
        return WindowSpec(
            partition_by=self.partition_by,
            order_by=self.order_by,
            frame_type="range",
            start=start,
            end=end,
            profiles=self.profiles,
        )

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "partitionBy": [
                c if isinstance(c, str) else coerce_column(c).node
                for c in self.partition_by
            ],
            "orderBy": [],
        }
        for c in self.order_by:
            expr = _coerce_order_key(c)
            entry: dict[str, Any] = {"expression": expr.node}
            if expr.sort_direction:
                entry["direction"] = expr.sort_direction
            if expr.nulls:
                entry["nulls"] = expr.nulls
            payload["orderBy"].append(entry)
        if self.frame_type is not None:
            payload["frame"] = {
                "type": self.frame_type,
                "start": _frame_bound(self.start),
                "end": _frame_bound(self.end),
            }
        return payload


class Window:
    """Factory for window specifications."""

    unboundedPreceding = "unboundedPreceding"
    unboundedFollowing = "unboundedFollowing"
    currentRow = "currentRow"

    @staticmethod
    def partitionBy(*cols: Any) -> WindowSpec:
        return WindowSpec().partitionBy(*cols)

    @staticmethod
    def orderBy(*cols: Any) -> WindowSpec:
        return WindowSpec().orderBy(*cols)
