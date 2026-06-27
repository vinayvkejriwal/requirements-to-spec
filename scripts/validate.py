#!/usr/bin/env python3
"""
validate.py - Deterministic checker for a filled requirements spec.

This script does the EXACT work the model is bad at: checking that every
required section is present and filled, and that acceptance criteria are
actually testable. It returns rule-based results, never model guesses.

Usage:
    python scripts/validate.py path/to/filled_spec.md

Exit code 0 = PASS, 1 = FAIL. Prints a per-check report either way.
"""

import re
import sys

REQUIRED_SECTIONS = [
    "Problem Statement",
    "Affected Users",
    "Acceptance Criteria",
    "Edge Cases",
    "Open Questions",
    "Compliance / Constraints Flags",
]

# Words that signal a vague, non-testable acceptance criterion.
VAGUE_WORDS = [
    "fast", "slow", "easy", "simple", "intuitive", "good", "nice",
    "user-friendly", "seamless", "robust", "scalable", "quickly",
    "efficient", "smooth", "clean", "modern",
]

# A criterion is considered testable if it contains at least one of these
# signals: a digit, a comparison word, or an explicit true/false condition.
TESTABLE_SIGNALS = re.compile(
    r"(\d|less than|more than|under|over|within|at least|at most|"
    r"equal|greater|fewer|maximum|minimum|must not|must |returns |"
    r"is true|is false|>=|<=|>|<|=|"
    r"persists|toggle|switches|displays|shows|enabled|disabled|"
    r"defaults to|follows|appears|redirects|rejects|accepts|"
    r"saved|stored|removed|added|after |when )",
    re.IGNORECASE,
)


def parse_sections(text):
    """Split markdown into {section_title: body_text} by ## headers."""
    sections = {}
    current = None
    buf = []
    for line in text.splitlines():
        m = re.match(r"^##\s+(.*)", line)
        if m:
            if current is not None:
                sections[current] = "\n".join(buf).strip()
            current = m.group(1).strip()
            buf = []
        else:
            buf.append(line)
    if current is not None:
        sections[current] = "\n".join(buf).strip()
    return sections


def strip_placeholders(body):
    """Remove template placeholder text and empty list markers.

    Placeholders are angle-bracket blocks that may span multiple lines, e.g.:
        <One or two sentences:
         continued here.>
    We drop everything from a line that starts with '<' until the line that
    ends with '>'. Also drops bare list markers ("1.", "-", "*") with no text.
    """
    cleaned = []
    in_placeholder = False
    for line in body.splitlines():
        s = line.strip()
        if not s:
            continue
        # entering a multi-line placeholder block
        if s.startswith("<"):
            if not s.endswith(">"):
                in_placeholder = True
            continue
        # inside a multi-line placeholder, skip until we hit the closing '>'
        if in_placeholder:
            if s.endswith(">"):
                in_placeholder = False
            continue
        # bare list markers with nothing after them: "1." or "-" or "2)"
        if re.fullmatch(r"(\d+[.)]|-|\*)", s):
            continue
        cleaned.append(s)
    return cleaned


def check_required_sections(sections):
    results = []
    for name in REQUIRED_SECTIONS:
        if name not in sections:
            results.append((f"Section present: {name}", False,
                            "section header missing"))
            continue
        content = strip_placeholders(sections[name])
        if not content:
            results.append((f"Section filled: {name}", False,
                            "section is empty or only placeholder text"))
        else:
            results.append((f"Section filled: {name}", True, ""))
    return results


def check_acceptance_testable(sections):
    results = []
    body = sections.get("Acceptance Criteria", "")
    items = strip_placeholders(body)
    if not items:
        results.append(("Acceptance criteria are testable", False,
                        "no acceptance criteria found"))
        return results

    for item in items:
        # strip leading list marker ("1.", "2)", "-", "*") so the list number
        # itself is not mistaken for a measurable signal
        stripped = re.sub(r"^\s*(\d+[.)]|-|\*)\s*", "", item)
        lower = stripped.lower()
        vague_hit = next((w for w in VAGUE_WORDS if w in lower), None)
        testable = bool(TESTABLE_SIGNALS.search(stripped))
        if vague_hit and not testable:
            results.append((f"Testable: '{item[:50]}...'", False,
                            f"vague word '{vague_hit}' with no measurable signal"))
        elif not testable:
            results.append((f"Testable: '{item[:50]}...'", False,
                            "no measurable signal (number/threshold/condition)"))
        else:
            results.append((f"Testable: '{item[:50]}...'", True, ""))
    return results


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/validate.py <filled_spec.md>")
        sys.exit(2)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        text = f.read()

    sections = parse_sections(text)
    results = []
    results += check_required_sections(sections)
    results += check_acceptance_testable(sections)

    passed = [r for r in results if r[1]]
    failed = [r for r in results if not r[1]]

    print("=" * 60)
    print("REQUIREMENTS-TO-SPEC VALIDATION REPORT")
    print("=" * 60)
    for name, ok, reason in results:
        mark = "PASS" if ok else "FAIL"
        line = f"[{mark}] {name}"
        if not ok and reason:
            line += f"  -> {reason}"
        print(line)
    print("-" * 60)
    print(f"{len(passed)} passed, {len(failed)} failed")
    print("=" * 60)

    sys.exit(0 if not failed else 1)


if __name__ == "__main__":
    main()