# Skills

Each subdirectory is one independent skill. A skill is the unit that gets installed into Claude
Code's global skills directory.

## Layout

```text
skills/
└── <skill-name>/
    ├── SKILL.md        # required: frontmatter + instructions
    └── ...             # optional: extra files used only by this skill
```

The directory name, the `name` field and the installed directory name must be identical.

## Frontmatter

```yaml
---
name: example-skill
description: One or two sentences: what the skill does and when to use it.
version: 0.1.0
dependencies:           # optional, repository files this skill needs
  - rules/accuracy.md
  - templates/document-template.md
---
```

| Field | Required | Notes |
|-------|----------|-------|
| `name` | yes | Lowercase letters, digits and hyphens. Must equal the directory name. |
| `description` | yes | Claude Code uses it to decide when to invoke the skill. Write it as a trigger condition. |
| `version` | yes | Semantic version of the skill. Bump it on every change. |
| `dependencies` | no | Paths relative to the repository root. Copied into the installed skill under `_shared/`. |

## Referencing shared material

Inside `SKILL.md` and other skill files, link to shared files with the `_shared/` prefix. The link
target is the path `_shared/rules/accuracy.md` inside a Markdown link. Repository-level docs such as
this file must not use that form, because the path does not exist here. The installer copies every declared dependency to
that location, so the installed skill never points back into the repository.

Rules for links:

- A `_shared/...` link must match an entry in `dependencies`.
- Any other relative link must stay inside the skill directory.
- Links to absolute paths or other repository locations are rejected by the validator.

## Adding a skill

1. Create `skills/<skill-name>/SKILL.md` with frontmatter.
2. Declare shared rules and templates in `dependencies` and reference them with `_shared/` links.
3. Start from [`example-skill`](example-skill/SKILL.md) for the expected sections.
4. Run `python3 scripts/validate_structure.py`.
5. Preview the installation: `python3 scripts/install_skills.py <skill-name> --dry-run`.
6. Add an entry under `[Unreleased]` in `CHANGELOG.md`.

## Installation model

The repository is the source of truth. Nothing in `skills/` is active for Claude Code until
`scripts/install_skills.py` copies it to `~/.claude/skills/`. Start a new Claude Code session
after installing if a new skill does not show up.

Do not edit installed copies. Change the source here and reinstall; the installer will detect and
protect local edits (see the main [README](../README.md#installing-updating-and-removing-skills)).
