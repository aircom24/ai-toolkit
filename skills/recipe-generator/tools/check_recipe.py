#!/usr/bin/env python3
"""Check a recipe JSON file against the recipe-generator rules, and optionally its rendered PDF.

Usage:
  check_recipe.py <recipe.json> [--pdf PATH] [--page-size A5|A4|A6|Letter]

Checks the JSON data for empty required fields, unfilled placeholders, notes about the source or a gap,
the date and sources rules. With --pdf it checks the page count (a recipe card has two pages at most)
and the page size, when pdfinfo is installed. Standard library only.

Exit codes: 0 no errors (warnings allowed), 1 errors found, 2 usage error.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

EXIT_OK, EXIT_ERRORS, EXIT_USAGE = 0, 1, 2
PAGE_SIZES = {"A4": (595.3, 841.9), "A5": (419.5, 595.3), "A6": (297.6, 419.5), "Letter": (612.0, 792.0)}
MAX_PAGES = 2
PLACEHOLDER = re.compile(r"\[[^\]\n]+\]")
ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
# Phrases that talk about the source or a gap instead of giving the recipe. They never belong in a recipe.
GUESS_NOTES = ("do potwierdzenia", "źródło nie", "nie podano", "nie podaje", "brak danych")
REQUIRED_TEXT = ("title", "date")
REQUIRED_LISTS = ("tools", "ingredients", "steps")
MAX_LISTED = 5


def strings(value) -> list[str]:
    """Every text value in the JSON data, at any depth."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [text for item in value.values() for text in strings(item)]
    if isinstance(value, list):
        return [text for item in value for text in strings(item)]
    return []


def step_items(data: dict) -> list[str]:
    """Step texts, with the steps of each group {heading, steps} flattened in."""
    items = []
    for item in data.get("steps", []):
        if isinstance(item, dict):
            items.extend(str(s) for s in item.get("steps", []))
        else:
            items.append(str(item))
    return items


def check(data: dict) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for field in REQUIRED_TEXT:
        if not str(data.get(field, "")).strip():
            errors.append(f"required field {field!r} is empty")
    for field in REQUIRED_LISTS:
        items = step_items(data) if field == "steps" else data.get(field, [])
        if not [item for item in items if str(item).strip()]:
            errors.append(f"required list {field!r} is empty")
    for group in data.get("steps", []):
        if isinstance(group, dict) and not (str(group.get("heading", "")).strip() and group.get("steps")):
            errors.append("each step group needs a heading and at least one step")

    for text in strings(data):
        lowered = text.lower()
        for phrase in GUESS_NOTES:
            if phrase in lowered:
                errors.append(f"text {text[:50]!r} has a note about the source or a gap ({phrase!r}); ask the user instead")
                break

    unfilled = [match.group(0) for text in strings(data) for match in PLACEHOLDER.finditer(text)]
    if unfilled:
        listed = ", ".join(unfilled[:MAX_LISTED])
        errors.append(f"{len(unfilled)} unfilled template placeholder(s), e.g. {listed}")

    date = str(data.get("date", ""))
    if date and not ISO_DATE.fullmatch(date):
        errors.append("date is not in RRRR-MM-DD format")
    listed_sources = [s for s in data.get("sources", []) if str(s).strip()]
    if not listed_sources:
        warnings.append("no sources are listed")
    nutrition = data.get("nutrition", {})
    given = [key for key, value in nutrition.items() if key != "basis" and str(value).strip()]
    if given and not listed_sources:
        warnings.append("nutrition values are given but no source is listed; confirm they come from a source or the user")

    return errors, warnings


def check_pdf(path: Path, page_size: str, errors: list[str], warnings: list[str]) -> None:
    if shutil.which("pdfinfo") is None:
        warnings.append("pdfinfo is not installed: page count and page size were not checked.")
        return
    result = subprocess.run(["pdfinfo", str(path)], capture_output=True, text=True)
    if result.returncode != 0:
        errors.append(f"pdfinfo cannot read {path}")
        return
    pages = re.search(r"Pages:\s+(\d+)", result.stdout)
    if pages and int(pages.group(1)) > MAX_PAGES:
        errors.append(f"recipe has {pages.group(1)} pages in the PDF; the limit is {MAX_PAGES}")
    size = re.search(r"Page size:\s+([\d.]+) x ([\d.]+) pts", result.stdout)
    if size and page_size in PAGE_SIZES:
        width, height = (float(value) for value in size.groups())
        expected_width, expected_height = PAGE_SIZES[page_size]
        if abs(width - expected_width) > 1 or abs(height - expected_height) > 1:
            errors.append(f"PDF page size is {width:.1f} x {height:.1f} pt; expected {page_size}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check a recipe JSON file against the recipe-generator rules.")
    parser.add_argument("recipe", type=Path, help="JSON file with the recipe content")
    parser.add_argument("--pdf", type=Path, help="PDF rendered from the recipe, to check page count and size")
    parser.add_argument("--page-size", choices=sorted(PAGE_SIZES), default="A5", help="expected page size (default: A5)")
    args = parser.parse_args(argv)

    if not args.recipe.is_file():
        print(f"ERROR: {args.recipe} is not a file.", file=sys.stderr)
        return EXIT_USAGE
    try:
        data = json.loads(args.recipe.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: {args.recipe} is not valid JSON: {exc}", file=sys.stderr)
        return EXIT_ERRORS

    errors, warnings = check(data)
    if args.pdf is not None:
        check_pdf(args.pdf, args.page_size, errors, warnings)

    for message in errors:
        print(f"ERROR: {message}")
    for message in warnings:
        print(f"WARNING: {message}")
    print(f"Result: {len(errors)} error(s), {len(warnings)} warning(s).")
    return EXIT_ERRORS if errors else EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
