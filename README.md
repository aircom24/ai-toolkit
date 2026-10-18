# ai-toolkit

A central, neutral library for building and maintaining extensions for Claude Code: skills, shared
rules, templates, reference knowledge and helper tools. The repository is the source of truth. Skills
become active in Claude Code only after they are installed with the provided script.

The toolkit is domain-neutral. It contains a reference skill that demonstrates the pattern, not a
concrete business workflow.

## Architecture

| Principle | How it is applied |
|-----------|-------------------|
| One source of each file | Every skill exists once, in `skills/<name>/`. No copies in `.claude/`. |
| Skills are self-contained after install | Declared dependencies are copied into `_shared/` at install time. |
| Explicit dependencies | Skills list shared files in frontmatter `dependencies`. Nothing is applied implicitly. |
| Separation of concerns | Instructions (`skills/`), behavior principles (`rules/`), fill-in structures (`templates/`), reference material (`knowledge/`), executable code (`tools/`), shared settings (`config/`). |
| Safe installation | Installs are tracked by a manifest. Local edits are detected and never overwritten silently. |
| Plain tooling | Python standard library only. No build step and no framework. |

### Why skills are not in `.claude/skills/`

Claude Code discovers skills in `.claude/skills/` of a project and in `~/.claude/skills/`. Placing the
sources in `.claude/skills/` of this repository would make them active for anyone working in the
repository, and would duplicate them if they are also installed globally. Instead, sources live in
`skills/`, and the installer copies them to `~/.claude/skills/` on request. Nothing is duplicated in the
repository.

## Directory layout

```text
.
├── README.md            # this file
├── CLAUDE.md            # guidance for working in this repository
├── CHANGELOG.md         # version history and how to record changes
├── .gitignore
├── skills/              # one directory per skill, each with SKILL.md
├── rules/               # reusable principles, loaded explicitly by skills
├── templates/           # reusable document skeletons with placeholders
├── knowledge/           # reference material consulted on demand
├── tools/               # executable helpers used by skills or people
├── config/              # shared non-secret configuration and metadata
├── inputs/              # working input data (not versioned, except .gitkeep)
├── outputs/             # generated results (not versioned, except .gitkeep)
├── tests/               # unittest suite and fixtures
└── scripts/             # maintenance scripts (install, uninstall, validate, list)
```

Each component directory has a `README.md` that explains its conventions.

## Components

| Type | Location | Format | Activated by |
|------|----------|--------|--------------|
| Skill | `skills/<name>/SKILL.md` | Frontmatter: `name`, `description`, `version`, optional `dependencies` | `install_skills.py` |
| Rule | `rules/<name>.md` | Frontmatter: `name`, `description`, `version` | A skill that declares it |
| Template | `templates/<name>.md` | Frontmatter: `name`, `description`, `version` | A skill that declares it |
| Knowledge | `knowledge/<topic>/<name>.md` | Frontmatter: `name`, `description`, `version` | A skill that declares it |
| Tool | `tools/<name>/` | Code plus its own `README.md` | Referenced by a skill |

### Global instructions, explicit rules, reference material

1. **`CLAUDE.md`** holds instructions for working in this repository. It is not part of any installed skill.
2. **`rules/`** holds principles that apply only where a skill references them. Claude Code does not
   apply these files on its own.
3. **`knowledge/`** holds material that is read only when a task needs it.

## Defining dependencies

A skill declares what it needs in its frontmatter:

```yaml
dependencies:
  - rules/accuracy.md
  - templates/document-template.md
```

Paths are relative to the repository root. Inside the skill, link to them with the `_shared/` prefix:

```markdown
Follow the accuracy rule at `_shared/rules/accuracy.md` when collecting facts.
```

The validator checks that every declared dependency exists, that every `_shared/` link matches a declared
dependency, and that all other links stay inside the skill directory. The installer copies each dependency
to `~/.claude/skills/<name>/_shared/<path>`, so an installed skill never refers back to this repository.

## Adding components

| To add | Steps |
|--------|-------|
| A skill | Create `skills/<name>/SKILL.md` (copy the structure of `example-skill`), run the validator, dry-run the install, add a changelog entry. |
| A rule | Create `rules/<name>.md` with frontmatter, add it to the table in `rules/README.md`, reference it from the skills that need it. |
| A template | Create `templates/<name>.md` with frontmatter, add it to `templates/README.md`, reference it from the skills that need it. |
| Knowledge | Create `knowledge/<topic>/<name>.md` with frontmatter; declare it only where it is used. |
| A tool | Create `tools/<name>/` with code and a `README.md`; document how skills invoke it. |

Every change is recorded under `[Unreleased]` in [`CHANGELOG.md`](CHANGELOG.md).

## Installing, updating and removing skills

Skills are installed into `~/.claude/skills/` (override with `--target`). The installer never runs
without a plan: `--dry-run` shows the planned action for every skill.

| Action | Result |
|--------|--------|
| `install` | Skill is new in the target; it is copied with its dependencies and a manifest. |
| `up-to-date` | Installed files match the repository; nothing is done. |
| `update` | Repository has a newer version and the installed copy is unmodified; files are replaced after confirmation. Files removed in the new version are deleted. |
| `conflict` | The installed directory has local changes, or it is not managed by the toolkit. Nothing is changed. |
| `replace` | Only with `--force`: the existing directory is copied to `~/.claude/ai-toolkit-backups/` first, then replaced. |

Commands:

```bash
python3 scripts/install_skills.py --all --dry-run          # preview everything
python3 scripts/install_skills.py example-skill            # install one skill (asks for confirmation)
python3 scripts/install_skills.py example-skill --yes      # same, without prompt
python3 scripts/install_skills.py example-skill --force    # replace local changes, keep a backup
python3 scripts/uninstall_skills.py example-skill --dry-run
python3 scripts/uninstall_skills.py example-skill --yes    # remove a managed skill
```

Exit codes for both scripts: `0` success or nothing to do, `1` usage or validation error, `2` conflict,
refused or cancelled. Uninstall only removes directories that carry the toolkit's manifest, and
it always lists locally changed files before deletion.

Do not edit files under `~/.claude/skills/` by hand. Change the source here and reinstall.

## Validation and tests

```bash
python3 scripts/validate_structure.py                  # structure, metadata, dependencies, links
python3 -m unittest discover -s tests -v               # validator and installer tests
python3 scripts/list_components.py                     # overview of all components
python3 scripts/list_components.py --type skills --json
```

The validator exits with `1` when it finds any error. Run both validator and tests before each commit.

## Git workflow

- Version all source: skills, rules, templates, knowledge, tools, config, docs and tests.
- `inputs/` and `outputs/` are ignored, except their `.gitkeep` files.
- To version a specific example deliberately, place it in `tests/fixtures/<name>/`, or force-add it with
  `git add -f <path>`. Mention the reason in the commit message.
- Commit small, focused changes with a descriptive message. Record user-visible changes in `CHANGELOG.md`.
- Never commit secrets, tokens, credentials or personal data. `.gitignore` covers common cases, but review
  `git status` before every commit.

## Known limitations

- Frontmatter is parsed by a deliberately small parser: `key: value` pairs and simple `- item` lists.
  Nested structures and multi-line values are not supported.
- Installation copies files; it does not resolve versions of other skills. Skills do not depend on each other.
- `list_components.py` does not list tools, because they have no metadata format.
- The installer does not run skills and does not verify that Claude Code loads them; check in a new session.
- Windows paths and permissions are not tested; the scripts target macOS and Linux shells.
