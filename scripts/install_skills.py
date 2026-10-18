#!/usr/bin/env python3
"""Install skills from this repository into Claude Code's global skills directory.

Each skill is copied to <target>/<skill-name>/. Repository files listed in the skill's
`dependencies` are copied to <skill-name>/_shared/ so the installed skill is self-contained.
A manifest file marks the directory as managed and records file hashes, which lets later
runs detect local edits.

Examples:
  install_skills.py --all --dry-run
  install_skills.py example-skill --yes
  install_skills.py --all --yes --target /some/other/dir

Exit codes: 0 success or nothing to do, 1 usage or validation error,
2 conflict, refused or cancelled.
"""

from __future__ import annotations

import argparse
import datetime
import json
import shutil
import sys
from pathlib import Path

from _common import (
    DEFAULT_TARGET,
    EXIT_CONFLICT,
    EXIT_OK,
    EXIT_USAGE,
    IGNORED_NAMES,
    MANIFEST_NAME,
    NAME_PATTERN,
    REPO_ROOT,
    SHARED_DIR,
    confirm,
    find_local_changes,
    read_manifest,
    sha256_file,
    skill_dependencies,
    skill_dirs,
    skill_meta,
)


def build_file_map(skill_dir: Path) -> dict[str, Path]:
    """Return {path inside the installed skill: source file} for everything it needs."""
    files: dict[str, Path] = {}
    for path in sorted(skill_dir.rglob("*")):
        if path.is_file() and not IGNORED_NAMES.intersection(path.parts):
            files[path.relative_to(skill_dir).as_posix()] = path
    for dep in skill_dependencies(skill_dir):
        source = (REPO_ROOT / dep).resolve()
        if REPO_ROOT.resolve() not in source.parents or not source.is_file():
            raise ValueError(f"{skill_dir.name}: dependency not found inside repository: {dep}")
        files[f"{SHARED_DIR}/{dep}"] = source
    return files


def plan_skill(name: str, version: str, target_root: Path, file_map: dict[str, Path], force: bool) -> tuple[str, str]:
    """Decide what happens to one skill. Returns (action, message)."""
    target = target_root / name
    if not target.exists():
        return "install", "not installed yet"
    manifest = read_manifest(target)
    if manifest is None:
        return ("replace" if force else "conflict"), f"exists but is not managed by ai-toolkit ({MANIFEST_NAME} missing)"
    changes = find_local_changes(target, manifest)
    if changes:
        return ("replace" if force else "conflict"), "local changes: " + ", ".join(changes)
    source_hashes = {rel: sha256_file(src) for rel, src in file_map.items()}
    if source_hashes == manifest["files"]:
        return "up-to-date", f"version {version} already installed"
    return "update", f"version {manifest.get('version', 'unknown')} -> {version}"


def backup_existing(target: Path) -> Path:
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    # Backups sit next to the skills directory, not inside it, so Claude Code never sees them.
    destination = target.parent.parent / "ai-toolkit-backups" / f"{target.name}-{stamp}"
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(target, destination)
    return destination


def write_skill(name: str, version: str, target_root: Path, file_map: dict[str, Path], previous: dict | None) -> None:
    target = target_root / name
    target.mkdir(parents=True, exist_ok=True)
    if previous:
        # Remove files that the previous version shipped but the new one does not.
        for rel in previous["files"]:
            if rel not in file_map and (target / rel).is_file():
                (target / rel).unlink()
    recorded: dict[str, str] = {}
    for rel, source in file_map.items():
        destination = target / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        recorded[rel] = sha256_file(destination)
    manifest = {
        "skill": name,
        "version": version,
        "installed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "files": recorded,
    }
    (target / MANIFEST_NAME).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Install ai-toolkit skills into Claude Code's skills directory.")
    parser.add_argument("skill", nargs="?", help="name of one skill to install")
    parser.add_argument("--all", action="store_true", help="install every skill in the repository")
    parser.add_argument("--target", type=Path, default=DEFAULT_TARGET, help=f"skills directory (default: {DEFAULT_TARGET})")
    parser.add_argument("--dry-run", action="store_true", help="show planned changes without touching files")
    parser.add_argument("--yes", action="store_true", help="skip the confirmation prompt")
    parser.add_argument("--force", action="store_true", help="replace local changes or unmanaged directories (a backup is kept)")
    args = parser.parse_args(argv)

    if bool(args.skill) == args.all:
        print("ERROR: give either a skill name or --all.", file=sys.stderr)
        return EXIT_USAGE

    available = {path.name: path for path in skill_dirs()}
    names = sorted(available) if args.all else [args.skill]
    for name in names:
        if not NAME_PATTERN.match(name) or name not in available:
            known = ", ".join(sorted(available)) or "none"
            print(f"ERROR: unknown skill {name!r}. Available: {known}", file=sys.stderr)
            return EXIT_USAGE

    target_root = args.target.expanduser()
    plans: list[tuple[str, str, dict[str, Path], str, str]] = []
    try:
        for name in names:
            skill_dir = available[name]
            version = skill_meta(skill_dir).get("version", "unknown")
            file_map = build_file_map(skill_dir)
            action, message = plan_skill(name, version, target_root, file_map, args.force)
            plans.append((name, version, file_map, action, message))
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return EXIT_USAGE

    print(f"Target: {target_root}")
    for name, _, _, action, message in plans:
        print(f"  [{action}] {name}: {message}")

    conflicts = [plan for plan in plans if plan[3] == "conflict"]
    if conflicts:
        print("ERROR: conflicts found, nothing was changed. Resolve them manually or re-run with --force (backups are kept).", file=sys.stderr)
        return EXIT_CONFLICT
    if args.dry_run:
        print("Dry run: no files were changed.")
        return EXIT_OK

    pending = [plan for plan in plans if plan[3] != "up-to-date"]
    if not pending:
        print("Nothing to do.")
        return EXIT_OK
    if not confirm(f"Apply {len(pending)} change(s) to {target_root}?", args.yes):
        print("Cancelled. Nothing was changed.")
        return EXIT_CONFLICT

    try:
        for name, version, file_map, action, _ in pending:
            target = target_root / name
            previous = None
            if action == "replace":
                print(f"  backup: {backup_existing(target)}")
                shutil.rmtree(target)
            elif action == "update":
                previous = read_manifest(target)
            write_skill(name, version, target_root, file_map, previous)
            print(f"  installed {name} {version}")
    except OSError as exc:
        print(f"ERROR: could not write to {target_root}: {exc}", file=sys.stderr)
        return EXIT_USAGE
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
