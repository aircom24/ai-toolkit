# Config

Shared, non-secret project configuration and component metadata.

## What belongs here

- Shared configuration that more than one script or skill reads, once it is needed.
- Metadata that does not fit into a component's frontmatter.

## What does not belong here

- Secrets, tokens, passwords, private keys or personal data. Read those from the environment at run
  time, never from this repository.
- Per-machine settings. Use an uncommitted local file instead (ignored by `.gitignore`).

## Current state

No configuration files are needed yet. Defaults that scripts use today are defined in
[`scripts/_common.py`](../scripts/_common.py), for example the default install directory. Move them
here only when a second consumer needs them.

## Conventions

- Use JSON or Markdown with a clear structure. Add a schema description to this file when a new config
  file is introduced.
- Version every config change through Git like any other source file.
