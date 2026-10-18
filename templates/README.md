# Templates

Templates are reusable, neutral skeletons for documents and artifacts. A skill fills a template
with content; the template itself defines structure only.

## Defining a template

A template is a Markdown file with frontmatter:

```yaml
---
name: document-template
description: One sentence: what kind of document this template produces.
version: 0.1.0
---
```

Below the frontmatter, write the document skeleton. Name the file after the `name` field, for example
`document-template.md`.

## Placeholders

- Write a placeholder as `{{snake_case_name}}`, for example `{{title}}` or `{{summary}}`.
- Each placeholder must be listed in the consuming skill's steps so that the skill knows what to fill.
- A skill must not leave any placeholder unresolved in the output.

## Required and optional sections

Mark a section in its heading:

- `## Summary [required]`: the consuming skill must fill it.
- `## Open questions [optional]`: the skill removes the whole section when it has no content.

Use a single HTML comment block at the top of the template to explain the markers. The skill removes
that comment from the generated document.

## Using a template in a skill

1. List the template in the skill's `dependencies`.
2. Link to it from the skill with a `_shared/templates/...` path, for example
   `_shared/templates/document-template.md` (see the [skills guide](../skills/README.md)).
3. Describe in the steps which placeholders the skill fills and how it chooses between optional sections.

## Avoiding duplication

- Put structure in templates and behavior in rules. Do not copy rule text into a template;
  link to the rule from the skill instead.
- Do not copy a template into a skill directory. Declare it as a dependency so there is one source.
- If two templates share a section, extract the section into a new template and reference it from both.

## Available templates

| Template | Purpose |
|----------|---------|
| [document-template](document-template.md) | Neutral structured document with required and optional sections |
