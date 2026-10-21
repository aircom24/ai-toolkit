---
name: recipe-generator
description: Generates a ready-to-print recipe or step-by-step production procedure as a PDF recipe card, from text the user supplies or from sources found on the internet. Use when the user asks for a recipe, procedure or process instruction.
version: 0.26.0
dependencies:
  - rules/accuracy.md
  - rules/uncertainty-handling.md
  - rules/output-quality.md
  - rules/input-validation.md
  - rules/environment-preflight.md
  - tools/preflight/preflight_check.py
  - rules/requirements-interview.md
---

# Recipe Generator

## Purpose and scope

- **Purpose:** turn a recipe or procedure, given by the user or found in sources, into a complete recipe card
  that is delivered as a printable PDF.
- **In scope:** asking the user about every gap and conflict, collecting the source material, filling the card
  data, rendering the PDF, checking it, and keeping the index of the output folder.
- **Out of scope:** delivering Markdown; inventing quantities, temperatures, times or nutrition values that no
  source or user gives; certifying a procedure as safe or validated; changing the card layout; running any step of
  the procedure.

## Principles

- **Never guess.** A value that is not in the request, in `source_text` or in a listed source is a question
  for the user, not a value to write. This includes nutrition values.
- **Never write about the source into the recipe.** The document contains the recipe, not notes about what
  the source does or does not say. No `Do potwierdzenia`, `źródło nie podaje`, `nie podano`, `brak danych` or
  similar phrase appears in the generated file.
- **Ask before writing.** Open questions are asked before the card is filled, not after.
- **PDF is the only deliverable.** The card data is a working file in a temporary folder and is never written to
  the output folder.

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `request` | yes | The recipe or procedure the user wants, in one or two sentences. |
| `source_text` | no | Recipe text the user supplied. Facts may come only from here, from the user's answers or from listed sources. |
| `photo` | no | Path to a photo the user supplies. The skill never fetches images. |
| `output_dir` | no | Folder for the PDF files. Defaults to `~/przepisy-kuchenne`, a folder in the user's home directory for all recipes. |
| `template` | no | Only `binder` exists (sans-serif, centered title, ruled meta row, wide left margin for binder holes). Nothing to choose. |

## Requirements

| Capability | Needed for |
|------------|------------|
| `pdf-read` | opening the HTML in a browser to verify layout; optional |

The renderer uses system fonts via CSS. No external programs are required.

## Steps

1. **Check requirements, then validate the request.** Run the [environment preflight](_shared/rules/environment-preflight.md)
   first: `python3 <skill-dir>/_shared/tools/preflight/preflight_check.py pdf-write pdf-read`. Report each capability
   as present or missing, with its hint. If `pdf-write` is missing, stop and give the user the install command from
   the hint. Then apply [input validation](_shared/rules/input-validation.md). Stop at the first blocking problem
   and report it. A request with no recipe name and no `source_text` cannot be searched for reliably; ask for the
   name first.
2. **Collect the source material.**
   - If `source_text` is given, use it as the only source for facts.
   - Otherwise search the internet for the recipe or procedure with `WebSearch` in standard mode. Use
     extended mode only if the standard results are thin or off-target. Prefer at least two independent
     sources and record each URL. If only one source is found, say so and ask whether to use it alone.
   - Never copy a source's wording as a whole. Use the source for facts and write the steps in your own
     words.
3. **Use the recipe card.** The card data follows `templates/recipe-card-template.json`: title, date, meta
   (preparation time, total time, servings), tools, ingredients, optional ingredients, a short description, steps, a
   control point, storage, nutrition, sources and an optional photo. The layout is fixed in
   `templates/binder.html`; the renderer fills it. A card fits two A5 pages at most. Nothing to choose.
4. **Ask about gaps and conflicts.** Compare the source material with the template and list everything
   that is missing, unclear or contradictory. This includes:
   - a value the card needs and no source or answer gives (quantities, temperatures, times, yields);
   - two sources that disagree, or a source that contradicts itself;
   - a value that does not scale linearly, when the user asks for a different yield;
   - a safety-relevant value with no clear source (food safety temperatures, preservation or fermentation
     limits, additive doses);
   - nutrition values (energy, protein, fat, carbohydrates, sugars, fibre, salt) when no source gives them. Ask
     whether the user has them; never estimate them from the ingredients.

   Ask all open questions together, in one message, as the [requirements interview](_shared/rules/requirements-interview.md)
   requires. Use [uncertainty handling](_shared/rules/uncertainty-handling.md).
   Offer a choice (for example `2 l` / `3 l` / `bez wody`) when the sources name options; ask for a value
   when they name none. Ask about safety values in the same way, and never fill them from memory. Do not
   render the card until the user has answered. If the user answers that a value is unknown, the field stays empty
   in the card, with no comment; the open point goes into the final message instead.
5. **Use the layout.** Use the `binder` layout (centered title, ruled meta row, ingredients and steps split by a
   vertical rule, binder holes) and the A5 page size. It is the only layout. Do not ask the user about it.
6. **Fill the card data in a temporary folder.** Copy `templates/recipe-card-template.json` into the temporary folder
   (`$TMPDIR`) as `<name>.json` and fill it with the source material and the user's answers. Never write the working
   file into `output_dir`.
   - Every list item is one short line; the steps are one action each, starting with an imperative verb.
   - Steps that follow a timeline (for example days after the start) may be grouped: an element of `steps` is then
     `{"heading": "Dzień 0", "steps": ["...", "..."]}` instead of a text. The heading is printed without a number and the
     numbering runs on across the groups. Use plain texts when there is no timeline. This is the only use of groups.
   - Put each quantity, temperature and time in the step where it is used. At most three sentences per step.
     Use one unit system (metric) and one notation for temperature (°C).
   - Keep the card's order: the time row, the tools, the ingredients and the nutrition table (left column); the photo
     if given, the short description and the numbered steps (right column); then sources and the handwriting notes.
     Do not add fields.
   - Fill quantities, temperatures and times only from the source material or the user's answers. Apply
     [accuracy](_shared/rules/accuracy.md): every number needs a traceable origin.
   - Fill `sources` with each URL or document name used, and nothing else: no facts, quantities or notes. The facts
     belong in the card itself.
   - **Nutrition is never generated.** Fill `nutrition` only with values the source or the user gives, with the
     source listed in `sources`. Never estimate nutrition values from the ingredients or from general knowledge. If no
     value is given, the nutrition section is left out of the card.
   - Set `photo` only to a file the user supplied.
   - Keep the language of the labels in the card as they are. Write the content in the language of the user's request.
   - **Date.** Set `date` to today's date in RRRR-MM-DD format. The date is used by the index and is not printed on
     the card. The card carries no status and no version.
   - **Scaling.** Only when the user asks for a different yield. Scale simple proportions (for example flour and water
     in a fixed ratio). Values that do not scale linearly (yeast, salt in fermentation, baking, cooking, cooling and
     drying times) are asked about in step 4, not estimated. Put the original yield in `meta.servings` and the target
     yield in the same field, as the user wants it.
7. **Render the PDF.** Use a kebab-case file name derived from the recipe name (for example `wino-z-winogron.pdf`).
   Run: `python3 <skill-dir>/tools/render_card.py <work>.json <output_dir>/<name>.pdf --page-size A5 --template binder`
   The renderer fills the HTML template and converts it to PDF via Chrome headless (respects `@page` margins).
   Pass `.html` instead of `.pdf` to get the raw HTML without conversion. Create `output_dir` if it is the
   default folder and missing; for any other folder that does not exist, ask before creating it. If a file with
   the same name already exists, stop and ask whether to replace it or use another name. Never overwrite a recipe silently.
8. **Run the check tool.** Run [the check tool](tools/check_recipe.py) on the working file:
   `python3 <skill-dir>/tools/check_recipe.py <work>.json`
   Fix every error, render again and check again until the tool reports none. Report every warning to the user. The
   tool checks the required fields, notes about the source or a gap, placeholders, date and sources.
9. **Update the index.** Only after the file passes the check, run [the index tool](tools/update_index.py)
   on the output folder: `python3 <skill-dir>/tools/update_index.py <output_dir>`. It rebuilds `README.md` in that
   folder, a list of every recipe there with its date. Never edit the index.
10. **Check quality.** Apply [output quality](_shared/rules/output-quality.md) and the checklist below before reporting.

## Error handling and missing data

- **Missing recipe or procedure:** stop and name the missing input. Do not produce a partial document.
- **No usable sources found:** stop, report what was searched, and ask the user to paste the recipe text.
- **Sources conflict on quantities or times:** ask the user which value to use (step 4). Never pick one value silently.
- **Missing value after the user's answer:** leave the field empty in the card, with no comment, and list it as an open
  point in the final message.
- **Nutrition unknown:** the nutrition fields stay empty. Tell the user in the final message that the values need a source.
- **Safety-relevant value without a clear source:** ask the user (step 4). If the user does not know it, leave the field
  empty and tell the user, in the final message, that a qualified person must confirm it before use.
- **Template file not found:** stop and report the path. Never invent a replacement structure.
- **PDF already exists:** stop and ask whether to replace it or use another name.
- **Custom `output_dir` does not exist:** ask before creating it. Never write into a folder the user did not name.
- **Home folder not writable:** stop, report the path, and offer a different `output_dir`.
- **Photo not found:** stop and ask for another file, or render without a photo if the user agrees.
- **Recipe does not fit two pages:** shorten the text; if that is not enough, tell the user and ask how to proceed.
- **`pdf-write` missing:** stop before the interview and give the install command from the preflight hint.
- **Check tool reports errors:** fix the working file, render again and run the tool again. Do not deliver a PDF with errors.
- **`pdf-read` missing:** the PDF is still made; the check tool reports the page count and size as not checked.
- **Unsupported request:** say which part is out of scope and what the skill can do instead.

## Output decision

- **Template:** `templates/binder.html`, the only layout. The data template is `templates/recipe-card-template.json`;
  `tools/render_card.py` fills the HTML template.
- **Output format:** PDF only. The card data is a working file in the temporary folder and is never delivered.
- **Page size:** always A5. The card is at most two pages.
- **Location:** `~/przepisy-kuchenne/` by default, one folder for all recipes. Its `README.md` index is rebuilt by the
  index tool after each recipe.
- **Generator:** Chrome headless via the DevTools Protocol, through `tools/render_card.py`. The skill stops with a
  clear message when no Chrome or Chromium is found.

## Expected output

- One PDF, `<kebab-case-recipe-name>.pdf`, in `output_dir` (default `~/przepisy-kuchenne`), at most two pages, with the
  card's layout, the nutrition section, the sources, the handwriting notes, and no placeholders left.
- `README.md` in the same folder, rebuilt by the index tool to list every recipe there.
- A final message, outside the document, with the file path, the sources used, the answers the
  user gave, and every open point that was left empty.

## Quality checklist

- [ ] Every gap and conflict was asked about before the card was rendered.
- [ ] No placeholder remains in the card data.
- [ ] No note about the source or a missing value appears in the card.
- [ ] The nutrition values are given by the source or the user, and the section is absent when none are given.
- [ ] The handwriting notes section is present.
- [ ] The card is at most two pages in the PDF.
- [ ] Every quantity, temperature and time traces to the request, `source_text`, a listed source or the user's answer.
- [ ] `sources` lists every source used.
- [ ] The PDF is A5 and uses the `binder` layout, with the sources at the bottom of every page.
- [ ] The check tool reports no errors, and its warnings are listed for the user.
- [ ] The PDF is in `output_dir`, the working data is not, and the index tool has rebuilt `README.md` there.
- [ ] Steps are one action each and start with an imperative verb.
- [ ] The output follows [output quality](_shared/rules/output-quality.md).
