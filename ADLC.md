# ADLC Worksheet — requirements-to-spec

One page per phase. Fill the blanks marked [ ... ] during the build.

## 1. Scope
- **Problem:** Informal feature requests are incomplete and untestable, so
  builders start from ambiguity and rework later.
- **Who it's for:** Product managers, business analysts, anyone turning a
  stakeholder ask into a buildable spec.
- **Success looks like:** A bare local model that rambles on a messy request,
  once given this skill, produces a complete spec that passes validation.
- **Out of scope:** Estimation, ticket creation, design mocks.

## 2. Design
- **Division of labor:** Model fills the template (fuzzy extraction);
  `validate.py` checks completeness + testability (deterministic).
- **Why a script, not the model:** Small local models are unreliable at exact
  checks and burn tokens. Rules are correct every time.
- **Template-driven output:** `assets/spec_template.md` forces structure so the
  model cannot ramble.

## 3. Build
- Skill: `SKILL.md` + `assets/spec_template.md` + `scripts/validate.py`.
- Model used for the agent run: [ granite4:micro, local ]
- [ Note anything you changed from this scaffold here. ]

## 4. Evaluate
- 3 cases in `evals/evals.json`, each a messy request with planted gaps.
- Method: run each input WITH skill and WITHOUT skill (`--no-skill`), then
  `validate.py` on each output.
- **Result (fill in during build):**
  - No-skill pass rate: [ e.g. 0/3 ]
  - With-skill pass rate: [ e.g. 3/3 ]

## 5. Deploy
- Distributed as a public GitHub repo with README + MIT license.
- Install: clone, then point any agentskills.io-compatible client at the folder.

## 6. Observe
- The validator's PASS/FAIL report is the observability surface: it names every
  failed check and why.
- [ Note any failure you saw during testing and what it revealed. ]

## 7. Iterate
- [ One concrete improvement you'd make next, e.g. "add a routing step that
  escalates the compliance-flag reasoning to Claude when the request touches
  user data." ]

## Model-Selection Rationale
- **Local (granite4:micro):** extraction and template-filling — high-volume,
  privacy-sensitive (requirement docs shouldn't leave the laptop), well-scoped.
- **Frontier (Claude, via $50 credit) — optional escalation:** only the
  ambiguous compliance-reasoning field, where quality beats cost.
- **Rationale:** cheap-and-local for the easy/private bulk; spend frontier
  tokens only on the genuinely hard call. Cost/latency logged if routing built.
