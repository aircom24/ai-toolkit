# Rules

Rules are reusable, independent principles that skills apply when they work. Each rule file is
one topic.

## Three kinds of guidance

1. **Global instructions** live in [`CLAUDE.md`](../CLAUDE.md) at the repository root. They
   guide anyone, or Claude Code, working on this repository itself. They are not part of installed
   skills.
2. **Rules loaded explicitly by skills** live in this directory. A skill uses one only when it lists
   the file in `dependencies` and references it from its steps.
3. **Reference material** lives in [`knowledge/`](../knowledge/README.md). It is consulted only when a
   task needs it.

Claude Code does not apply the files in this directory automatically. Nothing here takes effect
unless a skill references it.

## Rule file format

```yaml
---
name: accuracy
description: One sentence: what the rule governs and when it applies.
version: 0.1.0
---
```

`name` must equal the file name without `.md`. Every rule file has the sections *Purpose*,
*Rules*, *Why* and *How to apply*.

## Available rules

| Rule | Covers |
|------|--------|
| [accuracy](accuracy.md) | Factual accuracy and source traceability |
| [input-validation](input-validation.md) | Checking inputs before work starts |
| [output-quality](output-quality.md) | Completeness and consistency of results |
| [uncertainty-handling](uncertainty-handling.md) | Missing information and stated uncertainty |
| [naming-conventions](naming-conventions.md) | File, directory and identifier naming |

## Writing a new rule

- Keep one topic per file and make it applicable to more than one skill.
- Do not copy the content of another rule; link to it instead.
- Do not put skill-specific steps here; those belong in the skill.
