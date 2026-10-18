# Knowledge

Reference material used by skills: background documents, specifications, glossaries and similar
content. Knowledge is consulted when a task needs it, not applied to every task like a rule.

## Organization

- Group files in subdirectories by topic, for example `knowledge/<topic>/<document>.md`.
- Keep one subject per file. Split large documents instead of growing one file indefinitely.
- Use the same frontmatter as rules and templates:

```yaml
---
name: glossary-core
description: One sentence: what the document covers and when to consult it.
version: 0.1.0
---
```

`name` must equal the file name without `.md`.

## Dependencies

- A skill declares a knowledge file in `dependencies` only when it actually needs it.
- Reference it from the skill with a `_shared/knowledge/...` link, and say in the steps when to read it.
- Do not declare large knowledge sets "just in case". Every declared file is copied on install.

## Maintenance

- Record the source and date of facts that can change, in the document itself.
- Remove or update outdated documents rather than keeping parallel versions.
- Never store credentials, personal data or private customer material here.
