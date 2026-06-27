# requirements-to-spec

An agent skill that turns a messy, informal feature request into a complete,
**validated** specification — problem statement, affected users, testable
acceptance criteria, edge cases, open questions, and compliance flags.

Built for the Open Accelerator Agent Build Day (Lane 1), June 27, 2026.

## The idea in one line

The **model** does the fuzzy work (reading messy text, filling a template).
A **deterministic script** does the exact work (checking nothing is missing and
every acceptance criterion is testable). Together they beat the model alone.

## Before / after

Same local model, same input. The only difference is the skill.

| Input | Without skill | With skill |
|---|---|---|
| "add dark mode, should be easy, make it look good" | rambling paragraph, no success metric, no accessibility flag | 6-section spec, "looks good" → testable criteria, accessibility flagged under Open Questions |

Pass rate on the eval set: **without skill 0/3 → with skill 3/3.**

## Structure

```
requirements-to-spec/
├── SKILL.md                  # metadata + instructions (spec-conformant)
├── assets/spec_template.md   # the fill-in-the-blanks output form
├── scripts/validate.py       # deterministic completeness + testability check
├── evals/evals.json          # 3 before/after test cases with planted gaps
├── ADLC.md                   # Agent Development Life Cycle worksheet
└── references/               # (room for deeper docs)
```

## Run the validator

```bash
python scripts/validate.py path/to/filled_spec.md
# exit 0 = PASS, exit 1 = FAIL, with a per-check report
```

## Validate the skill itself

```bash
skills-ref validate ./requirements-to-spec
```

## Model selection

Local `granite4:micro` handles extraction and template-filling (high-volume,
privacy-sensitive, well-scoped). Optional escalation to Claude for the
ambiguous compliance-reasoning field only. See `ADLC.md` for the full rationale.

## License

MIT
