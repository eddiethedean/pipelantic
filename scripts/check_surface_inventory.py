#!/usr/bin/env python3
"""Drift check for public surface inventory vs etlantic.__all__."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "src" / "etlantic" / "schemas" / "surface-inventory.json"


def main() -> int:
    sys.path.insert(0, str(ROOT / "src"))
    import etlantic

    payload = json.loads(INVENTORY.read_text(encoding="utf-8"))
    documented = (
        set(payload.get("sdk_root_stable", []))
        | set(payload.get("sdk_root_provisional", []))
        | set(payload.get("sdk_root_experimental", []))
    )
    exported = set(etlantic.__all__) - {"__version__"}
    # Core exports may include helpers not listed as "root stable"; warn only
    # when inventory stable symbols disappear from __all__.
    missing_from_export = sorted(documented - exported)
    if missing_from_export:
        print("Surface inventory lists symbols missing from etlantic.__all__:")
        for name in missing_from_export:
            print(f"  - {name}")
        return 1
    print(
        f"Surface inventory OK: {len(documented)} inventoried root symbols "
        f"present in __all__ ({len(exported)} total exports)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
