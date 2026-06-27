# ADLC Worksheet — requirements-to-spec

The Agent Development Life Cycle, one page per phase, completed during the build.

## 1. Scope
- **Problem:** Completeness and testability gaps in requirements go undetected
  until they surface as rework mid-build. Senior analysts catch these by
  experience; that judgment is neither explicit nor repeatable.
- **Who it's for:** Product managers, business analysts, anyone turning a
  stakeholder ask into a buildable spec.
- **Success looks like:** A bare local model that rambles on a messy request,
  once given this skill, produces a complete spec whose acceptance criteria are
  testable — and the system catches the criteria that are not.
- **Out of scope:** Estimation, ticket creation, design mocks.

## 2. Design
- **Division of labor:** The model fills the template (fuzzy extraction);
  `validate.py` checks completeness and testability (deterministic). The model
  is good but imperfect; the script catches what it misses.
- **Why a script, not the model:** Small local models are unreliable at exact
  checks and burn tokens doing them. Rules are correct every time.
- **Template-driven output:** `assets/spec_template.md` forces structure so the
  model cannot ramble.
- **Self-correcting loop:** On a validation failure, the failed checks are fed
  back to the model to rewrite only the flagged criteria, capped at 2 retries.
  If it still fails, the system flags the items for human review rather than
  faking a pass.

## 3. Build
- Skill: `SKILL.md` + `assets/spec_template.md` + `scripts/validate.py`.
- Agent: `agent.py` on `agentkit`, model `granite4:micro` (local, via Ollama).
- Added a self-correcting validation loop to the skill path: generate -> validate
  -> on FAIL, feed the failed-check report back to the model to revise only the
  flagged criteria -> re-validate, up to 2 retries, then honest failure.
- `--no-skill` flag runs the same requirement with no skill and no template, as
  the before/after baseline.

## 4. Evaluate
- 3 cases in `evals/evals.json` (dark mode, data export, notifications), each a
  messy request with planted gaps (a missing metric, an unquantified word, an
  unstated compliance constraint).
- Method: run each input with the skill and without it (`--no-skill`), then run
  `validate.py` on each output.
- **Results:**
  - Without skill: unstructured output, fails all 6 required-section checks.
  - With skill: complete 6-section specs; validation passing 9/9 to 11/13
    checks depending on case, with the validator surfacing the exact soft
    criteria a human would wave through.
  - Cost $0.00, ~18s per spec, fully local.
- The skill demonstrably raises the structural pass rate over the no-skill
  baseline on every case.

## 5. Deploy
- Distributed as a public GitHub repo with README + MIT license.
- Validates against the spec with `agentskills validate ./requirements-to-spec`.
- Install: clone, then point any agentskills.io-compatible client at the folder.

## 6. Observe
- The validator's PASS/FAIL report is the observability surface: it names every
  failed check and the reason.
- Two validator defects surfaced during testing (an evaluate -> observe ->
  iterate loop, not inspection):
  1. Empty multi-line placeholder sections falsely passed. Cause: the
     placeholder stripper only removed single-line angle-bracket blocks. Fixed
     by stripping multi-line angle-bracket blocks.
  2. Criteria with the measurable signal in a sub-bullet (e.g. "200 ms" under a
     bold header) were falsely failed. Cause: each line was treated as a
     separate criterion. Fixed by grouping each numbered criterion with its
     sub-bullets before the testability check.
- Both fixes were re-verified against the full set of test specs (empty fails,
  bad fails, good passes) before shipping.

## 7. Iterate
- **Known limitation:** Genuinely qualitative criteria ("switches correctly",
  "displays correctly") cannot be made testable by the local model on retry;
  there is no number to inject. The loop flags these for human review rather
  than faking a pass — the safe failure direction for a requirements checker.
- **Next step:** Add testable-criterion examples to `SKILL.md` so the model
  writes measurable criteria on the first pass, reducing flagged items. Small
  models follow examples far better than instructions.

## Model-Selection Rationale
- **Local (granite4:micro):** all extraction and revision — high-volume,
  privacy-sensitive (requirement docs never leave the device), well-scoped.
  Measured at $0.00 cost and ~18s latency per spec across the test cases.
- **Frontier (Claude) — optional escalation:** reserved for genuinely ambiguous
  reasoning if needed; not required for this task.
- **Rationale:** cheap-and-local for the easy, high-volume, private bulk; spend
  frontier tokens only on the genuinely hard call. Local-first by design.