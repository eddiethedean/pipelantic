"""Asset descriptor and Windows path regressions for 0.21."""

from __future__ import annotations

from pathlib import PureWindowsPath

import pytest

from etlantic.bindings import (
    normalize_assets_map,
    parse_asset_descriptor,
)
from etlantic.workspace import WorkspacePaths


def test_absolute_file_uri_preserves_path() -> None:
    parsed = parse_asset_descriptor("file:///tmp/data.csv")
    assert parsed.provider == "file"
    assert parsed.location == "/tmp/data.csv"


def test_absolute_json_uri_preserves_path() -> None:
    parsed = parse_asset_descriptor("json:///var/data/rows.json")
    assert parsed.provider == "json"
    assert parsed.location == "/var/data/rows.json"


def test_relative_json_uri_still_works() -> None:
    parsed = parse_asset_descriptor("json://data/sample.json")
    assert parsed.provider == "json"
    assert parsed.location == "data/sample.json"


def test_object_metadata_rejected() -> None:
    with pytest.raises(ValueError, match="metadata is not persisted"):
        parse_asset_descriptor(
            {
                "provider": "json",
                "location": "data/x.json",
                "metadata": {"write_mode": "overwrite"},
            }
        )
    with pytest.raises(ValueError, match="metadata is not persisted"):
        normalize_assets_map(
            {
                "out": {
                    "provider": "json",
                    "location": "data/out.json",
                    "metadata": {"x": 1},
                }
            }
        )


def test_windows_style_workspace_paths() -> None:
    root = PureWindowsPath(r"C:\Users\demo\project")
    paths = WorkspacePaths(
        root=root,  # type: ignore[arg-type]
        reports=root / ".etlantic" / "reports",  # type: ignore[arg-type]
        artifacts=root / ".etlantic" / "artifacts",  # type: ignore[arg-type]
        schema_history=root / ".etlantic" / "schema-history",  # type: ignore[arg-type]
        data=root / "data",  # type: ignore[arg-type]
    )
    assert str(paths.reports).replace("\\", "/").endswith(".etlantic/reports")
    assert "schema-history" in str(paths.schema_history).replace("\\", "/")
    assert str(paths.data).replace("\\", "/").endswith("/data")
