#!/usr/bin/env python3
"""Validate repository structure, skill metadata, dependencies and local links.

Exit code 0 when all checks pass, 1 when any error is found.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from _common import (
    COMPONENT_KINDS,
    EXIT_OK,
    NAME_PATTERN,
    REPO_ROOT,
    SHARED_DIR,
    SKILL_FILE,
    component_files,
    read_frontmatter,
    skill_dependencies,
    skill_dirs,
)

REQUIRED_PATHS = [
    "README.md",
    "CLAUDE.md",
    "CHANGELOG.md",
    ".gitignore",
    "skills/README.md",
    "rules/README.md",
    "templates/README.md",
    "knowledge/README.md",
    "tools/README.md",
    "config/README.md",
    "inputs/.gitkeep",
    "outputs/.gitkeep",
    "tests/README.md",
    "tests/fixtures/.gitkeep",
    "scripts/_common.py",
    "scripts/install_skills.py",
    "scripts/uninstall_skills.py",
    "scripts/validate_structure.py",
    "scripts/list_components.py",
]
LINK_PATTERN = re.compile(r"\]\(([^)\s]+)\)")


def validate(root: Path = REPO_ROOT) -> list[str]:
    errors: list[str] = []
    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            errors.append(f"missing required path: {rel}")
    errors += _check_skills(root)
    for kind in COMPONENT_KINDS:
        errors += _check_components(kind, root)
    errors += _check_links(root)
    return errors


def _check_skills(root: Path) -> list[str]:
    errors: list[str] = []
    seen: dict[str, str] = {}
    for skill in skill_dirs(root):
        where = f"skills/{skill.name}/{SKILL_FILE}"
        if not NAME_PATTERN.match(skill.name):
            errors.append(f"skills/{skill.name}: directory name must match {NAME_PATTERN.pattern}")
        try:
            meta = read_frontmatter(skill / SKILL_FILE)
            deps = skill_dependencies(skill) if meta is not None else []
        except ValueError as exc:
            errors.append(f"{where}: {exc}")
            continue
        if meta is None:
            errors.append(f"{where}: missing frontmatter")
            continue
        name = str(meta.get("name", ""))
        if name != skill.name:
            errors.append(f"{where}: name {name!r} must equal directory name {skill.name!r}")
        if name in seen:
            errors.append(f"{where}: duplicate skill name {name!r} (also {seen[name]})")
        seen[name] = where
        for field in ("description", "version"):
            if not meta.get(field):
                errors.append(f"{where}: missing field {field!r}")
        for dep in deps:
            target = (root / dep).resolve()
            if root.resolve() not in target.parents or not target.is_file():
                errors.append(f"{where}: dependency not found inside repository: {dep}")
    return errors


def _check_components(kind: str, root: Path) -> list[str]:
    errors: list[str] = []
    seen: dict[str, str] = {}
    for path in component_files(kind, root):
        rel = path.relative_to(root).as_posix()
        try:
            meta = read_frontmatter(path)
        except ValueError as exc:
            errors.append(f"{rel}: {exc}")
            continue
        if meta is None:
            errors.append(f"{rel}: missing frontmatter (name, description, version)")
            continue
        for field in ("name", "description", "version"):
            if not meta.get(field):
                errors.append(f"{rel}: missing field {field!r}")
        name = str(meta.get("name", ""))
        if name and name != path.stem:
            errors.append(f"{rel}: name {name!r} must equal file name {path.stem!r}")
        if name in seen:
            errors.append(f"{rel}: duplicate {kind} name {name!r} (also {seen[name]})")
        seen[name] = rel
    return errors


def _owning_skill(md: Path, root: Path) -> Path | None:
    parts = md.relative_to(root).parts
    if len(parts) >= 3 and parts[0] == "skills":
        return root / "skills" / parts[1]
    return None


def _check_links(root: Path) -> list[str]:
    """Local markdown links must resolve. Inside a skill they must stay in the skill directory,
    except `_shared/...` links, which must match a declared dependency."""
    errors: list[str] = []
    for md in sorted(root.rglob("*.md")):
        rel = md.relative_to(root).as_posix()
        if ".git" in md.relative_to(root).parts:
            continue
        skill = _owning_skill(md, root)
        deps: set[str] = set()
        if skill is not None and (skill / SKILL_FILE).is_file():
            try:
                deps = set(skill_dependencies(skill))
            except ValueError:
                deps = set()  # already reported by _check_skills
        for link in LINK_PATTERN.findall(md.read_text(encoding="utf-8")):
            if link.startswith(("http://", "https://", "mailto:", "#")):
                continue
            path_part = link.split("#", 1)[0]
            if not path_part:
                continue
            if skill is not None and path_part.startswith(SHARED_DIR + "/"):
                if path_part[len(SHARED_DIR) + 1:] not in deps:
                    errors.append(f"{rel}: link {link} is not declared in the skill's dependencies")
                continue
            target = (md.parent / path_part).resolve()
            if not target.exists():
                errors.append(f"{rel}: broken link {link}")
                continue
            if skill is not None and skill.resolve() not in target.parents:
                errors.append(f"{rel}: link {link} points outside the skill directory")
    return errors


def main() -> int:
    errors = validate(REPO_ROOT)
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"\n{len(errors)} error(s) found.")
        return 1
    print("OK: repository structure is valid.")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
