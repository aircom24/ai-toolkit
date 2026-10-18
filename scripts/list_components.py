#!/usr/bin/env python3
"""List skills, rules, templates and knowledge documents with their metadata.

Usage:
  list_components.py [--type skills|rules|templates|knowledge] [--json]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _common import COMPONENT_KINDS, EXIT_OK, REPO_ROOT, SKILL_FILE, component_files, read_frontmatter, skill_dirs

KINDS = ("skills",) + COMPONENT_KINDS
DESCRIPTION_WIDTH = 70


def collect(kind: str, root: Path = REPO_ROOT) -> list[dict]:
    items = []
    if kind == "skills":
        paths = [(path / SKILL_FILE, path.name) for path in skill_dirs(root)]
    else:
        paths = [(path, path.stem) for path in component_files(kind, root)]
    for file, fallback_name in paths:
        rel = file.relative_to(root).as_posix()
        try:
            meta = read_frontmatter(file) or {}
        except ValueError as exc:
            meta = {"error": str(exc)}
        items.append({
            "type": kind,
            "name": str(meta.get("name", fallback_name)),
            "version": str(meta.get("version", "-")),
            "description": str(meta.get("description", "")),
            "dependencies": len(meta.get("dependencies", [])) if kind == "skills" and isinstance(meta.get("dependencies"), list) else 0,
            "path": rel,
            "error": meta.get("error"),
        })
    return items


def print_table(items: list[dict]) -> None:
    if not items:
        print("No components found.")
        return
    rows = [("TYPE", "NAME", "VERSION", "DESCRIPTION")]
    for item in items:
        description = item["error"] or item["description"]
        if len(description) > DESCRIPTION_WIDTH:
            description = description[: DESCRIPTION_WIDTH - 3] + "..."
        rows.append((item["type"], item["name"], item["version"], description))
    widths = [max(len(row[col]) for row in rows) for col in range(3)]
    for row in rows:
        print(f"{row[0]:<{widths[0]}}  {row[1]:<{widths[1]}}  {row[2]:<{widths[2]}}  {row[3]}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="List ai-toolkit components.")
    parser.add_argument("--type", choices=KINDS, help="only show one component type")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args(argv)

    kinds = [args.type] if args.type else list(KINDS)
    items = [item for kind in kinds for item in collect(kind)]
    if args.json:
        print(json.dumps(items, indent=2, ensure_ascii=False))
    else:
        print_table(items)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
