"""Shared helpers for ai-toolkit scripts. Standard library only."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TARGET = Path.home() / ".claude" / "skills"
SKILL_FILE = "SKILL.md"
MANIFEST_NAME = ".ai-toolkit-manifest.json"
SHARED_DIR = "_shared"
COMPONENT_KINDS = ("rules", "templates", "knowledge")
NAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")
IGNORED_NAMES = {"__pycache__", ".DS_Store"}

EXIT_OK, EXIT_USAGE, EXIT_CONFLICT = 0, 1, 2


def parse_frontmatter(text: str) -> dict | None:
    """Return the leading `---` block as a dict, or None when there is none.

    Supports `key: value` pairs and `key:` followed by `  - item` lists.
    Deliberately minimal so the toolkit needs no third-party packages.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    try:
        end = lines.index("---", 1)
    except ValueError:
        raise ValueError("frontmatter block is not closed")
    data: dict = {}
    list_key: str | None = None
    for line in lines[1:end]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith("  - ") and list_key is not None:
            data[list_key].append(line[4:].strip())
            continue
        key, sep, value = line.partition(":")
        if not sep or line.startswith(" "):
            raise ValueError(f"unsupported frontmatter line: {line!r}")
        key, value = key.strip(), value.strip().strip("\"'")
        if value:
            data[key] = value
            list_key = None
        else:
            data[key] = []
            list_key = key
    return data


def read_frontmatter(path: Path) -> dict | None:
    return parse_frontmatter(path.read_text(encoding="utf-8"))


def skill_meta(skill_dir: Path) -> dict:
    meta = read_frontmatter(skill_dir / SKILL_FILE)
    if meta is None:
        raise ValueError(f"{skill_dir.name}/{SKILL_FILE} has no frontmatter")
    return meta


def skill_dependencies(skill_dir: Path) -> list[str]:
    deps = skill_meta(skill_dir).get("dependencies", [])
    if not isinstance(deps, list):
        raise ValueError(f"{skill_dir.name}: 'dependencies' must be a list")
    return deps


def skill_dirs(root: Path = REPO_ROOT) -> list[Path]:
    base = root / "skills"
    if not base.is_dir():
        return []
    return sorted(p for p in base.iterdir() if p.is_dir() and (p / SKILL_FILE).is_file())


def component_files(kind: str, root: Path = REPO_ROOT) -> list[Path]:
    """Markdown files of a component kind, excluding README.md."""
    base = root / kind
    if not base.is_dir():
        return []
    return sorted(p for p in base.rglob("*.md") if p.name != "README.md")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_manifest(target: Path) -> dict | None:
    manifest = target / MANIFEST_NAME
    if not manifest.is_file():
        return None
    return json.loads(manifest.read_text(encoding="utf-8"))


def find_local_changes(target: Path, manifest: dict) -> list[str]:
    """Files changed, removed or added inside an installed skill since installation."""
    recorded = manifest["files"]
    changed = []
    for rel, digest in recorded.items():
        path = target / rel
        if not path.is_file() or sha256_file(path) != digest:
            changed.append(rel)
    for path in sorted(target.rglob("*")):
        rel = path.relative_to(target).as_posix()
        if path.is_file() and rel != MANIFEST_NAME and rel not in recorded and not IGNORED_NAMES.intersection(path.parts):
            changed.append(rel)
    return changed


def confirm(question: str, assume_yes: bool) -> bool:
    if assume_yes:
        return True
    if not sys.stdin.isatty():
        print("Confirmation required: re-run with --yes in non-interactive mode.", file=sys.stderr)
        return False
    return input(f"{question} [y/N] ").strip().lower() in ("y", "yes")
