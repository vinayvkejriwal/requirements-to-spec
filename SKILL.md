---
name: requirements-to-spec
description: Converts messy, informal product requirement requests into a structured, validated specification. Use when a user provides a vague feature request, stakeholder email, or requirements blurb and needs a clean spec with problem statement, affected users, testable acceptance criteria, edge cases, and open questions. Triggers on requests like "turn this into a spec", "write a PRD from this", "structure these requirements", or any unstructured feature ask.
license: MIT
metadata:
  author: vinay-kejriwal
  version: "1.0"
---

# Requirements-to-Spec

Turn an unstructured feature request into a complete, testable specification.

## What this does

A raw feature request is usually a messy paragraph: it mixes the goal with
side-asks, hides the success criteria, and leaves requirements implicit. This
skill forces every request through a fixed template, then runs a deterministic
validator that catches what the model misses.

The division of labor matters:

- **The model** reads the messy text and fills the template (fuzzy work).
- **The validator script** checks the filled spec for completeness and testable
  criteria (exact work — it is never wrong because it is just rules).

## Steps

1. Read the user's raw requirement text.
2. Load the template at `assets/spec_template.md`.
3. Fill every section of the template. Do not invent facts. If information is
   missing, write it as an explicit item under **Open Questions** rather than
   guessing.
4. For every item under **Acceptance Criteria**, write it so it is *testable*:
   it must describe an observable, checkable outcome (contains a number,
   threshold, true/false condition, or a clear pass/fail state). Avoid vague
   words like "fast", "easy", "good", "intuitive".
5. Save the filled spec to a file, then run the validator:
   `python scripts/validate.py <path-to-filled-spec.md>`
6. If the validator reports problems, fix them and re-run until it passes.

## Rules (gotchas)

- **Never guess a missing requirement.** A missing constraint goes under Open
  Questions. Silently inventing it is the most common failure and the validator
  is designed to catch the symptom (empty required sections).
- **Defaults, not menus.** Produce one filled spec, not three options for the
  user to choose between.
- **Untestable acceptance criteria fail.** "The page should load fast" is not a
  criterion. "The page should load in under 2 seconds" is.
- **Keep edge cases concrete.** Each edge case names a specific situation and
  the expected behavior.

## Output

The final output is the filled `spec_template.md` saved to disk, plus the
validator's PASS result printed to the console.
