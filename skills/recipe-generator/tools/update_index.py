#!/usr/bin/env python3
"""Rebuild the README.md index of a recipe folder from the recipe PDFs in it.

Usage:
  update_index.py <folder>

Each recipe is a PDF made by the recipe-generator skill. The index lists the file name, a title made from
it and the date of the last change. The index is regenerated on every run, so edit the recipes, not the
index. Standard library only.

Exit codes: 0 index written, 2 usage error.
"""

from __future__ import annotations

import argparse
import datetime
import sys
from pathlib import Path

EXIT_OK, EXIT_USAGE = 0, 2
INDEX_NAME = "README.md"
INTRO = """# Przepisy kuchenne

Ten katalog zawiera przepisy wygenerowane przez skill `recipe-generator`. Każdy przepis to plik `.pdf`.

Lista poniżej jest tworzona automatycznie. Nie edytuj jej ręcznie.

"""


def title_of(path: Path) -> str:
    words = path.stem.replace("-", " ").strip()
    return words[:1].upper() + words[1:]


def changed_on(path: Path) -> str:
    return datetime.date.fromtimestamp(path.stat().st_mtime).isoformat()


def build_index(folder: Path) -> str:
    recipes = sorted(folder.glob("*.pdf"), key=lambda p: p.name)
    rows = [f"| [{title_of(p)}]({p.name}) | {changed_on(p)} |" for p in recipes]
    body = "| Przepis | Ostatnia zmiana |\n|---|---|\n" + "\n".join(rows)
    if not rows:
        body = "Brak przepisów w tym katalogu."
    return INTRO + body + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Rebuild the README.md index of a recipe folder.")
    parser.add_argument("folder", type=Path, help="folder that holds the recipe PDFs")
    args = parser.parse_args(argv)
    folder = args.folder.expanduser()
    if not folder.is_dir():
        print(f"ERROR: {folder} is not a folder.", file=sys.stderr)
        return EXIT_USAGE
    (folder / INDEX_NAME).write_text(build_index(folder), encoding="utf-8")
    print(f"Wrote {folder / INDEX_NAME}")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
