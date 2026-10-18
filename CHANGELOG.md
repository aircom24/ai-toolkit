# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the toolkit as a whole uses
[Semantic Versioning](https://semver.org/).

## How to record changes

- Add each change under `## [Unreleased]`, in the section that fits: `Added`, `Changed`, `Deprecated`,
  `Removed`, `Fixed` or `Security`.
- Write one line per change, from the user's point of view. Name the component it affects.
- When releasing, rename `[Unreleased]` to `[x.y.z] - YYYY-MM-DD` and start a new empty `[Unreleased]` section.
- Skills carry their own `version` in `SKILL.md`. Mention the skill and its new version in the entry.

## [Unreleased]

## [0.1.0] - 2026-10-18

### Added

- Repository structure for skills, rules, templates, knowledge, tools, config, tests and scripts.
- `example-skill` (0.1.0): neutral reference skill showing structure, dependencies and quality checks.
- Shared rules: accuracy, input validation, output quality, uncertainty handling, naming conventions.
- `document-template` (0.1.0): neutral template with placeholders and required/optional section markers.
- `scripts/install_skills.py`: installs skills and their dependencies into `~/.claude/skills/` with dry-run,
  manifest tracking, conflict detection, backups on `--force`, and confirmation.
- `scripts/uninstall_skills.py`: removes only skills that carry the toolkit's manifest, after confirmation.
- `scripts/validate_structure.py`: checks required paths, frontmatter, name uniqueness, dependencies and local links.
- `scripts/list_components.py`: lists components as a table or JSON.
- `tests/test_toolkit.py`: unittest suite for the validator and installer, using temporary target directories.
- Documentation: `README.md`, `CLAUDE.md`, per-directory README files.
