---
name: example-skill
description: Reference skill that demonstrates the ai-toolkit skill pattern. Use it as a template when creating new skills; it performs no real domain task.
version: 0.1.0
dependencies:
  - rules/accuracy.md
  - rules/input-validation.md
  - rules/output-quality.md
  - rules/uncertainty-handling.md
  - rules/naming-conventions.md
  - templates/document-template.md
---

# Example Skill

This skill shows the structure every toolkit skill should follow. It takes a short request and
produces a Markdown document from a shared template. It contains no domain knowledge.

## Purpose and scope

- **Purpose:** turn a request plus optional source material into one structured document.
- **In scope:** validating inputs, asking for missing information, writing a document from the
  shared template, checking the result.
- **Out of scope:** fetching external data, editing files outside the output location, making
  decisions that belong to the user.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `request` | yes | The task in one or two sentences. |
| `source_material` | no | Text the user supplied. Facts may only come from here. |
| `title` | no | Document title. Defaults to `Untitled result`. |

## Steps

1. **Validate the request.** Apply [input validation](_shared/rules/input-validation.md).
   Stop at the first blocking problem and report it.
2. **Handle missing or ambiguous information.** Follow
   [uncertainty handling](_shared/rules/uncertainty-handling.md). Ask one focused question
   per gap instead of guessing.
3. **Collect facts.** Use only `source_material` and the request. Apply
   [accuracy](_shared/rules/accuracy.md): every fact needs a traceable origin.
4. **Fill the template.** Use the [document template](_shared/templates/document-template.md).
   Replace every placeholder, keep all `[required]` sections, and remove `[optional]` sections
   that have no content.
5. **Name the output file.** Follow [naming conventions](_shared/rules/naming-conventions.md):
   kebab-case, derived from the title, with a `.md` extension.
6. **Check quality.** Run the checklist below before reporting.

## Error handling and missing data

- **Missing required input:** stop. Name the missing field. Do not produce a partial document.
- **Conflicting source material:** record each conflict in the `Open questions` section. Do not
  choose one version silently.
- **Template not found:** stop and report the path. Never invent a replacement structure.
- **Unsupported request:** say which part is out of scope and what the skill can do instead.

## Expected output

- One Markdown file, `<kebab-case-title>.md`, written to `outputs/` unless the user gives a path.
- The file contains the title, a summary, the details, and open questions when there are any.
- The final chat message gives the file path and a summary of at most three lines.

## Quality checklist

All items must pass before the result is reported:

- [ ] Every `[required]` section is filled with content.
- [ ] No `{{placeholder}}` remains in the document.
- [ ] Every fact can be traced to the request or the source material.
- [ ] Uncertain statements are marked as uncertain.
- [ ] The document follows [output quality](_shared/rules/output-quality.md).
