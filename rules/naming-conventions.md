---
name: naming-conventions
description: Naming and directory-structure conventions for files and identifiers produced or stored in the toolkit.
version: 0.1.0
---

# Naming conventions

## Purpose

Make names predictable so that tools, skills and people can find things without searching.

## Rules

- Directory names and skill names use lowercase kebab-case: `example-skill`, `document-template`.
- Skill names use only lowercase letters, digits and hyphens, and start with a letter or digit.
- Markdown file names use lowercase kebab-case and end with `.md`.
- Python script names use lowercase snake_case: `validate_structure.py`.
- Generated output file names are derived from the title in kebab-case, without dates unless the
  date is part of the meaning.
- Avoid spaces, uppercase letters and non-ASCII characters in file and directory names.
- Use the same name for a component everywhere: directory, `name` field and file stem must match.

## Why

Consistent names allow automated checks and make references stable across renames of the surrounding
text.

## How to apply

Apply to every new file or identifier. The validator enforces the skill and component name rules;
the rest is a convention checked during review.
