# Tests

Tests for the toolkit's own scripts and structure, plus test data for components.

## Layout

```text
tests/
├── README.md               # this file
├── test_toolkit.py         # unittest suite for validator and installer
└── fixtures/               # test inputs and expected outputs, versioned
```

## Running the tests

From the repository root:

```bash
python3 scripts/validate_structure.py
python3 -m unittest discover -s tests -v
```

The installer tests always use a temporary `--target` directory. They never touch `~/.claude/skills`.

## Adding tests

- Add tests for scripts to `test_toolkit.py`, or create a new `test_<topic>.py` file.
- Build broken repositories in a temporary copy (see `ValidatorTests`) instead of committing broken
  components.
- Put sample inputs and expected results for a skill in `fixtures/<skill-name>/`. Keep them small.

## Test data and Git

Fixtures are versioned because they are source material for tests. Working data in `inputs/` and
`outputs/` is not versioned; see the Git section of the main [README](../README.md#git-workflow) for
how to version a specific example deliberately.

## Principles

- Each test checks one behavior and states the expected exit code or result.
- Tests must be deterministic: no network access, no dependency on the user's home directory.
