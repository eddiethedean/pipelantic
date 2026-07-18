"""Lower DTCS kernel actions onto Polars frames."""

from __future__ import annotations

from typing import Any

import polars as pl

from etlantic_polars.lowering.expr import lower_expr

KERNEL_ACTIONS = frozenset(
    {
        "dtcs:filter",
        "dtcs:project",
        "dtcs:with_fields",
        "dtcs:drop_fields",
        "dtcs:rename_fields",
    }
)


def apply_action(
    frame: pl.DataFrame | pl.LazyFrame,
    action: dict[str, Any],
    *,
    parameters: dict[str, Any],
) -> pl.DataFrame | pl.LazyFrame:
    """Apply one kernel semantic action to a Polars frame."""
    kind = action.get("kind") or {}
    name = kind.get("action")
    params = kind.get("parameters") or {}
    if name == "dtcs:filter":
        predicate = lower_expr(params["predicate"], parameters=parameters)
        return frame.filter(predicate)
    if name == "dtcs:project":
        fields = params.get("fields") or []
        exprs: list[pl.Expr | str] = []
        for field in fields:
            if isinstance(field, str):
                exprs.append(field)
            elif isinstance(field, dict):
                if "expression" in field:
                    alias = field.get("name")
                    if not alias:
                        raise ValueError(
                            "dtcs:project expression fields require a name alias"
                        )
                    exprs.append(
                        lower_expr(field["expression"], parameters=parameters).alias(
                            str(alias)
                        )
                    )
                elif "name" in field:
                    exprs.append(str(field["name"]))
            else:
                raise ValueError(f"Unsupported project field {field!r}")
        return frame.select(exprs)
    if name == "dtcs:with_fields":
        assignments = []
        for item in params.get("assignments") or []:
            if item.get("window") is not None:
                raise ValueError(
                    "dtcs:with_fields window specs are not supported by the "
                    "Polars kernel compiler"
                )
            expr = lower_expr(item["expression"], parameters=parameters)
            assignments.append(expr.alias(str(item["name"])))
        return frame.with_columns(assignments)
    if name == "dtcs:drop_fields":
        names = [str(n) for n in (params.get("fields") or params.get("names") or [])]
        return frame.drop(names)
    if name == "dtcs:rename_fields":
        mapping = params.get("mapping") or {}
        if isinstance(mapping, list):
            rename = {
                str(item["from"]): str(item["to"])
                for item in mapping
                if isinstance(item, dict)
            }
        else:
            rename = {str(k): str(v) for k, v in dict(mapping).items()}
        return frame.rename(rename)
    raise ValueError(f"Unsupported action {name!r}")
