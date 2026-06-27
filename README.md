# requirements-to-spec

An agent skill that turns a messy, informal feature request into a complete,
**validated** specification — problem statement, affected users, testable
acceptance criteria, edge cases, open questions, and compliance flags.

Built for the Open Accelerator Agent Build Day (Lane 1), June 27, 2026.

## The idea in one line

The **model** does the fuzzy work (reading messy text, filling a template).
A **deterministic script** does the exact work (checking nothing is missing and
every acceptance criterion is testable). The model is good but imperfect; the
script catches what it misses — so the output is gradable, not just impressive.

## Before / after

Same local model (`granite4:micro`), same input. The only difference is the skill.

| | Without skill | With skill |
|---|---|---|
| **Output** | A few vague restatements of the request | A complete 6-section spec |
| **"make it look good"** | left as-is, untestable | becomes WCAG AA contrast (4.5:1), a 500 ms transition target |
| **Missing constraints** | silently dropped | surfaced under Open Questions (no guessing) |
| **Accessibility / PII** | not mentioned | flagged under Compliance / Constraints |
| **Structural checks** | fails all 6 required sections | passes all 6 |
| **Cost / latency** | — | $0.00, ~18s, fully local |

Across three test cases (dark mode, data export, notifications), the no-skill
baseline fails every structural check; the skilled agent produces a complete
spec each time and the validator surfaces the exact soft criteria a human would
wave through.

## Self-correcting loop

When the validator flags a non-testable criterion, the agent feeds the failed
checks back to the model to rewrite only those criteria, then re-validates —
up to 2 retries. If a criterion is genuinely qualitative and cannot be made
measurable, the loop flags it for human review rather than faking a pass. A
validator you can always satisfy is not checking anything.

## Structure

```
requirements-to-spec/
├── SKILL.md                  # metadata + instructions (spec-conformant)
├── agent.py                  # the agent: fill -> validate -> self-correct
├── assets/spec_template.md   # the fill-in-the-blanks output form
├── scripts/validate.py       # deterministic completeness + testability check
├── evals/evals.json          # 3 before/after test cases with planted gaps
├── ADLC.md                   # Agent Development Life Cycle worksheet
└── references/               # (room for deeper docs)
```

## Run it

```bash
# with the skill (fills, validates, self-corrects)
python agent.py "add dark mode to the app, should be easy, make it look good"

# baseline: no skill, no template, structure not enforced
python agent.py --no-skill "add dark mode to the app, should be easy, make it look good"
```

## Validate the skill against the spec

```bash
agentskills validate ./requirements-to-spec
```

## Run the validator directly

```bash
python scripts/validate.py path/to/filled_spec.md
# exit 0 = PASS, exit 1 = FAIL, with a per-check report
```

## Model selection

Local `granite4:micro` (via Ollama) handles all extraction and revision:
high-volume, privacy-sensitive (requirement docs never leave the device),
well-scoped. Measured at $0.00 cost and ~18s latency per spec. Frontier
escalation is reserved for genuinely ambiguous reasoning if needed; it is not
required for this task. See `ADLC.md` for the full rationale.

## License

MIT