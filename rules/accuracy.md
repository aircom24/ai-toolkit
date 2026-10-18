---
name: accuracy
description: Factual accuracy and source traceability for any generated content.
version: 0.1.0
---

# Accuracy

## Purpose

Keep generated content verifiable. A reader must be able to tell which statements come from the
input and which are inferences.

## Rules

- State only facts that are supported by the provided input or by a named, verifiable source.
- Mark every inference as an inference, for example "Inferred from: <source>".
- Do not fill gaps with plausible-sounding values. Write the gap as unknown.
- Copy names, numbers, dates and identifiers exactly as given. Do not round or reformat them.
- Recheck calculations, unit conversions and comparisons before reporting them.
- When sources disagree, report the disagreement instead of picking one silently.

## Why

Unsupported statements are hard to detect after the fact. One invented value can undermine trust
in the whole output.

## How to apply

Apply the rule while writing, not only in a final review. Skills reference it in the step where
facts are collected or stated.
