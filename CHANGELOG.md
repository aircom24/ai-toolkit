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

### Added

- `skill-builder` (0.1.0): guides creation of a new skill, from scaffold to validated, installable skill.
- `skill-builder/tools/scaffold_skill.py`: deterministic skeleton generator with validation and dry-run.
- Tests for the scaffold tool.
- `tools/preflight/preflight_check.py`: shared check of tools and capabilities (PDF reader and writer, screenshot,
  display, browser, Android and iOS emulators). Installs nothing; reports what is missing and how to set it up.
- `rules/environment-preflight.md` (0.1.0): skills check their requirements first and tell the user what is missing.
- Every skill must have a `## Requirements` section; the validator checks the listed capability ids against the
  preflight catalog and requires the preflight tool as a dependency when any are listed.
- `rules/requirements-interview.md` (0.1.0): skills must ask for required input before work and never write
  placeholders such as "brak" or "nie podano" in place of a value.
- `recipe-generator` (0.6.0): generates a printable recipe or process instruction in Markdown or PDF from
  a short or long-period template, using user text or internet sources; asks when the template is unclear.
  PDF defaults to A5 with a choice of A4, A6 or Letter; every template ends with a handwritten notes section.
- `recipe-generator/templates/`: short one-page recipe template and long-period process template (Polish labels).
- `recipe-generator/tools/check_recipe.py`: deterministic check of a generated recipe (placeholders, status, date,
  sources, Notatki, PDF page count and size), with tests in
  `tests/test_recipe_check.py`.
- `recipe-generator`: step-writing rules (one action per step), status and date rules, and scaling rules.
- `recipe-generator` (0.22.0): new `binder` template (`templates/binder.html`, `--template binder`): centered letter-spaced title, servings and times between horizontal rules, ingredients and directions split by a vertical rule, a nutrition table ("Składniki odżywcze") bottom left, the photo bottom right, and two binder holes in a 22 mm left margin.
- `recipe-generator` (0.20.0): templates renamed to `card.html` and `notebook.html`; all HTML rendering logic moved from Python into JavaScript in each template (data injection pattern). `render_card.py` reduced to: validate JSON, inject `window.RECIPE = {...}` into template, Chrome CDP PDF conversion. Templates open directly in a browser with built-in mock data for live development preview without Python.
- `recipe-generator` (0.19.1): PDF conversion now uses Chrome DevTools Protocol (`Page.printToPDF` with `displayHeaderFooter: false, preferCSSPageSize: true`) instead of `--print-to-pdf` CLI flag, removing the unwanted default Chrome date header and file-path footer from generated PDFs.
- `recipe-generator` (0.19.0): renderer and templates switched from LaTeX/PDF to HTML+CSS. Output is a self-contained `.html` file opened in a browser and printed. Two templates: `card` (Baskerville/Didot serif, right-aligned ingredients, SVG icons) and `notebook` (American Typewriter body, Snell Roundhand script title, binder rings, prose steps). No xelatex dependency.
- `recipe-generator` (0.18.0): second `notebook` template (`recipe-card-notebook.tex`) — script title (Snell Roundhand), bullet lists, Avenir Next body, letter-spaced section headings, horizontal rules. `render_card.py` gains `--template card|notebook`; the skill asks which layout to use before rendering. Notebook PDF uses a `-notatnik` filename suffix. Notebook step-splitting uses a separate budget constant calibrated for 10pt font.
- `recipe-generator` (0.17.0): template and renderer rebuilt from scratch. `[t]` alignment for all minipages; `top=20mm` geometry so title lands at ~10mm from paper top. `render_card.py` estimates step heights and splits overflow steps to a continuation block. `<<CONT>>` marker in the template handles overflow; notes always appear after content on the last page. Previous margin-fix attempts (vspace*, headheight patches) removed.
- `recipe-generator` (0.16.12): fixed header clipping — title and icons no longer appear above the top margin; added a top spacer to the document body so the header sits inside the 10 mm margin.
- `recipe-generator` (0.16.11): recipe data example updated (preparation time 3–4 h).
- `recipe-generator` (0.16.10): the sources and the status line are a footer on every page, at the bottom.
- `recipe-generator` (0.16.9): tools are set like the ingredients; a blank line after the description.
- `recipe-generator` (0.16.8): more space between the steps than between the lines of a step.
- `recipe-generator` (0.16.7): recipe data example updated (sugar 2,5–3 kg).
- `recipe-generator` (0.16.5): the optional ingredient is part of the ingredient list, in the same font.
- `recipe-generator` (0.16.4): smaller header icons and a gap between the header and the two columns.
- `recipe-generator` (0.16.3): the title and the time row share one line, with smaller icons; a gap before the closing notes.
- `recipe-generator` (0.16.2): the title is left-aligned and the time row (icons, labels, values on one line) sits on the right; new icons; numbers stay with their units; hyphenation is off in the card text.
- `recipe-generator` (0.16.1): nutrition is never generated. The nutrition section is shown only when the source or the user gives a value; the checker warns when values are given without a source.
- `recipe-generator` (0.16.0): the card follows the reference layout: an uppercase title, a time row with icons, ingredients and tools aligned to the right, the nutrition table, and the photo with numbered steps on the right. Fonts are Baskerville and Didot. The two blocks have fixed widths (36% and 58%); a block cannot break across pages, so the left block and the right block must each fit on the page.
- `recipe-generator` (0.15.0): the recipe card is rendered by `tools/render_card.py` from JSON card data. The layout (`templates/recipe-card.tex`) follows the reference card: script headings and title, a meta row with dividers, two text columns, a nutrition section, sources and handwriting notes. The Markdown templates and the pandoc layout files are removed. `check_recipe.py` checks the JSON data and the PDF. The card has icons in the meta row, and its columns have equal width: unequal widths need the `paracol` package, which is not installed.
- `recipe-generator` (0.14.0): PDF is the only deliverable; Markdown is a working file in a temporary folder. The PDF layout files moved to `templates/`. The index tool lists the recipe PDFs (title, last change) instead of Markdown files.
- `recipe-generator` (0.13.0): the long template is removed; the recipe card is the only template, and the check and index tools no longer take a template type.
- `recipe-generator` (0.12.0): one recipe card template in two columns (tools and ingredients on the left, short description and steps on the right), up to two A5 pages. The cheat sheet is removed from both templates. The Markdown stays plain; `tools/pdf_layout.lua` sets the two columns in PDF output from the "Narzędzia" and "Krótki opis" labels.
- `recipe-generator` (0.10.0): the PDF step checks `pdf-write` and `pdf-read` with the shared preflight check (`tools/preflight`), and the skill lists them in a Requirements section.
- `recipe-generator` (0.9.0): PDF output keeps each table on one page and moves a heading with the table below it (`tools/pdf_layout.lua` and `tools/pdf_layout.tex`, used with pandoc and xelatex).
- `recipe-generator` (0.7.0): the long template is shorter: each stage is one compact block, and the okresy oczekiwania,
  lista kontrolna, dziennik, historia zmian and status weryfikacji sections are removed (their content is in the
  harmonogram, the stage blocks and the sources).
- `recipe-generator` (0.6.0): asks the user about every gap and conflict before writing, and never writes notes about
  the source or a missing value into the recipe; `check_recipe.py` flags such notes.
- `recipe-generator`: recipes are written to `~/przepisy-kuchenne/` by default, and `tools/update_index.py` rebuilds
  the folder's `README.md` index after each recipe, with tests in `tests/test_update_index.py`.

### Changed

- `recipe-generator` (0.26.0): the card carries no status and no version. The footer prints only the sources, and
  `sources` holds only names or URLs. `status` and `version` are removed from the data template and the checks; `date`
  stays for the index and is not printed.
- `recipe-generator` (0.25.0): steps may be grouped under a heading (`{"heading", "steps"}`) for timelines such as days;
  the heading is not numbered and the numbering runs on. `render_card.py` and `check_recipe.py` check the groups.
- `recipe-generator` (0.25.0): the sources and status line is printed at 7.5 pt in dark grey (was 6 pt in light grey),
  so it stays sharp on paper; the bottom page margin is 22 mm to fit it.
- `recipe-generator` (0.24.0): `binder` is the only layout. The sources and the status line are printed at the bottom
  of every page, in the page margin, instead of after the notes.
- `recipe-generator` (0.23.0): `binder` is the default template, in the skill and in `render_card.py`. `card` and `notebook`
  are used only when the user asks for them.
- `recipe-generator` (0.23.0): the `binder` template no longer shows an empty "Składniki odżywcze" table when a recipe
  has no nutrition values; the section is left out, as the skill requires.
- Tests moved next to the skill they test: `recipe-generator` tests in `skills/recipe-generator/tests/`, and the
  `skill-builder` scaffold tests in `skills/skill-builder/tests/`. The root `tests/` keeps the toolkit tests only.
- `scripts/run_tests.py` runs the toolkit tests and every skill's tests; it replaces the `unittest discover` command.
- `scripts/install_skills.py` never copies a skill's `tests/` folder into the installed skill.

- `recipe-generator` (0.21.0): no longer asks about page size or layout. Always renders the `card` layout on A5;
  the `page_size` input is removed and `template` is always `card`.
- `example-skill` (0.2.0): writes its output to the current working directory, or to a path the user gives,
  instead of `outputs/`, so it works outside this repository.
- `example-skill` (0.3.0): starts with a requirements interview and no longer proceeds with missing input.
- `example-skill` (0.4.0): adds the Requirements section and the preflight step.
- `skill-builder` (0.2.0) and its scaffold: generated skills get a Requirements section and a preflight step before
  the interview.
- `skill-builder` scaffold: generated skills start with the interview step; the builder interviews its author first.
- `rules/uncertainty-handling` (0.2.0) and `rules/accuracy`: assumptions and "unknown" placeholders are no
  longer accepted for required input; ask instead.

### Removed

- `recipe-generator` (0.24.0): the `card` and `notebook` layouts and the LaTeX layout files. `binder` remains the
  only template; `render_card.py --template` accepts only `binder`.
- `inputs/` and `outputs/` working directories, and their ignore rules in `.gitignore`.

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
