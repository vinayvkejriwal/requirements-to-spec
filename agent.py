"""requirements-to-spec — turn a messy ask into a validated spec.

The agent reads the spec template through a tool, then the loaded skill makes
the local model fill every section. The harness saves the result and runs the
deterministic validator (scripts/validate.py) over it — the model does the
fuzzy work, the script does the exact work.

The ``--no-skill`` flag is the before/after baseline: same requirement, no
skill and no template, structure NOT enforced. Diff the two outputs to see
what the skill buys you.
"""

import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _agentkit_root() -> Path:
    """Locate the dir holding ``agentkit`` so ``python agent.py`` works anywhere.

    This skill lives alongside AgentDay-Example rather than inside it, so we
    check each parent AND each parent's children (where AgentDay-Example sits).
    """
    for p in [HERE, *HERE.parents]:
        if (p / "agentkit").is_dir():
            return p
        try:
            for child in p.iterdir():
                if child.is_dir() and (child / "agentkit").is_dir():
                    return child
        except (PermissionError, OSError):
            pass
    raise RuntimeError("could not find agentkit on any parent path")


sys.path.insert(0, str(_agentkit_root()))

from agentkit import run_agent, tool  # noqa: E402

DEFAULT_SKILL = HERE  # the SKILL.md for this skill lives in this directory
TEMPLATE = HERE / "assets" / "spec_template.md"
VALIDATOR = HERE / "scripts" / "validate.py"
OUTPUT_DIR = HERE / "output"

SYSTEM = (
    "You are Requirements-to-Spec, an agent that turns a messy product "
    "requirement into ONE structured, testable specification. "
    "Always read the spec template with your tool before writing anything, "
    "then fill EVERY section using its exact '## ' headers. "
    "Output only the completed specification markdown — the filled template "
    "and nothing else: no preamble, no commentary, no code fences."
)


@tool
def read_spec_template():
    """Read the spec template that must be filled in. Always read this before writing the spec, and reproduce every '## ' section header it contains."""
    return TEMPLATE.read_text(encoding="utf-8")


def _spec_instructions(requirement: str) -> str:
    return (
        "Convert this raw product requirement into a spec:\n\n"
        f'"""\n{requirement}\n"""\n\n'
        "Read the spec template, then fill in every section based ONLY on the "
        "requirement above. Make each acceptance criterion testable — include a "
        "number, threshold, or clear pass/fail condition, and avoid vague words "
        "like 'fast', 'easy', or 'good'. Anything the requirement does not "
        "specify goes under Open Questions; do not guess it. "
        "Return only the filled-in template markdown."
    )


def run(requirement: str):
    """Skill path: load the skill + template tool, return the filled spec."""
    return run_agent(
        _spec_instructions(requirement),
        tools=[read_spec_template],
        skill=DEFAULT_SKILL,
        system=SYSTEM,
    )


def run_baseline(requirement: str):
    """No-skill baseline: same ask, no skill, no template, no structure enforced."""
    task = (
        "Turn this product requirement into a specification:\n\n"
        f'"""\n{requirement}\n"""'
    )
    return run_agent(task, skill=None)


def _stats(r):
    return (
        f"\n[{r.turns} turns · {r.usage['prompt_tokens']}+{r.usage['completion_tokens']} tok"
        f" · ${r.cost_usd} · {r.latency_s}s · tools: {[c[0] for c in r.tool_calls]}]"
    )


def _run_validator(spec_path):
    """Run scripts/validate.py over a spec. Returns (returncode, stdout, stderr)."""
    res = subprocess.run(
        [sys.executable, str(VALIDATOR), str(spec_path)], capture_output=True, text=True
    )
    return res.returncode, res.stdout, res.stderr


def _fail_lines(report):
    """Pull the validator's '[FAIL] ...' lines out of its stdout report."""
    return [ln.rstrip() for ln in report.splitlines() if ln.lstrip().startswith("[FAIL]")]


REVISE_SYSTEM = (
    "You are Requirements-to-Spec, repairing a specification that failed "
    "automated validation. You are given the full current spec and the "
    "validator's failed checks. Rewrite ONLY the flagged acceptance criteria so "
    "each contains a measurable signal: a number, threshold, count, time limit, "
    "or an explicit pass/fail / true-false condition (e.g. 'within 1 click', "
    "'in under 2 seconds', 'toggle persists across restarts', 'must not exceed', "
    "'displays X'). Never use vague words like 'fast', 'easy', 'good', "
    "'intuitive', or 'seamless'. Leave every other section and every line that "
    "already passed EXACTLY as-is, keeping the same '## ' headers. Output only "
    "the full revised specification markdown — no preamble, no commentary, no "
    "code fences."
)


def revise(spec_text, fail_lines):
    """One self-correction pass: reuse run_agent to rewrite only the flagged criteria."""
    task = (
        "This specification FAILED validation.\n\n"
        "=== FAILED CHECKS (rewrite only what these flag) ===\n"
        + "\n".join(fail_lines)
        + "\n\n=== CURRENT SPECIFICATION ===\n"
        + spec_text
        + "\n\nRewrite ONLY the flagged criteria so each has a measurable signal. "
        "Keep every other section and passing line identical. Return the full "
        "revised spec markdown."
    )
    return run_agent(task, system=REVISE_SYSTEM)


def correct_until_valid(out, max_retries=2):
    """Validate the saved spec; on failure, feed the failed checks back to the
    model and rewrite only the flagged criteria, re-validating after each pass.

    Caps at ``max_retries`` revisions (initial + 2 = 3 attempts max). Prints
    each attempt's verdict so the loop is visible. Returns
    ``(returncode, remaining_fail_lines, attempts)``.
    """
    print("\n" + "=" * 60)
    print(f"Validating {out.relative_to(HERE)} ...")
    print("=" * 60)
    rc, report, err = _run_validator(out)
    print(report, end="")
    if err:
        print(err, end="", file=sys.stderr)
    fails = _fail_lines(report)
    attempt = 1
    print(f"\nAttempt {attempt}: " + ("PASS" if rc == 0 else f"FAIL ({len(fails)} issue{'' if len(fails) == 1 else 's'})"))

    while rc != 0 and attempt <= max_retries:
        attempt += 1
        print("\n" + "-" * 60)
        print(f"Revision {attempt - 1}: feeding {len(fails)} failed check(s) back to the model ...")
        for ln in fails:
            print("  " + ln)
        print("-" * 60)
        rr = revise(out.read_text(encoding="utf-8"), fails)
        out.write_text(rr.text, encoding="utf-8")
        print(_stats(rr), file=sys.stderr)
        rc, report, err = _run_validator(out)
        if err:
            print(err, end="", file=sys.stderr)
        fails = _fail_lines(report)
        print(f"Attempt {attempt}: " + ("PASS" if rc == 0 else f"FAIL ({len(fails)} issue{'' if len(fails) == 1 else 's'})"))

    return rc, fails, attempt


def main():
    ap = argparse.ArgumentParser(description="requirements-to-spec — messy ask -> validated spec")
    ap.add_argument("requirement", help='e.g. "add dark mode to the app, should be easy, make it look good"')
    ap.add_argument("--no-skill", action="store_true", help="baseline: no skill, no template, structure not enforced")
    args = ap.parse_args()

    OUTPUT_DIR.mkdir(exist_ok=True)

    if args.no_skill:
        r = run_baseline(args.requirement)
        out = OUTPUT_DIR / "spec_noskill.md"
        out.write_text(r.text, encoding="utf-8")
        print(r.text)
        print(_stats(r), file=sys.stderr)
        print(f"\n[baseline saved -> {out.relative_to(HERE)} · structure NOT enforced]", file=sys.stderr)
        return

    out = OUTPUT_DIR / "spec.md"

    # Attempt 1 — generate the spec from the raw requirement.
    r = run(args.requirement)
    out.write_text(r.text, encoding="utf-8")
    print(r.text)
    print(_stats(r), file=sys.stderr)
    print(f"\n[spec saved -> {out.relative_to(HERE)}]", file=sys.stderr)

    # Validate, and self-correct up to 2 revisions if the validator fails.
    rc, fails, attempt = correct_until_valid(out, max_retries=2)

    if attempt > 1:
        print("\n" + "=" * 60)
        print(f"Final spec ({out.relative_to(HERE)}):")
        print("=" * 60)
        print(out.read_text(encoding="utf-8"))

    print("\n" + "=" * 60)
    if rc == 0:
        print("VERDICT: PASS ✅")
    else:
        n = len(fails)
        print(f"VERDICT: FAIL ❌ — {n} issue{'' if n == 1 else 's'} remain{'s' if n == 1 else ''}, flagged for human review")
        for ln in fails:
            print("  " + ln)
    print(f"[done · {attempt} attempt{'' if attempt == 1 else 's'} · final spec at {out.relative_to(HERE)}]", file=sys.stderr)


if __name__ == "__main__":
    main()
