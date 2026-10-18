---
name: input-validation
description: Checks to run on user-supplied inputs before a skill starts its main work.
version: 0.1.0
---

# Input validation

## Purpose

Catch unusable inputs at the start, when they are cheap to fix, instead of producing a broken
result halfway through.

## Rules

- Check that every required input is present and not empty.
- Check the type and format the skill expects, for example a path, a number or a list.
- Check that referenced files or paths exist and are readable before using them.
- Treat whitespace-only text as empty.
- Reject inputs that exceed the size or length limit the skill documents, and say what the limit is.
- Do not silently repair an input. If normalization is needed, say what was changed.
- Report all blocking problems together when that is practical, instead of one per round trip.

## Why

Validation errors discovered late waste effort and can leave partial output that looks complete.

## How to apply

Run validation as the first step of a skill. A blocking problem stops the skill, and the report names
the field and the expected form. Non-blocking problems are recorded and the skill continues.
