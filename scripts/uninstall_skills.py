#!/usr/bin/env python3
"""Remove one skill that was installed by install_skills.py.

Only directories carrying an ai-toolkit manifest are removed. Locally changed files are
listed before removal. Removal always needs confirmation: --yes or an interactive answer.

Usage:
  uninstall_skills.py <skill-name> [--target DIR] [--dry-run] [--yes]

Exit codes: 0 removed, not installed or dry run; 1 usage error; 2 refused or cancelled.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from _common import (
    DEFAULT_TARGET,
    EXIT_CONFLICT,
    EXIT_OK,
    EXIT_USAGE,
    NAME_PATTERN,
    confirm,
    find_local_changes,
    read_manifest,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Remove an ai-toolkit skill from Claude Code's skills directory.")
    parser.add_argument("skill", help="name of the installed skill to remove")
    parser.add_argument("--target", type=Path, default=DEFAULT_TARGET, help=f"skills directory (default: {DEFAULT_TARGET})")
    parser.add_argument("--dry-run", action="store_true", help="show what would be removed without deleting")
    parser.add_argument("--yes", action="store_true", help="skip the confirmation prompt")
    args = parser.parse_args(argv)

    if not NAME_PATTERN.match(args.skill):
        print(f"ERROR: invalid skill name {args.skill!r}.", file=sys.stderr)
        return EXIT_USAGE

    target_root = args.target.expanduser()
    target = target_root / args.skill
    if not target.exists():
        print(f"{args.skill}: not installed in {target_root}. Nothing to do.")
        return EXIT_OK

    manifest = read_manifest(target)
    if manifest is None:
        print(f"ERROR: {target} is not managed by ai-toolkit (no manifest). Refusing to remove it.", file=sys.stderr)
        return EXIT_CONFLICT

    print(f"Will remove {target} ({len(manifest['files'])} managed file(s)).")
    changes = find_local_changes(target, manifest)
    if changes:
        print("Locally changed, removed or added files (these will be deleted too):")
        for rel in changes:
            print(f"  - {rel}")
    if args.dry_run:
        print("Dry run: nothing was removed.")
        return EXIT_OK
    if not confirm(f"Remove {target}?", args.yes):
        print("Cancelled. Nothing was removed.")
        return EXIT_CONFLICT

    shutil.rmtree(target)
    print(f"Removed {target}")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
