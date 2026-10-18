# Tools

Executable helpers that skills or people can run: scripts, small CLIs and automations. Code lives
here; instructions that describe when and how to use it live in the relevant skill or in the tool's
own README.

## Organization

- One tool per directory: `tools/<tool-name>/` with its own `README.md` describing purpose, inputs,
  outputs and exit codes.
- Keep the executable code separate from prose documentation.
- Prefer the Python standard library. Add a third-party dependency only with a clear reason, and
  document it in the tool's README.

## Using tools from skills

Installed skills contain only the skill directory and declared dependencies. To make a tool available to
a skill, declare its file in `dependencies` (any repository file is allowed), and reference it from the
skill's `_shared/tools/...` path. Document how the skill invokes it.

## Not listed automatically

`scripts/list_components.py` does not list tools, because they have no metadata format. The
repository's own maintenance scripts live in [`scripts/`](../scripts/) and are not tools in this sense.

## Safety

- Never embed secrets, tokens or credentials. Read them from the environment at run time.
- Tools that delete or overwrite data must support a dry-run mode and ask for confirmation.
