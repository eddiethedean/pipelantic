#!/usr/bin/env python3
"""Scan src/etlantic for diagnostic code literals and print a catalog.

Usage:
  uv run python scripts/generate_diagnostics_catalog.py
  uv run python scripts/generate_diagnostics_catalog.py --markdown >> docs/10_REFERENCE/DIAGNOSTICS_GENERATED.md
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "etlantic"
CODE_RE = re.compile(r'\bcode\s*=\s*["\']([A-Z]{2,}[A-Z0-9]*\d{3})["\']')
LITERAL_RE = re.compile(r'["\']((?:PM|ODCS|DTCS|DPCS)[A-Z0-9]*\d{3})["\']')


def collect_codes() -> dict[str, set[str]]:
    found: dict[str, set[str]] = {}
    for path in SRC.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        rel = str(path.relative_to(ROOT))
        for match in CODE_RE.finditer(text):
            found.setdefault(match.group(1), set()).add(rel)
        for match in LITERAL_RE.finditer(text):
            found.setdefault(match.group(1), set()).add(rel)
    return found


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--markdown",
        action="store_true",
        help="Emit a markdown table instead of plain text",
    )
    args = parser.parse_args()
    codes = collect_codes()
    if args.markdown:
        print("| Code | Example source paths |")
        print("|---|---|")
        for code in sorted(codes):
            paths = ", ".join(f"`{p}`" for p in sorted(codes[code])[:3])
            print(f"| `{code}` | {paths} |")
        return
    for code in sorted(codes):
        paths = ", ".join(sorted(codes[code])[:5])
        print(f"{code}\t{paths}")
    print(f"# {len(codes)} codes", file=__import__("sys").stderr)


if __name__ == "__main__":
    main()
