# CLAUDE.md

Guidance for working in this repository. Read [README.md](README.md) for architecture and commands.

- This repository is the source of truth for skills, rules, templates, knowledge and tools. Edit sources here.
- Never edit installed copies under `~/.claude/skills/` by hand. Change the source and reinstall with `scripts/install_skills.py`.
- Installed skills must stay self-contained. Reference shared files only through `dependencies` and `_shared/` links.
- Every `SKILL.md` needs frontmatter with `name` (equal to the directory name), `description` and `version`.
- Run `python3 scripts/validate_structure.py` and `python3 -m unittest discover -s tests -v` after every change.
- Preview installs with `--dry-run` first. Never remove or overwrite installed skills without confirmation.
- Keep the example skill domain-neutral; do not add business-specific content to it.
- Do not commit or store secrets, tokens or personal data anywhere in the repository.
- Do not version working data in `inputs/` or `outputs/`.
- Write documentation in English.
- Record every user-visible change under `[Unreleased]` in `CHANGELOG.md`.
- Do not run `git init`, `git commit`, `git push` or other history-changing commands unless the user asks for them explicitly.
